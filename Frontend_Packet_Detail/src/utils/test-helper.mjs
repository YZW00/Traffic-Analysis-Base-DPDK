import listData from '@/test/packet-list-large.json'
import detailData from '@/test/packet-detail.json'

import { sleep } from '@/utils/util.mjs'

import { isRef } from 'vue'

export async function initDissector() {
    await sleep(1000)
    return 'test'
}

export async function loadFile(session, file, state=null) {
    if (isRef(state)) {
        for(let i=0;i<=120;i+=Math.round(Math.random()*20)) {
            if (i > 100) i = 100
            // await sleep(800)
            state.value = i
            if (i == 100) break
        }
    }
    return listData.length
}

export async function getFrames(session, filter, skip, limit, state=null) {
    if (isRef(state)) {
        for(let i=0;i<=120;i+=Math.round(Math.random()*20)) {
            if (i > 100) i = 100
            await sleep(400)
            state.value = i
            if (i == 100) break
        }
    }
    const start = Math.min(listData.length - 1, skip)
    const length = Math.min(listData.length - start, limit)
    return listData.slice(start, start + length)
}

export async function parseFrame(session, id) {
    await sleep(10)
    return detailData
}

export function parseDetailTree(data, layer=[]) {
    return data.map(({l:label, n:children, h:hex}, index) => ({
        key: layer.concat([index]).join('-'),
        label,
        hex,
        children: children ? parseDetailTree(children, layer.concat([index])) : null
    }))
}

export async function checkFilter(session, filter) {
    return true
}
