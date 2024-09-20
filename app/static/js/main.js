// app/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const queryInput = document.getElementById('query-input');
    const submitButton = document.getElementById('submit-query');
    const responseContent = document.getElementById('response-content');

    submitButton.addEventListener('click', () => {
        const query = queryInput.value.trim();
        if (query) {
            responseContent.innerHTML = 'Processing query...';
            socket.emit('query', { query: query });
        }
    });

    socket.on('response', (data) => {
        responseContent.innerHTML = data.response;
    });
});
