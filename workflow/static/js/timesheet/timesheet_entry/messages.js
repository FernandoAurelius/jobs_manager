import { sentMessages } from './state.js'


/**
 * Renders dynamic messages in the template's message container.
 * @param {Array} messages - List of messages in the format [{level: "success|error|info", message: "Message"}].
 */
export function renderMessages(messages) {
    const alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        console.error('Alert container not found.');
        return;
    }

    // Add new messages
    messages.forEach(msg => {
        const messageKey = `${msg.level}:${msg.message}`;

        console.log(sentMessages);
        if (sentMessages.has(messageKey) && msg.level !== 'success') {
            console.log('Message skipped (already sent).');
            return;
        }
        sentMessages.add(messageKey);

        const alertDiv = document.createElement('div');
        msg.level = msg.level === 'error' ? 'danger' : msg.level;
        alertDiv.className = `alert alert-${msg.level} alert-dismissible fade show mt-1`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${msg.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.appendChild(alertDiv);

        // Add fade out effect after 1 second if message level is success
        console.log("Message level: ", msg.level);
        if (msg.level === 'success') {
            setTimeout(() => {
                alertDiv.classList.remove('show');
                alertDiv.classList.add('fade');
                setTimeout(() => {
                    alertDiv.remove();
                }, 150); // Wait for fade animation to complete
            }, 2000);
        }
    });
}