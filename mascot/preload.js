// Preload script: runs before the page loads, with a safe bridge to Electron.
// Owner: Michael
//
// renderer.js talks to the backend with the browser's own WebSocket. The page only needs
// a few things from Electron: quitting (the × button), fitting the window to its content,
// and hearing the F8 hands-free shortcut. Expose just those small functions.
// Never expose ipcRenderer itself.
// Docs: https://www.electronjs.org/docs/latest/tutorial/context-isolation

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("mascotApp", {
  quit: () => ipcRenderer.send("mascot:quit"),
  setHeight: (height) => ipcRenderer.send("mascot:set-height", height),
  // Calls `callback()` whenever F8 is pressed. Don't pass the IPC event to the page.
  onToggleHandsFree: (callback) => ipcRenderer.on("mascot:toggle-hands-free", () => callback()),
});
