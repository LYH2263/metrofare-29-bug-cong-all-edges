export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
async function sendJSON(method, path, body) {
  const r = await fetch(path, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export const postJSON = (path, body) => sendJSON('POST', path, body)
export const putJSON = (path, body) => sendJSON('PUT', path, body)
export async function deleteJSON(path) {
  const r = await fetch(path, { method: 'DELETE' })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
