// Preload script: runs before the page loads, with a safe bridge to Electron.
// Owner: Michael
//
// Nothing is needed here yet: renderer.js talks to the backend with the browser's own
// WebSocket. If the page ever needs Electron (e.g. to hide the window), expose ONE small
// function with contextBridge.exposeInMainWorld. Never expose ipcRenderer itself.
// Docs: https://www.electronjs.org/docs/latest/tutorial/context-isolation
