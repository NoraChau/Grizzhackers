// Hands-free mode: point with your head, hold still on a button to press it.
// Owner: Michael
//
// How it works:
//   1. The webcam feed goes into MediaPipe Face Landmarker, which finds ~478 points on the
//      face many times a second. Everything runs on this laptop: no video leaves the page.
//   2. Head direction = where the NOSE TIP sits relative to the midpoint between the outer
//      eye corners, divided by the eye distance (so it doesn't matter how close you sit).
//   3. For the first second we record the user's comfortable "straight ahead" pose. After
//      that, turning/tilting the head moves the pointer away from the window's center.
//   4. Dwell click: hold the pointer on a [data-dwell] button and a ring fills up; when it's
//      full (2 s, or data-dwell-ms) we call button.click(), exactly like a mouse click.
//      After a click you must move off that button before it can fire again.
//
// The pointer only moves inside the mascot window (not the whole screen): small head
// movements cover a small area, which is far more precise than whole-screen tracking.
//
// Docs: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/web_js

import {
  FaceLandmarker,
  FilesetResolver,
} from "./node_modules/@mediapipe/tasks-vision/vision_bundle.mjs";

// ---- Tuning: change these after trying it ----
const DWELL_MS = 2000; // default hold time to click (a button can override with data-dwell-ms)
const SENSITIVITY_X = 6; // higher = less head turn needed to reach the window's left/right edge
const SENSITIVITY_Y = 8; // higher = less head tilt needed to reach the top/bottom
const SMOOTHING = 0.25; // 0..1: lower = steadier but laggier pointer
const SNAP_PX = 24; // a pointer this close to a button counts as on it (helps accuracy)
const GRACE_MS = 250; // brief wobbles off a button don't reset the ring
const CALIBRATE_MS = 1000; // how long we record the "straight ahead" pose
const RECENTER_AFTER_LOST_MS = 3000; // face gone this long -> recalibrate when it's back

// Landmark indexes in MediaPipe's face mesh.
const NOSE_TIP = 1;
const RIGHT_EYE_OUTER = 33; // the person's right eye
const LEFT_EYE_OUTER = 263;

const toggleEl = document.getElementById("hands-free");
const toggleLabelEl = document.getElementById("hands-free-label");
const pointerEl = document.getElementById("head-pointer");
const videoEl = document.getElementById("camera");

let landmarker = null;
let stream = null;
let rafId = 0;
let on = false;
let busy = false; // starting/stopping in progress

// Head tracking state
let neutral = null; // {x, y} "straight ahead" pose
let calibration = []; // samples collected while calibrating
let calibrateUntil = 0;
let lastVideoTime = -1;
let lastFaceAt = 0;
let pointer = null; // smoothed {x, y} in window pixels

// Dwell state
let dwellTarget = null;
let dwellStart = 0;
let lostSince = null;
let mustLeave = null; // the button just clicked: ignore it until the pointer leaves it

// ---------------------------------------------------------------- on / off

function say(text) {
  // showReply() lives in renderer.js (a classic script, so it's a global).
  if (typeof window.showReply === "function") window.showReply(text);
}

async function createLandmarker() {
  const base = new URL("./node_modules/@mediapipe/tasks-vision/wasm", import.meta.url).href;
  const model = new URL("./models/face_landmarker.task", import.meta.url).href;
  const fileset = await FilesetResolver.forVisionTasks(base);
  const options = (delegate) => ({
    baseOptions: { modelAssetPath: model, delegate },
    runningMode: "VIDEO",
    numFaces: 1,
  });
  try {
    return await FaceLandmarker.createFromOptions(fileset, options("GPU"));
  } catch (err) {
    console.warn("GPU face tracking failed, using CPU:", err);
    return FaceLandmarker.createFromOptions(fileset, options("CPU"));
  }
}

