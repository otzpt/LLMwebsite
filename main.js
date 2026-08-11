document.addEventListener('DOMContentLoaded', () => {
  //main elements
  const form = document.getElementById('chat-form');
  const input = document.getElementById('message');
  const messages = document.getElementById('messages');

  // URL for backend communication
  const BACKEND_URL = 'https://localhost:5000/chat';

  //function to get input msg
  function addMessage(text, isUser) {
    const msgDiv = document.createElement('div');

    msgDiv.classname = isUser ? 'message user' : 'message bot';
    msgDiv.textContent = text;
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage(message) {
    try {
      const res = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
      });

      if (!res.ok) {
        throw new Error(`server responded with ${res.status}`);
      }
      const data = await res.json();
      addMessage(data.response, false);
    } catch (err) {
      addMessage('Error: could not reach the server.', false);
      console.error(err);
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, true);
    input.value = '';
    sendMessage(message);
  });
});
