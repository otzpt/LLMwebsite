document.addEventListener('DOMContentLoaded', () => {
    // grab the pieces of the page we need
    const form = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const messages = document.getElementById('messages');

    // where the backend is running, change this if you deploy it somewhere else
    const BACKEND_URL = 'https://2a01-4f9-3a-276e--1019.sslip.io/generate';

    // adds a message bubble to the chat window
    function addMessage(text, isUser) {
        const msgDiv = document.createElement('div');
        msgDiv.className = isUser ? 'message user' : 'message bot'; // different color depending on who sent it
        msgDiv.textContent = text;
        messages.appendChild(msgDiv);
        messages.scrollTop = messages.scrollHeight; // auto scroll to the bottom
    }

    // sends the user's message to the backend and shows whatever comes back
  async function sendMessage(message) {
    //shows if model thinking or nah
    const loadingMsg = addMessage('Thinking...', false);
    // god this is hard to read
        try {
            const res = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: message })
            });

            if (!res.ok) {
                throw new Error(`Server responded with ${res.status}`); // backend is up but returned an error
            }

            const data = await res.json();
          loadingMsg.textContent = data.answer;
        } catch (err) {
            // backend is down, unreachable, or something broke, don't just fail silently
          loadingMsg.textContent = 'Error: could not reach the server.';
            console.error(err);
        }
    }

    // runs every time the user hits send / presses enter
    form.addEventListener('submit', (e) => {
        e.preventDefault(); // stop the page from reloading, which is what forms do by default
        const message = input.value.trim();
        if (!message) return; // ignore empty messages

        addMessage(message, true); // show the user's own message immediately
        input.value = '';           // clear the input box
        sendMessage(message);       // go get the real response
    });
});
