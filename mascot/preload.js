// Preload script: runs before the page loads, with a safe bridge to Electron.
// Owner: Michael
//
// renderer.js talks to the backend with the browser's own WebSocket. The page only needs
// two things from Electron: quitting (the × button) and fitting the window to its content.
// Expose just those small functions. Never expose ipcRenderer itself.
// Docs: https://www.electronjs.org/docs/latest/tutorial/context-isolation

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("mascotApp", {
  quit: () => ipcRenderer.send("mascot:quit"),
  setHeight: (height) => ipcRenderer.send("mascot:set-height", height),
});
