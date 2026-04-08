from __future__ import annotations

import uuid
from typing import Any

import gradio as gr

from cyber_feng.backend import pending_user_messages, stream_assistant_reply_events
from cyber_feng.config import (
    APP_TITLE,
    DB_PATH,
    build_app_description,
    load_settings,
)
from cyber_feng.storage import ensure_db, save_message


READY_STATUS_TEXT = "模型状态：就绪"
CHAT_INPUT_ENTER_SCRIPT = """
<script>
(() => {
  const bindEnterToSend = () => {
    const textarea = document.querySelector("#chat-input textarea");
    const sendButton = document.querySelector(
      "#send-button button, button#send-button, #send-button",
    );

    if (!textarea || !sendButton || textarea.dataset.enterBound === "true") {
      return;
    }

    textarea.dataset.enterBound = "true";
    textarea.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.shiftKey) {
        return;
      }

      // Avoid sending while the user is still choosing IME candidates.
      if (event.isComposing || event.keyCode === 229) {
        return;
      }

      event.preventDefault();
      sendButton.click();
    });
  };

  const startBinding = () => {
    bindEnterToSend();

    if (window.__chatEnterObserverAttached) {
      return;
    }

    window.__chatEnterObserverAttached = true;
    new MutationObserver(bindEnterToSend).observe(document.body, {
      childList: true,
      subtree: true,
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startBinding, { once: true });
  } else {
    startBinding();
  }
})();
</script>
"""


def clone_history(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(item) for item in history]


def build_app() -> gr.Blocks:
    settings = load_settings()
    ensure_db(DB_PATH)

    def add_message(
        history: list[dict[str, Any]] | None,
        user_text: str | None,
        session_id: str,
    ) -> tuple[list[dict[str, Any]], str]:
        history = history or []
        text = (user_text or "").strip()

        if not text:
            return history, ""

        history.append({"role": "user", "content": text})
        save_message(DB_PATH, session_id, "user", text)
        return history, ""

    def submit_messages(
        history: list[dict[str, Any]] | None,
        session_id: str,
    ) -> tuple[list[dict[str, Any]], str]:
        history = history or []
        pending = pending_user_messages(history)

        if not pending:
            yield clone_history(history), READY_STATUS_TEXT
            return

        request_history = clone_history(history)
        stream_history = clone_history(history)
        stream_history.append({"role": "assistant", "content": ""})
        current_status = "模型状态：准备中"
        saw_error = False

        yield clone_history(stream_history), current_status

        for event in stream_assistant_reply_events(request_history, settings):
            event_type = event["type"]
            event_text = event["text"]

            if event_type == "status":
                current_status = f"模型状态：{event_text}"
                yield clone_history(stream_history), current_status
                continue

            if event_type == "delta":
                stream_history[-1]["content"] += event_text
                yield clone_history(stream_history), current_status
                continue

            if event_type == "error":
                saw_error = True
                stream_history[-1]["content"] = event_text
                yield clone_history(stream_history), READY_STATUS_TEXT

        final_reply = (stream_history[-1].get("content") or "").strip()
        if final_reply:
            save_message(DB_PATH, session_id, "assistant", final_reply)

        if not saw_error:
            yield clone_history(stream_history), READY_STATUS_TEXT

    with gr.Blocks(title=APP_TITLE, head=CHAT_INPUT_ENTER_SCRIPT) as app:
        gr.Markdown(build_app_description(settings))
        status_markdown = gr.Markdown(READY_STATUS_TEXT)

        chatbot = gr.Chatbot(height=520, label="峰哥")
        session_id = gr.State(str(uuid.uuid4()))
        chat_input = gr.Textbox(
            lines=3,
            max_lines=6,
            placeholder="输入消息，按回车发送，Shift+回车换行。",
            show_label=False,
            elem_id="chat-input",
        )
        send_button = gr.Button("发送", variant="primary", elem_id="send-button")

        send_event = chat_input.submit(
            add_message,
            inputs=[chatbot, chat_input, session_id],
            outputs=[chatbot, chat_input],
        )
        send_event.then(
            submit_messages,
            inputs=[chatbot, session_id],
            outputs=[chatbot, status_markdown],
        )
        send_button.click(
            add_message,
            inputs=[chatbot, chat_input, session_id],
            outputs=[chatbot, chat_input],
        ).then(
            submit_messages,
            inputs=[chatbot, session_id],
            outputs=[chatbot, status_markdown],
        )

    return app


def launch_app() -> None:
    build_app().queue(default_concurrency_limit=1).launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    launch_app()
