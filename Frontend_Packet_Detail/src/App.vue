<template>
    <Toast />
    <PacketLoad :value="value" :visible="visible || outsideFinish" :text="text"></PacketLoad>
    <PacketFilter v-model:value="filter" @setFilter="setFilter" @stopCapture="doStopCapture" :realTime="realTime" :config="CONFIG"/>
    <DetailPanel>
        <template #packet-list>
            <PacketList ref="packetList" :data="frameList" @row-click="listClick"/>
        </template>
        <template #packet-detail>
            <PacketDetail :data="detailTree" v-model:selected-key="selected" v-model:unfolded-key="unfolded"/>
        </template>
        <template #packet-hex>
            <PacketHex :bytes="detailBytes" :tree="detailTree" @click-space="spaceClick"/>
        </template>
    </DetailPanel>
    <PacketStatus :total="totalFrames" :loaded="loadedFrames" :forceFinish="forceFinish" :realTime="realTime"/>
</template>

<script setup>
import { ref, shallowRef, watch, onMounted } from 'vue'
import { initDissector, loadFile, checkFilter, getFrames, parseDetailTree, parseFrame, closeSession, getConfig } from '@/utils/sharkd-helper.mjs'
import { sleep } from '@/utils/util.mjs'

import DetailPanel from '@/components/DetailPanel.vue'
import PacketList from '@/components/PacketList.vue'
import PacketDetail from '@/components/PacketDetail.vue'
import PacketHex from '@/components/PacketHex.vue'
import PacketLoad from '@/components/PacketLoad.vue'
import PacketStatus from '@/components/PacketStatus.vue'
import PacketFilter from '@/components/PacketFilter.vue'

import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const filter = ref('')
const packetList = ref(null)
let scrollTarget = 0
let realFilter = ''
const realTime = ref(true)
const frameList = shallowRef([])
const detailTree = shallowRef([])
const detailBytes = ref('')

const totalFrames = ref(-1)
const loadedFrames = ref(-1)
const forceFinish = ref(false)


const outsideFinish = ref(false)
const visible = ref(false)
const value = ref(0)
const text = ref('')

let CONFIG = ref({})

watch(value, (newValue) => {
    if (value.value > -1) {
        const textDot = text.value.replace(/(?:\(\d+%\))?\.\.\.$/, '')
        text.value = `${textDot}(${newValue}%)...`
    }
})
function updateState(newText, newVal=-1) {
    text.value = newText
    value.value = newVal
}

const toast = useToast()
function cacheToast(error) {
    console.error(error)
    updateState('加载异常, 请检查服务器设置', -1)
    toast.add({
        severity: 'error', summary: error.name, detail: error.message, life: 3000
    })
}

function getRealNum(num) {
    let i = 0
    while (num > loadedFiles[i].end) {
        i += 1
    }
    return [loadedFiles[i], num - loadedFiles[i].start + 1]
}

const MAX_FILE = 2
let waiter = null
const PID_Ctrl = {
    P: 0.01, I: 0.1, D: 0,
    E_n: 0, E_n1: 0, E_n2: 0, E_leak: 0,
    out: 256
}
async function loadAppend(uuid) {
    const listData = await getFrames(uuid, realFilter)
    const listEnd = listData.length ? listData.at(-1).num : 0
    let removeLength = 0
    while (loadedFiles.length >= (CONFIG.value?.maxFileNum ?? MAX_FILE)) { // 移除最老的file
        const removed = loadedFiles.shift()
        removeLength += removed.length
        if (CONFIG.value?.sendCloseRequest) {
            if (!loadedFiles.filter(e => e.uuid == removed.uuid)) {
                closeSession(e.uuid) // no await
            }
        }
    }
    const oldFrameList = frameList.value.slice(removeLength)
    let shift
    if (!loadedFiles.length) { // 计算偏移量
        shift = 0
    } else {
        if (loadedFiles.at(-1).end + listEnd > 0xffffffff) {
            shift = 0
        } else {
            shift = loadedFiles.at(-1).end
        }
    }
    for (const item of listData) { // 追加偏移量
        item.num += shift
        // item.c[0] = item.c[0] | 0 + shift
    }
    frameList.value = oldFrameList.concat(listData)
    loadedFiles.push({
        uuid, start: shift + 1, end: shift + listEnd, length: listData.length
    })
    if (!CONFIG.value?.autoScrollStep) { // Update state
        if (CONFIG.value?.pid) {
            [PID_Ctrl.P, PID_Ctrl.I, PID_Ctrl.D] = CONFIG.value.pid
        }
        PID_Ctrl.E_n = frameList.value.length - listData.length - scrollTarget - PID_Ctrl.E_leak
        let out = (PID_Ctrl.P * PID_Ctrl.E_n) - (PID_Ctrl.I * PID_Ctrl.E_n1) + (PID_Ctrl.I * PID_Ctrl.E_n2)
        PID_Ctrl.E_n2 = PID_Ctrl.E_n1
        PID_Ctrl.E_n1 = PID_Ctrl.E_n
        PID_Ctrl.E_leak = 0
        if (out > 1048576) out = 1048576
        if(out < 0) out = 0
        PID_Ctrl.out = out
    }
    scrollTarget -= removeLength
    if (scrollTarget < 0) scrollTarget = 0
    loadedFrames.value = frameList.value.length
    totalFrames.value += listData.length
    if (waiter) {
        waiter()
        waiter = null
    }
}

