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

const mascotEl = document.getElementById("mascot");
const bubbleEl = document.getElementById("bubble");
const confirmEl = document.getElementById("confirm");
const requestEl = document.getElementById("request");

/** Show `text` in the speech bubble. */
function showReply(text) {
  // TODO(Michael)
}

/** Switch the bear's look. `state` is one of MascotState (idle, thinking, talking, confirm). */
function setState(state) {
  // TODO(Michael): style.css can style each state via mascotEl.dataset.state
}

/** Show the question with Yes/No buttons; remember `id` for the CONFIRM_RESPONSE. */
function askConfirm(id, question) {
  // TODO(Michael)
}
