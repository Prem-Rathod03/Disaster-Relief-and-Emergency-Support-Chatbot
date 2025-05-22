(function () {
  const chatMessages = document.getElementById("messages");
  const chatInput = document.getElementById("user-input");
  const chatForm = document.getElementById("chat-form");

  // Append a message to the chat area
  function appendMessage(text, sender = "bot") {
    const msgEl = document.createElement("div");
    msgEl.textContent = text;
    msgEl.classList.add(sender === "user" ? "user-message" : "bot-message");
    chatMessages.appendChild(msgEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Handle chat form submit
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;

    appendMessage(msg, "user");
    chatInput.value = "";

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: msg,
          user_id: "default_user",
        }),
      });

      const data = await response.json();
      appendMessage(data.response, "bot");
    } catch (error) {
      console.error("Error communicating with chatbot:", error);
      appendMessage(
        "Oops! Something went wrong while contacting the chatbot.",
        "bot"
      );
    }
  });
})();
