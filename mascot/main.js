// Electron main process: creates the small, frameless, transparent, always-on-top mascot window.
// Owner: Michael
// Docs (Electron 44): https://www.electronjs.org/docs/latest/api/browser-window

const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("node:path");

const WINDOW_WIDTH = 340;
// Starting guess only: the page reports its real content height right after it loads
// (mascot:set-height) and the window shrinks/grows to fit, so there's no empty space.
const WINDOW_HEIGHT = 300;
const MIN_HEIGHT = 120;
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
  // No title bar, so the page has its own × button (see preload.js).
}

// The × button in the page (preload.js exposes window.mascotApp.quit()).
ipcMain.on("mascot:quit", () => app.quit());

// The page's content changed height: fit the window to it, keeping the BOTTOM edge where
// it is, so the mascot grows upward from its corner instead of sliding off the screen.
ipcMain.on("mascot:set-height", (event, height) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (!win || !Number.isFinite(height)) return; // never trust values from the page blindly

  const bounds = win.getBounds();
  const { workArea } = screen.getDisplayMatching(bounds);
  const newHeight = Math.round(Math.min(Math.max(height, MIN_HEIGHT), workArea.height));
  if (newHeight === bounds.height) return;

  const bottom = bounds.y + bounds.height;
  const y = Math.max(workArea.y, bottom - newHeight); // don't push the top off-screen
  win.setBounds({ x: bounds.x, y, width: bounds.width, height: newHeight });
});

app.whenReady().then(createWindow);

app.on("window-all-closed", () => app.quit());
