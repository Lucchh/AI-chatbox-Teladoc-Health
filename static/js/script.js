// script.js

document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("sendBtn");
    const userInput = document.getElementById("userInput");
    const messages = document.getElementById("messages");
  
    sendBtn.addEventListener("click", () => {
      sendMessage();
    });
  
    // Optional: allow sending message on "Enter" key
    userInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
      }
    });
  
    async function sendMessage() {
      const input = userInput.value.trim();
      if (!input) {
        alert("Please enter a message.");
        return;
      }
  
      // Display user message
      messages.innerHTML += `<p><strong>You:</strong> ${input}</p>`;
      userInput.value = "";
  
      try {
        const response = await fetch("https://flask-chatbot-1092579805305.us-east1.run.app/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ input }),
        });
  
        const data = await response.json();
  
        // Display chatbot response
        if (data.response) {
          messages.innerHTML += `<p><strong>Chatbot:</strong> ${data.response}</p>`;
        } else {
          messages.innerHTML += `<p><strong>Chatbot:</strong> Sorry, I couldn't understand that.</p>`;
        }
      } catch (error) {
        messages.innerHTML += `<p><strong>Chatbot:</strong> Error connecting to the server. Please try again later.</p>`;
      }
  
      // Scroll to the bottom of the chat
      messages.scrollTop = messages.scrollHeight;
    }
  });
  