async function start() {
  if (on || busy) return;
  busy = true;
  toggleLabelEl.textContent = "Starting…";
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: "user" },
      audio: false,
    });
    videoEl.srcObject = stream;
    await videoEl.play();
    landmarker ??= await createLandmarker();
  } catch (err) {
    console.error("hands-free failed to start:", err);
    releaseCamera();
    busy = false;
    toggleLabelEl.textContent = "Hands-free";
    say(
      err?.name === "NotAllowedError" || err?.name === "NotFoundError"
        ? "I couldn't open the camera. Check that one is plugged in and that Windows lets apps use it."
        : "Sorry, hands-free mode couldn't start.",
    );
    return;
  }

  on = true;
  busy = false;
  document.body.classList.add("hands-free");
  toggleEl.setAttribute("aria-pressed", "true");
  toggleLabelEl.textContent = "Hands-free on";
  toggleEl.title = "Turn hands-free off (F8, or hold the pointer here for 4 seconds)";
  lastFaceAt = performance.now();
  beginCalibration("Hands-free is on. Look at the bear and hold still for a moment…");
  rafId = requestAnimationFrame(tick);
}

function releaseCamera() {
  stream?.getTracks().forEach((track) => track.stop()); // turns the camera light off
  stream = null;
  videoEl.srcObject = null;
}

function stop() {
  if (!on || busy) return;
  on = false;
  cancelAnimationFrame(rafId);
  releaseCamera();
  setDwellTarget(null, 0);
  mustLeave = null;
  pointer = null;
  pointerEl.hidden = true;
  document.body.classList.remove("hands-free");
  toggleEl.setAttribute("aria-pressed", "false");
  toggleLabelEl.textContent = "Hands-free";
  toggleEl.title = "Hands-free mode (F8)";
  say("Hands-free is off.");
}

function toggle() {
  if (on) stop();
  else start();
}

// ---------------------------------------------------------------- head -> pointer

/** Forget "straight ahead"; the next CALIBRATE_MS of face frames set it again. */
function beginCalibration(message) {
  neutral = null;
  calibration = [];
  pointer = null;
  pointerEl.hidden = true;
  setDwellTarget(null, performance.now());
  say(message);
}

