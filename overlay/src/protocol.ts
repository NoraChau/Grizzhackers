/**
 * Messages shared by the overlay and the backend.
 *
 * Every WebSocket message is one JSON object: { type: "...", payload: {...} }
 * Keep this file in sync with backend/protocol.py. Add a type there -> add it here too.
 *
 * Owner: Experienced #2
 */

// Must match WS_HOST / WS_PORT in backend/protocol.py and connect-src in index.html.
export const WS_URL = "ws://127.0.0.1:8765";

export type AgentState = "idle" | "listening" | "thinking" | "acting" | "speaking" | "recording";

/** Overlay -> backend */
export type ClientMessage =
  | { type: "user_text"; payload: { text: string } }
  | { type: "confirm_response"; payload: { id: string; approved: boolean } }
  | { type: "cancel"; payload: Record<string, never> };

/** Backend -> overlay */
export type ServerMessage =
  | { type: "status"; payload: { state: AgentState } }
  | { type: "transcript"; payload: { role: "user" | "assistant"; text: string } }
  | {
      type: "step";
      payload: { tool: string; args: Record<string, unknown>; result: string; ms: number };
    }
  | { type: "confirm_request"; payload: { id: string; tool: string; summary: string } }
  | { type: "error"; payload: { message: string } };
