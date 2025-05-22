(function () {
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const chatForm = document.getElementById("chat-input-area");

  // Simulated AI reply (placeholder logic)
  function getBotResponse(userMessage) {
    const lower = userMessage.toLowerCase();
    if (lower.includes("hello") || lower.includes("hi")) {
      return "Hello! How can I assist you today?";
    }
    if (lower.includes("how are you")) {
      return "I'm an AI, so I don't have feelings, but thanks for asking!";
    }
    if (lower.includes("bye") || lower.includes("goodbye")) {
      return "Goodbye! Have a nice day!";
    }
    return "Sorry, I don't have an answer for that yet.";
  }

  // Append a message to the chat area
  function appendMessage(text, sender = "bot") {
    const msgEl = document.createElement("div");
    msgEl.textContent = text;
    msgEl.classList.add(sender === "user" ? "user-message" : "bot-message");
    chatMessages.appendChild(msgEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Handle chat form submit
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;

    appendMessage(msg, "user");
    chatInput.value = "";

    // Simulate AI response delay
    setTimeout(() => {
      const botReply = getBotResponse(msg);
      appendMessage(botReply, "bot");
    }, 800);
  });
})();
