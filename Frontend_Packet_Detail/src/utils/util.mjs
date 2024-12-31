export function sleep(time) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve()
        }, time)
    })
}

export async function *readIter(reader) {
    while(true) {
        const { done, value } = await reader.read()
        if (!done) {
            yield value
        } else {
            return value
        }
    }
}
