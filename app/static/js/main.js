// app/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const queryInput = document.getElementById('query-input');
    const submitButton = document.getElementById('submit-query');
    const messages = document.getElementById('messages');

    submitButton.addEventListener('click', () => {
        const query = queryInput.value.trim();
        if (query) {
            addMessage(query, 'user');
            socket.emit('query', { query });
            queryInput.value = '';
        }
        messages.scrollTop = messages.scrollHeight; // Scroll to the bottom
    });

    socket.on('response', (data) => {
        addMessage(formatResponse(data.response), 'ai');
        messages.scrollTop = messages.scrollHeight; // Scroll to the bottom
    });

    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.innerHTML = text; // Use innerHTML for formatted text
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight; // Scroll to the bottom
    }

    function formatResponse(response) {
        return response.replace(/\n/g, '<br>').replace(/(\*\*|__)(.*?)\1/g, '<strong>$2</strong>');
        // Add more formatting rules as needed
    }
});