import loadWiregasm from '@goodtools/wiregasm/dist/wiregasm'

let wiregasm = null
let session = null

async function initDissector() {
    if (!wiregasm) {
        wiregasm = await loadWiregasm({
            locateFile: (path, prefix) => {
                if (path.endsWith('.data')) return new URL('/wiregasm.data', import.meta.url)
                if (path.endsWith('.wasm')) return new URL('/wiregasm.wasm', import.meta.url).toString()
                return prefix + path
            }
        })
        wiregasm.init()
    }
}

async function loadFile(file) {
    wiregasm.FS.writeFile('/uploads/file.pcap', file)
    session = new wiregasm.DissectSession('/uploads/file.pcap')
    const ret = session.load()
    if (ret.code) {
        throw new Error(ret.error)
    }
    return ret.summary.packet_count
}

async function getFrames(filter, skip, limit) {
    const { frames } = session.getFrames(filter, skip, limit)
    const frameNum = frames.size()
    const list = []
    for (let i = 0; i < frameNum; i++) {
        const rawFrame = frames.get(i)
        if (i % 10000 == 0) {
            postMessage({
                func: 'update',
                result: Math.floor(i * 100 / frameNum),
                success: true
            })
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

function parseDetailTree(data, layer=[]) {
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

async function parseFrame(id) {
    const { tree, data_sources } = session.getFrame(id)
    return {
        tree: parseDetailTree(tree),
        bytes: data_sources.get(0).data
    }
}

const workerFunction = {
    'initDissector': initDissector,
    'loadFile': loadFile,
    'getFrames': getFrames,
    'parseFrame': parseFrame
}

onmessage = function({ data }) {
    const { func, args } = data
    workerFunction[func].apply(this, args).then((result) => postMessage({
        func, result, success: true
    })).catch((err) => postMessage({
        func, result: err, success: false
    }))
}
  