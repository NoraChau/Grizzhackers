// Electron main process: creates the small, frameless, transparent, always-on-top mascot window.
// Owner: Michael
// Docs (Electron 44): https://www.electronjs.org/docs/latest/api/browser-window

const { app, BrowserWindow, globalShortcut, ipcMain, screen, session } = require("electron");
const path = require("node:path");

const WINDOW_WIDTH = 340;
// Starting guess only: the page reports its real content height right after it loads
// (mascot:set-height) and the window shrinks/grows to fit, so there's no empty space.
const WINDOW_HEIGHT = 300;
const MIN_HEIGHT = 120;
const MARGIN = 16; // gap from the screen edge

// Turns hands-free (head pointer) mode on/off from anywhere, even when the mascot window
// isn't focused: handy for a helper setting things up. One key, no chord.
const HANDS_FREE_KEY = "F8";

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
      // Keep head tracking running while the user works in another app (the mascot is
      // always visible, but Chromium would otherwise slow down an unfocused page).
      backgroundThrottling: false,
    },
  });

  win.loadFile("index.html");

  globalShortcut.register(HANDS_FREE_KEY, () => {
    win.webContents.send("mascot:toggle-hands-free");
  });

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

// Permissions: the page may use the CAMERA (hands-free head tracking) and nothing else:
// no microphone (the Python backend records audio), location, notifications, etc.
function isCameraOnly(permission, details) {
  if (permission !== "media") return false;
  const types = details?.mediaTypes ?? [];
  return types.length > 0 && types.every((type) => type === "video");
}

app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_webContents, permission, callback, details) => {
    callback(isCameraOnly(permission, details));
  });
  session.defaultSession.setPermissionCheckHandler((_webContents, permission, _origin, details) => {
    return permission === "media" && (details?.mediaType ?? "video") === "video";
  });
  createWindow();
});

app.on("will-quit", () => globalShortcut.unregisterAll());

app.on("window-all-closed", () => app.quit());
