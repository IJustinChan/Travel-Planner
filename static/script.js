document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const tripIdEl = document.getElementById('tripId');

    if (!chatForm || !chatMessages || !messageInput || !tripIdEl) {
        return;
    }

    const tripId = tripIdEl.value;

    function addMessage(sender, text) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${sender}`;
        messageEl.textContent = text;
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    chatForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (!message) {
            return;
        }

        addMessage('user', message);
        messageInput.value = '';
        messageInput.disabled = true;

        try {
            const response = await fetch(`/chatbot/${tripId}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Request failed');
            }

            const data = await response.json();
            addMessage('bot', data.reply || 'Sorry, I could not generate a response.');
        } catch (error) {
            addMessage('bot', 'Sorry, the chatbot is unavailable right now.');
        } finally {
            messageInput.disabled = false;
            messageInput.focus();
        }
    });
});