/** Head direction from one face: nose offset from the eyes' midpoint, in eye-widths. */
function headDirection(landmarks) {
  // Landmarks are 0..1 of the image's width/height; use pixels so x and y match.
  const w = videoEl.videoWidth || 640;
  const h = videoEl.videoHeight || 480;
  const nose = landmarks[NOSE_TIP];
  const r = landmarks[RIGHT_EYE_OUTER];
  const l = landmarks[LEFT_EYE_OUTER];
  const eyeDist = Math.hypot((l.x - r.x) * w, (l.y - r.y) * h) || 1;
  return {
    x: ((nose.x - (l.x + r.x) / 2) * w) / eyeDist,
    y: ((nose.y - (l.y + r.y) / 2) * h) / eyeDist,
  };
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function tick(now) {
  if (!on) return;
  rafId = requestAnimationFrame(tick);

  // Only run the model when the camera has a new frame.
  if (videoEl.readyState < 2 || videoEl.currentTime === lastVideoTime) return;
  lastVideoTime = videoEl.currentTime;

  const result = landmarker.detectForVideo(videoEl, now);
  const face = result.faceLandmarks?.[0];

  if (!face) {
    // No face (looked away, left the desk): hide the pointer and never click.
    pointerEl.hidden = true;
    if (dwellTarget) setDwellTarget(null, now);
    if (neutral && now - lastFaceAt > RECENTER_AFTER_LOST_MS) {
      // Gone a while: they may sit differently when they're back, so recalibrate.
      beginCalibration("I lost sight of you. Look at the bear and hold still for a moment…");
    }
    return;
  }

  const head = headDirection(face);
  lastFaceAt = now;

  if (!neutral) {
    // Time the calibration from the first frame that actually has a face in it.
    if (calibration.length === 0) calibrateUntil = now + CALIBRATE_MS;
    calibration.push(head);
    if (now < calibrateUntil) return;
    neutral = {
      x: calibration.reduce((sum, p) => sum + p.x, 0) / calibration.length,
      y: calibration.reduce((sum, p) => sum + p.y, 0) / calibration.length,
    };
    calibration = [];
    say("Ready! Move your head to point, and hold still on a button for 2 seconds to press it.");
  }

  // The camera sees you mirrored: turning to YOUR right moves your nose LEFT in the image,
  // so flip x. Then scale so a comfortable head turn reaches the window's edge.
  const halfW = window.innerWidth / 2;
  const halfH = window.innerHeight / 2;
  const target = {
    x: halfW + clamp(-(head.x - neutral.x) * SENSITIVITY_X, -1, 1) * halfW,
    y: halfH + clamp((head.y - neutral.y) * SENSITIVITY_Y, -1, 1) * halfH,
  };
  pointer = pointer
    ? {
        x: pointer.x + (target.x - pointer.x) * SMOOTHING,
        y: pointer.y + (target.y - pointer.y) * SMOOTHING,
      }
    : target;

  pointerEl.hidden = false;
  pointerEl.style.transform = `translate(${pointer.x}px, ${pointer.y}px)`;
  updateDwell(pointer.x, pointer.y, now);
}

// ---------------------------------------------------------------- dwell click

function isUsable(el) {
  return el.offsetParent !== null && !el.disabled; // offsetParent is null when hidden
}

/** The dwell button under (x, y), or the nearest one within SNAP_PX. */
function findTarget(x, y) {
  const hit = document.elementFromPoint(x, y)?.closest("[data-dwell]");
  if (hit && isUsable(hit)) return hit;

  let best = null;
  let bestDist = SNAP_PX;
  for (const el of document.querySelectorAll("[data-dwell]")) {
    if (!isUsable(el)) continue;
    const r = el.getBoundingClientRect();
    const dx = Math.max(r.left - x, 0, x - r.right);
    const dy = Math.max(r.top - y, 0, y - r.bottom);
    const dist = Math.hypot(dx, dy);
    if (dist < bestDist) {
      best = el;
      bestDist = dist;
    }
  }
  return best;
}

function setDwellTarget(el, now) {
  dwellTarget?.classList.remove("dwell-hover");
  dwellTarget = el;
  dwellStart = now;
  lostSince = null;
  el?.classList.add("dwell-hover");
  pointerEl.style.setProperty("--progress", "0");
}

function updateDwell(x, y, now) {
  let target = findTarget(x, y);

  // Just clicked this one: wait until the pointer leaves it (no accidental double clicks,
  // e.g. Talk turning straight into Stop).
  if (mustLeave) {
    if (target === mustLeave) target = null;
    else mustLeave = null;
  }

  if (target !== dwellTarget) {
    // Short wobbles off the button keep the ring going.
    if (dwellTarget && !target) {
      lostSince ??= now;
      if (now - lostSince < GRACE_MS) return;
    }
    setDwellTarget(target, now);
    return;
  }
  lostSince = null;
  if (!dwellTarget) return;

  const holdMs = Number(dwellTarget.dataset.dwellMs) || DWELL_MS;
  const progress = Math.min((now - dwellStart) / holdMs, 1);
  pointerEl.style.setProperty("--progress", String(progress));

  if (progress >= 1) {
    const clicked = dwellTarget;
    setDwellTarget(null, now);
    mustLeave = clicked;
    clicked.click();
  }
}

// ---------------------------------------------------------------- wiring

toggleEl.addEventListener("click", toggle);
window.mascotApp?.onToggleHandsFree?.(toggle); // F8 (see main.js)

// Hands-free starts every time the mascot opens: someone who needs it can't click to turn
// it on. Anyone who doesn't want it turns it off (button, F8, or a 4 s hold on the button);
// that lasts until the mascot is closed, and the next launch starts hands-free again.
start();
