<template>
    <div class="hexviewer-container flex">
        <div class="bg-gray-200 text-bluegray-700 px-2 select-none">{{ getHexOffset(bytesArray.length) }}</div>
        <div class="px-3">
            <template v-for="info in segments">
                <span @mouseenter="spaceEnter(info)"
                      @mouseleave="spaceLeave(info)"
                      @click="spaceClick(info)"
                      :class="{
                        'hexviewer-hover': hoverKey && info.key == hoverKey
                      }">{{ getHexString(info.bytes, info.start) }}</span>
                <a>{{ info.end %  8 ? " " : info.end % 16 ? "　" : "\n" }}</a>
            </template>
        </div>
        <div class="hexviewer-ascii">
            <template v-for="info in segments">
                <span @mouseenter="spaceEnter(info)"
                      @mouseleave="spaceLeave(info)"
                      @click="spaceClick(info)"
                      :class="{
                        'hexviewer-hover': hoverKey && info.key == hoverKey
                      }">{{ getASCIIString(info.bytes, info.start) }}</span>
                <a v-if="info.end % 16 === 0">{{ "\n" }}</a>
            </template>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { base64DecToArr } from '@/utils/base64.mjs'

const props = defineProps({
    bytes: String,
    tree: Array
})
const emits = defineEmits(['clickSpace'])

const hoverKey = ref(null)

const bytesArray = computed(() => base64DecToArr(props.bytes))
const segments = computed(() => getSpace(props.tree).map(({ start, end, key }) => ({
    bytes: bytesArray.value.slice(start, end), start, end, key
})))

/* event handler */
function spaceEnter(item) {
    hoverKey.value = item.key
}
function spaceLeave(item) {
    if (hoverKey.value == item.key) {
        hoverKey.value = null
    }
}
function spaceClick(item) {
    emits('clickSpace', item)
}

function getSpace(tree) {
    let space = []
    for (const item of tree) {
        const lastSpace = space.at(-1)
        if (!item.children && item.hex) {
            let [start, length] = item.hex
            const end = start + length
            if (lastSpace) {
                if (lastSpace.start >= start) {
                    continue
                }
                if (lastSpace.end < start) {
                    space.push({
                        start: lastSpace.end,
                        end: start,
                        key: null
                    })
                } else if (lastSpace.end > start) {
                    continue
                }
            }
            if (length && start < end) {
                space.push({ start, end, key: item.key })
            }
        }
        if (item.children) {
            let childSpace = getSpace(item.children)
            if (lastSpace) {
                childSpace = childSpace.filter(e => e.start >= lastSpace.end)
                if (childSpace[0] && childSpace[0].start > lastSpace.end) {
                    space.push({
                        start: lastSpace.end,
                        end: childSpace[0].start,
                        key: item.key
                    })
                }
            }
            space = space.concat(childSpace)
        }
    }
    return space
}

function getHexOffset(len, pad=4) {
    const totalLineCount = (len + 15) >> 4
    const output = []
    for (let line = 0; line < totalLineCount; line++) {
        output.push((line*16).toString(16).padStart(pad, "0"))
    }
    return output.join("\n")
}

function getASCIIString(hexList, skip=0) {
    skip = skip % 16
    const totalLineCount = (hexList.length + skip + 15) >> 4
    let totalOutputCount = hexList.length // 字符数
    totalOutputCount += totalLineCount? totalLineCount - 1 : 0 // 行间换行
    const output = new Uint8Array(totalOutputCount)
    let pointer = 0
    let hex_num = skip
    for (let hex_i = 0; hex_i < hexList.length; hex_i++) {
        output[pointer] = (hexList[hex_i] > 0x1F && hexList[hex_i] < 0x7F) ? hexList[hex_i] : 0x2E
        pointer += 1
        if (hex_i === hexList.length - 1) {
            break
        }
        if (hex_num % 16 === 15) {
            output[pointer] = 0x0A
            pointer += 1
        }
        hex_num += 1
    }
    const decoder = new TextDecoder()
    return decoder.decode(output)
}

function getHexString(hexList, skip=0) {
    skip = skip % 16
    const totalLineCount = (hexList.length + skip + 15) >> 4
    const realLineCount = (hexList.length >> 4)
    const residual = hexList.length % 16
    let totalOutputCount = hexList.length * 2 // 字符数
    totalOutputCount += realLineCount * ((8 - 1) * 2 + 3) // 行内空格
    totalOutputCount += totalLineCount? totalLineCount - 1 : 0 // 行间换行
    totalOutputCount += residual ? residual - 1 : 0 // 剩余空格
    if (residual + skip > 8) { // 剩余大间隔
        totalOutputCount += 3 - 1
    }
    const output = new Uint8Array(totalOutputCount)
    let pointer = 0
    let hex_num = skip
    for (let hex_i = 0; hex_i < hexList.length; hex_i++) {
        const toASCII = num => num > 0x09 ? num + 0x61 - 10 : num + 0x30
        output[pointer+0] = toASCII(hexList[hex_i] >> 4)
        output[pointer+1] = toASCII(hexList[hex_i] & 0x0F)
        pointer += 2
        if (hex_i === hexList.length - 1) {
            break
        }
        if (hex_num % 16 === 15) {
            output[pointer+0] = 0x0A
            pointer += 1
        } else {
            if (hex_num % 8 === 7) {
                output[pointer+0] = 0xE3
                output[pointer+1] = 0x80
                output[pointer+2] = 0x80
                pointer += 3
            } else {
                output[pointer+0] = 0x20
                pointer += 1
            }
        }
        hex_num += 1
    }
    let clipLength = 0
    for (let i = output.length - 1; i >= 0; i--) {
        if (output[i]) {
            clipLength = i + 1
            break
        }
    }
    const decoder = new TextDecoder()
    return decoder.decode(output.slice(0, clipLength))
}
</script>

<style scoped>
.hexviewer-container {
    font-family: var(--font-family);
    line-height: 1.5rem;
    word-break: break-all;
    white-space: pre;
}

span {
    cursor: default;
}

.hexviewer-hover {
    cursor: pointer;
    background-color: #ddd;
}
</style>
