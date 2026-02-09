    const chat = document.getElementById("chat");
    const input = document.getElementById("input");

    function addMessage(text, cls) {
      const div = document.createElement("div");
      div.className = "msg " + cls;
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    async function send() {
      const text = input.value.trim();
      if (!text) return;

      addMessage("You: " + text, "user");
      input.value = "";

      try {
        await fetch("http://127.0.0.1:5000/speak", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });

        addMessage("Soso is responding…", "ai");
      } catch (err) {
        addMessage("Error: cannot reach Soso", "ai");
      }
    }

    input.addEventListener("keydown", e => {
      if (e.key === "Enter") send();
    });