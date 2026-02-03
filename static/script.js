let sessionId = null;
const chatBox = document.getElementById('chat-box');
const inputArea = document.getElementById('input-area');
const userInput = document.getElementById('user-input');
const controlsArea = document.getElementById('controls-area');

// On Load
window.onload = function () {
    initChat();
};

async function initChat() {
    // Call Start API
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        handleBotResponse(data);
    } catch (e) {
        console.error("Failed to start chat", e);
    }
}

async function restartChat() {
    // Clear chat box
    chatBox.innerHTML = '';

    // Call Restart API with current session ID to delete it
    try {
        const response = await fetch('/api/restart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        const data = await response.json();

        // Reset session ID to start fresh
        sessionId = null;

        // Handle the restart response - no delays for instant restart
        if (data.session_id) {
            sessionId = data.session_id;
        }

        // Display messages instantly without delays for restart
        data.messages.forEach((msg, index) => {
            addMessage(msg, 'bot');
        });

        // Configure input after restart
        if (data.messages.length > 0) {
            configureInput(data);
        }
    } catch (e) {
        console.error("Failed to restart chat", e);
        addMessage("Sorry, something went wrong. Please refresh the page.", "bot");
    }
}

function handleBotResponse(data) {
    if (data.session_id) {
        sessionId = data.session_id; // Store session
    }

    // Display messages with delay
    let delay = 0;
    data.messages.forEach((msg, index) => {
        setTimeout(() => {
            showTypingIndicator().then((removeTyping) => {
                removeTyping();
                addMessage(msg, 'bot');
                // If it's the last message, show controls
                if (index === data.messages.length - 1) {
                    configureInput(data);
                }
            });
        }, delay);
        delay += 1000; // 1 second delay between messages
    });

    // If no messages (rare), just config input
    if (data.messages.length === 0) {
        configureInput(data);
    }
}

function configureInput(data) {
    // Clear previous inputs
    userInput.value = '';
    inputArea.classList.remove('active');
    userInput.value = '';
    inputArea.classList.remove('active');
    // controlsArea removed

    if (data.input_type === 'text' || data.input_type === 'tel') {
        inputArea.classList.add('active');
        userInput.type = data.input_type === 'tel' ? 'tel' : 'text';
        if (data.placeholder) {
            userInput.placeholder = data.placeholder;
        } else {
            userInput.placeholder = "Type your message...";
        }
        userInput.focus();
    } else if (data.input_type === 'button') {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper bot-wrapper';
        wrapper.style.paddingLeft = '45px'; // Offset for the icon space without showing the icon again

        // Create a container for buttons within the chat
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'button-container';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.flexWrap = 'wrap';
        buttonContainer.style.gap = '8px';
        buttonContainer.style.marginTop = '5px';

        data.buttons.forEach((btn, index) => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.innerText = btn.text;
            button.style.animationDelay = `${index * 0.1}s`;
            button.onclick = () => {
                sendSelection(btn.value, btn.text);
            };
            buttonContainer.appendChild(button);
        });

        wrapper.appendChild(buttonContainer);
        chatBox.appendChild(wrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Basic Frontend Validation for Mobile
    if (userInput.type === 'tel') {
        const cleaned = text.replace(/\s+/g, '');
        if (cleaned.length < 10) {
            addMessage("Please enter a valid mobile number (at least 10 digits).", 'bot');
            return;
        }
    }

    addMessage(text, 'user');
    inputArea.classList.remove('active'); // Hide input after sending

    // API Call
    callMessageApi(text);
}

function sendSelection(value, text) {
    addMessage(text, 'user'); // Show what user clicked
    // buttons stay in history now, or we can disable them logic elsewhere

    callMessageApi(value); // Send backend value
}

async function callMessageApi(messageOrValue) {
    // Check if this is a restart request
    if (messageOrValue === "restart") {
        return restartChat();
    }

    // Show typing generic
    const removeTyping = await showTypingIndicator(false); // Immediate typing

    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                message: messageOrValue
            })
        });

        removeTyping(); // Remove "typing..." before handling response
        const data = await response.json();
        handleBotResponse(data);

    } catch (e) {
        removeTyping();
        addMessage("Sorry, something went wrong. Please try again.", "bot", true);
        console.error(e);
    }
}

function addMessage(text, sender, isError = false) {
    const div = document.createElement('div');
    div.className = `message-wrapper ${sender}-wrapper`;

    let iconHtml = '';
    if (sender === 'bot') {
        iconHtml = `<img src="logo.jpeg" class="bot-icon" alt="Bot" onerror="this.style.backgroundColor='#002D62';">`;
    }

    const errorClass = isError ? ' error-message' : '';

    div.innerHTML = `
        ${iconHtml}
        <div class="message ${sender}-message${errorClass}">
            ${parseMarkdown(text)}
        </div>
    `;

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator(withPromise = true) {
    const div = document.createElement('div');
    div.className = 'message-wrapper bot-wrapper typing-wrapper';
    div.innerHTML = `
        <img src="logo.jpeg" class="bot-icon" alt="AI" onerror="this.style.backgroundColor='#002D62';">
        <div class="typing bot-message">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;

    const remove = () => {
        if (div.parentNode) div.parentNode.removeChild(div);
    };

    if (withPromise) {
        return new Promise(resolve => {
            setTimeout(() => resolve(remove), 600); // Fake typing delay
        });
    }
    return remove;
}

function parseMarkdown(text) {
    // Simple parser for bold and lists
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\n- (.*)/g, '<br>• $1') // Lists
        .replace(/\n/g, '<br>'); // Newlines
    return html;
}

// Enter key to send
userInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});