async function autoScroll() {
    function waitLoad() {
        return new Promise((resolve, reject) => {
            waiter = resolve
        })
    }
    while (!CONFIG.value?.disableAutoScroll && realTime.value) {
        packetList.value.scorllToItem(scrollTarget)
        scrollTarget += CONFIG.value?.autoScrollStep ?? PID_Ctrl.out
        if (scrollTarget > frameList.value.length) {
            PID_Ctrl.E_leak += scrollTarget - frameList.value.length
            scrollTarget = frameList.value.length
            await waitLoad()
        }
        if (!CONFIG.value?.autoScrollStep) { // Update state
            if (CONFIG.value?.pid) {
                [PID_Ctrl.P, PID_Ctrl.I, PID_Ctrl.D] = CONFIG.value.pid
            }
            PID_Ctrl.E_n = frameList.value.length - scrollTarget - PID_Ctrl.E_leak
            let out = (PID_Ctrl.P * PID_Ctrl.E_n) - (PID_Ctrl.I * PID_Ctrl.E_n1) + (PID_Ctrl.I * PID_Ctrl.E_n2)
            PID_Ctrl.E_n2 = PID_Ctrl.E_n1
            PID_Ctrl.E_n1 = PID_Ctrl.E_n
            PID_Ctrl.E_leak = 0
            if (out > 1048576) out = 1048576
            if(out < 0) out = 0
            PID_Ctrl.out = out
            console.log(PID_Ctrl)
        }
        await sleep(CONFIG.value?.autoScrollDelay ?? 200)
    }
}

let loadedFiles =  []
let testAutoLoad
async function loadFrames(filter='') {
    const uuid = await initDissector()
    forceFinish.value = false
    updateState('加载pcap文件...')
    const params = new URLSearchParams(document.location.search)
    let file
    if(params.get('realTime')){
        file = '/home/【User】/etadp_backend/pcaps/output-20241122-162502_01_000.pcap'
    }else{
        file = params.get('file')
        stopCapture()
    }
    const timer = setTimeout(()=> {
        forceFinish.value = true
        visible.value = false
        toast.add({
            severity: 'error', summary: "文件加载异常", detail: "指定的文件不完整或无效", life: 3000
        })
    }, 120 * 1000)
    totalFrames.value = await loadFile(uuid, file, value)
    clearTimeout(timer)
    updateState('加载首屏数据...')
    const listData = await getFrames(uuid, filter)
    loadedFrames.value = listData.length
    frameList.value = listData
    loadedFiles = []
    loadedFiles.push({
        uuid, start: 1, end: listData.length, length: listData.length
    })
    // testAutoLoad = setInterval(() => {
    //     loadAppend(uuid).catch(cacheToast)
    // }, 10000)
    autoScroll().catch(cacheToast)
}

try {
    const ws = new WebSocket(`ws://${document.location.hostname}:21346`)
    ws.addEventListener("message", (ev) => {
        const message = JSON.parse(ev.data)
        switch (message.type) {
            case "stop":
                stopCapture()
                break
        }
    })
} catch(e) {
    console.error(e)
}

onMounted(() => {
    const task = async () => {
        visible.value = true
        updateState('加载系统配置...')
        try {
            CONFIG.value = await getConfig()
        } catch (error) {
            console.error(error)
        }
        updateState('初始化系统...')
        await loadFrames('')
        visible.value = false
        window.dispatchEvent(new Event('resize'))
    }
    task().catch(cacheToast)
})

const unfolded = ref([])
const selected = ref(null)

/* Event handler */
function setFilter(filter) { // TODO
    const task = async () => {
        visible.value = true
        updateState('设置过滤条件...')
        try {
            await checkFilter(loadedFiles.at(-1).uuid, filter)
            realFilter = filter
        } catch {
            toast.add({
                severity: 'error', summary: '表达式错误', detail: '输入的过滤表达式错误或无效', life: 3000
            })
            visible.value = false
            return
        }
        if (CONFIG.value?.filterOldFileInRealTime || !realTime.value) {
            frameList.value = []
            totalFrames.value = 0
            loadedFrames.value = 0
            const cacheFiles = loadedFiles
            loadedFiles = []
            scrollTarget = 0
            for (const file of cacheFiles) {
                await loadAppend(file.uuid)
            }
        }
        visible.value = false
        window.dispatchEvent(new Event('resize'))
    }
    task().catch(cacheToast)
}
function listClick(item) {
    const [file, realNum] = getRealNum(item.data.num)
    parseFrame(file.uuid, realNum).then(({tree, bytes}) => {
        unfolded.value = []
        selected.value = null
        detailTree.value = parseDetailTree(tree)
        detailBytes.value = bytes
    }).catch(cacheToast)
}
function spaceClick(item) {
    if (!item.key) return
    selected.value = item.key
    const keyArr = []
    const addedkey = []
    for (const key of item.key.split('-')) {
        keyArr.push(key)
        const realKey = keyArr.join('-')
        if (!unfolded.value.includes(realKey)) {
            addedkey.push(realKey)
        }
    }
    unfolded.value = unfolded.value.concat(addedkey)
}

function doStopCapture() {
    fetch("http://【Your_ip_addr_main】/nmas/traffic_collect/stop_capture/")
    stopCapture()
}

function stopCapture() {
    realTime.value = false
    totalFrames.value = loadedFrames.value
    forceFinish.value = true
    if (testAutoLoad) {
        clearInterval(testAutoLoad)
        testAutoLoad = null
    }
}

globalThis.loadState = function(showText, showValue, show) {
    text.value = showText
    value.value = showValue
    outsideFinish.value = show
}
</script>
