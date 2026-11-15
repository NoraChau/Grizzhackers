// Message types shared with the backend. MUST match backend/protocol.py.
// Every WebSocket message is JSON: {"type": "...", "payload": {...}}
//
// Loaded before renderer.js in index.html, so renderer.js can use these names.
// Owner: Michael

const WS_URL = "ws://127.0.0.1:8765"; // same as WS_HOST/WS_PORT in protocol.py and the CSP in index.html

const MessageType = Object.freeze({
  // mascot -> backend
  USER_TEXT: "user_text", // payload: {text}
  CONFIRM_RESPONSE: "confirm_response", // payload: {id, approved}
  MIC: "mic", // payload: {on}   mic button: start/stop recording

  // backend -> mascot
  STATE: "state", // payload: {state}  one of MascotState
  REPLY: "reply", // payload: {text}   show in the speech bubble
  TRANSCRIPT: "transcript", // payload: {text}   what speech-to-text heard
  CONFIRM_REQUEST: "confirm_request", // payload: {id, question}
  ERROR: "error", // payload: {message}
  MIC_STATUS: "mic_status", // payload: {recording, key}   is the mic on, and the hotkey name
});

const MascotState = Object.freeze({
  IDLE: "idle",
  THINKING: "thinking",
  TALKING: "talking",
  CONFIRM: "confirm", // asking yes/no before a destructive action
});
