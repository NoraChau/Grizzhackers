/**
 * Preload script: runs before index.html loads and is the only bridge between the page and Electron.
 * Expose a *small*, specific API with contextBridge. Never expose ipcRenderer itself.
 *
 * Owner: Experienced #2
 * Docs: https://www.electronjs.org/docs/latest/tutorial/context-isolation
 */
import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("companion", {
  // TODO(exp2): add what the page needs, e.g. hide() for a close button.
  overlayVersion: "0.1.0",
});
