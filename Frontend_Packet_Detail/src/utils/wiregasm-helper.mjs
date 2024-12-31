import loadWiregasm from '@goodtools/wiregasm/dist/wiregasm'

import { readIter } from '@/utils/util.mjs'

import { isRef } from 'vue'

let wiregasm = null
let session = null

export async function initDissector(state=null) {
    if (!wiregasm) {
        wiregasm = await loadWiregasm({
            locateFile: (path, prefix) => {
                if (path.endsWith('.data')) return './wiregasm.data'
                if (path.endsWith('.wasm')) return './wiregasm.wasm'
                return prefix + path
            }
        })
        wiregasm.init()
    }
}

export async function downloadFile(url, state=null) {
    const response = await fetch(url)
    const size = parseInt(response.headers.get('content-length'))
    let downloadedSize = 0
    const reader = response.body.getReader()
    const chunks = []
    for await (const data of readIter(reader)) {
        chunks.push(data)
        downloadedSize += data.length
        const progress = Math.floor(downloadedSize / size * 100)
        if (isRef(state)) {
            state.value = progress
        }
    }
    const blob = new Blob(chunks)
    return new Uint8Array(await blob.arrayBuffer())
}

export async function loadFile(file, state=null) {
    wiregasm.FS.writeFile('/uploads/file.pcap', file)
    session = new wiregasm.DissectSession('/uploads/file.pcap')
    const ret = session.load()
    if (ret.code) {
        throw new Error(ret.error)
    }
    return ret.summary.packet_count
}

export async function getFrames(filter, skip, limit, state=null) {
    const { frames } = session.getFrames(filter, skip, limit)
    const frameNum = frames.size()
    const list = []
    const realState = isRef(state) ? state : { value : 0 }
    for (let i = 0; i < frameNum; i++) {
        const rawFrame = frames.get(i)
        if (i % 10000 == 0) {
            realState.value = Math.floor(i * 100 / frameNum)
        }
        list.push({
            bg: rawFrame.bg.toString(16).padStart(6,'0'),
            fg: rawFrame.fg.toString(16).padStart(6,'0'),
            num: rawFrame.number,
            c: Array.from({ length: rawFrame.columns.size() }, (v, k) => rawFrame.columns.get(k))
        })
    }
    return list
}

export function parseDetailTree(data, layer=[]) {
    const tree = []
    const length = data.size()
    for (let i = 0; i < length; i++) {
        const element = data.get(i)
        tree.push({
            key: layer.concat([i]).join('-'),
            label: element.label,
            children: element.tree.size() ? parseDetailTree(element.tree, layer.concat([i])) : null,
            hex: [element.start, element.length]
        })
    }
    return tree
}

export async function parseFrame(id) {
    const { tree, data_sources } = session.getFrame(id)
    return {
        tree,
        bytes: data_sources.get(0).data
    }
}
