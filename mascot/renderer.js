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

let socket = null
let pendingConfirmId = null

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

requestEl.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  const text = requestEl.value.trim();
  if (text === "") return;
  sendMessage(MessageType.USER_TEXT, { text });
  requestEl.value = "";
});

yesEl.addEventListener("click", () => answerConfirm(true));
noEl.addEventListener("click", () => answerConfirm(false));

connect();
requestEl.focus();
