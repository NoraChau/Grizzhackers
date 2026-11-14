// Electron main process: creates the small, frameless, transparent, always-on-top mascot window.
// Owner: Michael
// Docs (Electron 44): https://www.electronjs.org/docs/latest/api/browser-window

const { app, BrowserWindow, screen } = require("electron");
const path = require("node:path");

const WINDOW_WIDTH = 340;
const WINDOW_HEIGHT = 440;
const MARGIN = 16; // gap from the screen edge

function createWindow() {
  // Bottom-right corner, above the taskbar (workArea excludes the taskbar).
  const { workArea } = screen.getPrimaryDisplay();

  const win = new BrowserWindow({
    width: WINDOW_WIDTH,
    height: WINDOW_HEIGHT,
    x: workArea.x + workArea.width - WINDOW_WIDTH - MARGIN,
    y: workArea.y + workArea.height - WINDOW_HEIGHT - MARGIN,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    hasShadow: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true, // the page can't touch Node or Electron directly
      nodeIntegration: false,
      sandbox: true,
    },
  });

  win.loadFile("index.html");

  // TODO(Michael): the transparent parts of the window still block clicks to apps behind it.
  // See win.setIgnoreMouseEvents(true, { forward: true }) in the BrowserWindow docs.
  // TODO(Michael): there's no title bar, so add a way to quit (tray icon or a hotkey).
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => app.quit());
