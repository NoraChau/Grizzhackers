/**
 * Electron main process: creates the small always-on-top overlay window.
 *
 * Owner: Experienced #2
 * Docs: https://www.electronjs.org/docs/latest/api/browser-window
 *       https://www.electronjs.org/docs/latest/tutorial/security
 */
import { app, BrowserWindow, screen } from "electron";
import * as path from "node:path";

const WIDTH = 320;
const HEIGHT = 420;
const MARGIN = 16; // gap from the screen edge

function createOverlayWindow(): BrowserWindow {
  // Bottom-right corner of the main screen, above the taskbar.
  const area = screen.getPrimaryDisplay().workArea;

  const win = new BrowserWindow({
    width: WIDTH,
    height: HEIGHT,
    x: area.x + area.width - WIDTH - MARGIN,
    y: area.y + area.height - HEIGHT - MARGIN,
    alwaysOnTop: true,
    frame: false, // no title bar; index.html has its own drag bar
    resizable: false,
    backgroundColor: "#111418",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true, // the page can't reach Electron or Node directly
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // __dirname is overlay/dist, so index.html is one folder up.
  void win.loadFile(path.join(__dirname, "..", "index.html"));
  return win;
}

app.whenReady().then(() => {
  createOverlayWindow();
});

app.on("window-all-closed", () => {
  app.quit();
});

// TODO(exp2): a close/hide button (frameless windows have none): expose it via preload + ipcMain.
