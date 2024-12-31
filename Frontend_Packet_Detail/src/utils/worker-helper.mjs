import { isRef } from 'vue'

let worker = null
let refState = null

const waitMap = new Map()

function workerCallback({ data }) {
    const { func, result, success } = data
    console.log(data)
    if (func === 'update') {
        if (isRef(refState)) {
            refState.value = result
        }
    }
    if (waitMap.has(func)) {
        const { resolve, reject } = waitMap.get(func)
        if (success) {
            resolve(result)
        } else {
            reject(result)
        }
        waitMap.delete(func)
    }
}

function workCall(func, ...args) {
    if (!worker) {
        throw new Error('No worker')
    }
    if (waitMap.has(func)) {
        throw new Error('Worker busy')
    }
    return new Promise((resolve, reject) => {
        waitMap.set(func, { resolve, reject })
        worker.postMessage({
            func, args
        })
    })
}

export async function initDissector(url, state=null) {
    refState = state
    if (!worker) {
        worker = new Worker(url, { type : 'module' })
        worker.onmessage = workerCallback
        await workCall('initDissector')
    }
}

export async function loadFile(file, state=null) {
    refState = state
    return await workCall('loadFile', file)
}

export async function getFrames(filter, skip, limit, state=null) {
    refState = state
    return await workCall('getFrames', filter, skip, limit)
}

export function parseDetailTree(data, layer=[]) {
    return data
}

export async function parseFrame(id) {
    return await workCall('parseFrame', id)
}
