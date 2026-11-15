// Renderer: the mascot page's own script. Talks to the backend over a WebSocket.
// Owner: Michael
// MessageType, MascotState and WS_URL come from protocol.js (loaded first in index.html).
//
// TODO(Michael): connect with new WebSocket(WS_URL). If the backend isn't up yet, retry
//   every 2 s instead of giving up.
// TODO(Michael): on each message: JSON.parse -> switch on msg.type -> call the functions below.
// TODO(Michael): on Enter in the request box: send {type: MessageType.USER_TEXT, payload: {text}}
//   and clear the box.
// TODO(Michael): Yes/No buttons -> send MessageType.CONFIRM_RESPONSE with the request's id.
// WebSocket docs: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

const RETRY_MS = 2000;

const mascotEl = document.getElementById("mascot");
const bubbleEl = document.getElementById("bubble");
const confirmEl = document.getElementById("confirm");
const requestEl = document.getElementById("request");
const yesEl = document.getElementById("confirm-yes");
const noEl = document.getElementById("confirm-no");
const closeEl = document.getElementById("close");
const sendEl = document.getElementById("send");
const micEl = document.getElementById("mic");
const micLabelEl = document.getElementById("mic-label");
const hintKeyEl = document.querySelector("#hint kbd");

let socket = null
let pendingConfirmId = null
// The backend does the recording; this only mirrors what it last told us (MIC_STATUS).
let micOn = false

function connect() {
  socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("connected to backend");
  };

  socket.onmessage = (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch {
      console.error("bad message from backend:", event.data);
      return;
    }
    handleMessage(msg);
  };

  socket.onclose = () => {
    setMic(false); // no backend = nothing is recording
    console.log(`not connected, retrying in ${RETRY_MS / 1000} s`);
    setTimeout(connect, RETRY_MS);
  };
}

function handleMessage(msg) {
  switch (msg.type) {
    case MessageType.STATE:
      setState(msg.payload.state);
      break;
    case MessageType.REPLY:
      showReply(msg.payload.text);
      break;
    case MessageType.TRANSCRIPT:
      // Already sent to the agent by the backend: show it, don't put it in the box
      // (or pressing Enter would send it a second time).
      showReply(`You said: "${msg.payload.text}"`);
      break;
    case MessageType.CONFIRM_REQUEST:
      askConfirm(msg.payload.id, msg.payload.question);
      break;
    case MessageType.ERROR:
      showReply(`Oops: ${msg.payload.message}`);
      break;
    case MessageType.MIC_STATUS:
      setMic(msg.payload.recording === true);
      if (msg.payload.key) hintKeyEl.textContent = msg.payload.key;
      break;
    default:
      console.warn("unknown message type:", msg.type);
  }
}

function sendMessage(type, payload) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    showReply("I'm not connected to my brain yet. Is the backend running?");
    return;
  }
  socket.send(JSON.stringify({ type, payload }));
}

/** Show `text` in the speech bubble. */
function showReply(text) {
  bubbleEl.textContent = text;
}

/** Switch the bear's look. `state` is one of MascotState (idle, thinking, talking, confirm). */
function setState(state) {
  mascotEl.dataset.state = state;
}

/** Show the question with Yes/No buttons; remember `id` for the CONFIRM_RESPONSE. */
function askConfirm(id, question) {
  pendingConfirmId = id;
  showReply(question);
  confirmEl.hidden = false;
  yesEl.focus();
}

function answerConfirm(approved) {
  if (pendingConfirmId === null) return;
  sendMessage(MessageType.CONFIRM_RESPONSE, { id: pendingConfirmId, approved });
  pendingConfirmId = null;
  confirmEl.hidden = true;
  requestEl.focus();
}

/** Show the mic as on (red, "Stop") or off ("Talk"). Called when the backend says so. */
function setMic(on) {
  micOn = on;
  micEl.setAttribute("aria-pressed", String(on));
  micLabelEl.textContent = on ? "Stop" : "Talk";
  micEl.title = on ? "Stop and send" : "Start talking";
  if (on) showReply("I'm listening...");
}

// One click on, one click off. The button only changes once the backend confirms
// (MIC_STATUS), so it can't show "recording" when the mic failed to open.
micEl.addEventListener("click", () => {
  sendMessage(MessageType.MIC, { on: !micOn });
});

/** Send what's in the request box (Enter key or the Enter button), then clear it. */
function submitRequest() {
  const text = requestEl.value.trim();
  if (text === "") {
    requestEl.focus();
    return;
  }
  sendMessage(MessageType.USER_TEXT, { text });
  requestEl.value = "";
  requestEl.focus(); // ready for the next request without another click
}

requestEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter") submitRequest();
});
sendEl.addEventListener("click", submitRequest);

// × button: quit the whole mascot app (window.mascotApp comes from preload.js).
closeEl.addEventListener("click", () => {
  if (micOn) sendMessage(MessageType.MIC, { on: false }); // don't leave the mic recording
  window.mascotApp.quit();
});

yesEl.addEventListener("click", () => answerConfirm(true));
noEl.addEventListener("click", () => answerConfirm(false));

// Fit the window to the content: whenever the content's height changes (longer reply,
// Yes/No buttons shown/hidden), tell Electron the new height. No empty space above.
function fitWindow() {
  window.mascotApp.setHeight(Math.ceil(mascotEl.getBoundingClientRect().height));
}
new ResizeObserver(fitWindow).observe(mascotEl);

connect();
requestEl.focus();
