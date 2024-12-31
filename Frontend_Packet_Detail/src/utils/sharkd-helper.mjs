import { parseDetailTree as sharkdTreeParse } from "@/utils/test-helper.mjs"

const apiPort = '/nmas'
let loadedSession = []

async function getResult(response) {
    const result = await response.json()
    if (!result.success) {
        throw new Error(result.result)
    } else {
        return result.result
    }
}

function syncCloseSession() {
    for (const session of loadedSession) {
        const params = new URLSearchParams({
            uuid: session
        })
        const xmlHttp = new XMLHttpRequest()
        xmlHttp.open('GET', `${apiPort}/close_session?${params}`, false)
        xmlHttp.send()
    }
}

export async function closeSession(session) {
    const params = new URLSearchParams({
        uuid: session
    })
    const response = await fetch(`${apiPort}/close_session?${params}`)
    loadedSession = loadedSession.filter(e => e != session)
    return await getResult(response)
}

export async function initDissector() {
    const response = await fetch(`${apiPort}/creat_session`)
    const uuid = await getResult(response)
    const session = uuid
    loadedSession.push(session)
    return session
}
window.addEventListener('beforeunload', () => {
    syncCloseSession(session)
})

export async function loadFile(session, file, state=null) {
    const paramsLoad = new URLSearchParams({
        uuid: session,
        method: 'load',
        params: JSON.stringify({ file })
    })
    const responseLoad = await fetch(`${apiPort}/session_request?${paramsLoad}`)
    await getResult(responseLoad)
    const paramsStatus = new URLSearchParams({
        uuid: session,
        method: 'status',
        params: JSON.stringify({})
    })
    const responseStatus = await fetch(`${apiPort}/session_request?${paramsStatus}`)
    const {frames} = await getResult(responseStatus)
    return frames
}

export async function checkFilter(session, filter) {
    const params = new URLSearchParams({
        uuid: session,
        method: 'frames',
        params: JSON.stringify({ filter })
    })
    const response = await fetch(`${apiPort}/session_request?${params}`)
    await getResult(response)
}

export async function getFrames(session, filter, skip=null, limit=null, state=null) {
    const frameParams = { filter }
    if (skip > 0) {
        frameParams.skip = skip
    }
    if (limit > 0) {
        frameParams.limit = limit
    }
    const params = new URLSearchParams({
        uuid: session,
        method: 'frames',
        params: JSON.stringify(frameParams)
    })
    const response = await fetch(`${apiPort}/session_request?${params}`)
    const list = await getResult(response)
    return list
}

export async function parseFrame(session, id) {
    const params = new URLSearchParams({
        uuid: session,
        method: 'frame',
        params: JSON.stringify({ frame: id, proto: true, bytes: true })
    })
    const response = await fetch(`${apiPort}/session_request?${params}`)
    const tree = await getResult(response)
    return tree
}

export function parseDetailTree(data, layer=[]) {
    return sharkdTreeParse(data, layer)
}

export async function getConfig() {
    const response = await fetch(`${apiPort}/static/config.json`)
    return await response.json()
}
