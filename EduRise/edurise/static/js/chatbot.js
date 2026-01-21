document.addEventListener('DOMContentLoaded', function () {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMessages = document.getElementById('chat-messages');

    const chatMicBtn = document.getElementById('chat-mic-btn');
    const stopSpeechBtn = document.getElementById('chat-stop-speech-btn');
    let recognition = null;
    let isListening = false;
    let synth = window.speechSynthesis;
    let isOpen = false;

    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US'; // Changed to English

        recognition.onstart = () => {
            isListening = true;
            chatMicBtn.classList.add('listening');
            chatInput.placeholder = 'Listening...';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            sendMessage();
        };

        recognition.onerror = (event) => {
            console.error('Speech Recognition Error:', event.error);
            stopListening();
        };

        recognition.onend = () => {
            stopListening();
        };
    } else {
        if (chatMicBtn) chatMicBtn.style.display = 'none';
        console.warn('Speech Recognition not supported in this browser.');
    }

    function stopListening() {
        isListening = false;
        if (chatMicBtn) chatMicBtn.classList.remove('listening');
        chatInput.placeholder = 'Type your question...';
        if (recognition) recognition.stop();
    }

    function toggleListening() {
        if (isListening) {
            stopListening();
        } else {
            if (recognition) recognition.start();
        }
    }

    if (chatMicBtn) chatMicBtn.addEventListener('click', toggleListening);

    // Stop Speech Functionality
    if (stopSpeechBtn) {
        stopSpeechBtn.addEventListener('click', function () {
            if (synth.speaking) {
                synth.cancel();
                stopSpeechBtn.style.display = 'none';
            }
        });
    }

    // Toggle Chat Window
    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            chatWindow.style.display = 'flex';
            chatInput.focus();
        } else {
            chatWindow.style.display = 'none';
            if (synth.speaking) {
                synth.cancel();
                if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
            }
        }
    }

    if (chatToggleBtn) chatToggleBtn.addEventListener('click', toggleChat);
    if (chatCloseBtn) chatCloseBtn.addEventListener('click', toggleChat);

    // Send Message Logic
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input
        chatInput.value = '';
        stopListening();
        if (synth.speaking) {
            synth.cancel();
            if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
        }

        // Add User Message
        addMessage(message, 'user');

        // Add Loading Indicator
        const loadingId = addLoadingIndicator();

        try {
            const response = await fetch('/chatbot/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            });

            const data = await response.json();

            // Remove Loading Indicator
            removeLoadingIndicator(loadingId);

            if (data.error) {
                addMessage('Error: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
                speakText(data.response); // Automatically read bot response
            }

        } catch (error) {
            removeLoadingIndicator(loadingId);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
            console.error('Chat Error:', error);
        }
    }

    function speakText(text) {
        if (!synth) return;
        if (synth.speaking) synth.cancel();

        if (stopSpeechBtn) stopSpeechBtn.style.display = 'flex';

        // Stripping markdown/HTML for cleaner speech
        const cleanText = text.replace(/<[^>]*>/g, '').replace(/[*#_`]/g, '');

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'en-US'; // Changed to English
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onend = () => {
            if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
        };
        utterance.onerror = () => {
            if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
        };

        // Find a natural English voice
        const voices = synth.getVoices();
        const englishVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) ||
            voices.find(v => v.lang.startsWith('en'));
        if (englishVoice) utterance.voice = englishVoice;

        synth.speak(utterance);
    }

    if (chatSendBtn) chatSendBtn.addEventListener('click', sendMessage);

    if (chatInput) {
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Helper: Add Message to UI
    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.classList.add('message', sender);

        if (sender === 'bot') {
            // Render markdown for bot messages
            const html = renderMarkdown(text);
            div.innerHTML = html;
        } else {
            // Keep user messages as plain text for security
            div.textContent = text;
        }

        chatMessages.appendChild(div);
        scrollToBottom();
    }

    // Helper: Render Markdown to HTML (lightweight implementation)
    function renderMarkdown(text) {
        if (!text) return '';

        let html = text;

        // Escape HTML first to prevent XSS
        html = html.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Headers (h1-h6)
        html = html.replace(/^######\s+(.+)$/gm, '<h6>$1</h6>');
        html = html.replace(/^#####\s+(.+)$/gm, '<h5>$1</h5>');
        html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
        html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');

        // Bold (**text** or __text__)
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

        // Italic (*text* or _text_)
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.+?)_/g, '<em>$1</em>');

        // Inline code (`code`)
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Tables (improved markdown table parsing)
        html = html.replace(/\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)/g, function (match, header, rows) {
            let table = '<table><thead><tr>';

            // Parse header
            const headerCells = header.split('|').map(cell => cell.trim()).filter(cell => cell);
            headerCells.forEach(cell => {
                table += '<th>' + cell + '</th>';
            });
            table += '</tr></thead><tbody>';

            // Parse rows
            const rowLines = rows.trim().split('\n').filter(line => line.trim());
            rowLines.forEach(row => {
                const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
                if (cells.length > 0) {
                    table += '<tr>';
                    cells.forEach(cell => {
                        table += '<td>' + cell + '</td>';
                    });
                    table += '</tr>';
                }
            });

            table += '</tbody></table>';
            return '\n' + table + '\n';
        });

        // Unordered lists
        html = html.replace(/^\s*[-*+]\s+(.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Ordered lists
        html = html.replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>');

        // Line breaks and paragraphs
        html = html.replace(/\n\n/g, '</p><p>');
        html = '<p>' + html + '</p>';

        // Clean up empty paragraphs
        html = html.replace(/<p>\s*<\/p>/g, '');
        html = html.replace(/<p>(<[uo]l>)/g, '$1');
        html = html.replace(/(<\/[uo]l>)<\/p>/g, '$1');
        html = html.replace(/<p>(<table>)/g, '$1');
        html = html.replace(/(<\/table>)<\/p>/g, '$1');
        html = html.replace(/<p>(<h[1-6]>)/g, '$1');
        html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');

        return html;
    }

    // Helper: Add Loading Indicator
    function addLoadingIndicator() {
        const div = document.createElement('div');
        div.classList.add('typing-indicator');
        div.id = 'typing-' + Date.now();
        div.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(div);
        scrollToBottom();
        return div.id;
    }

    // Helper: Remove Loading Indicator
    function removeLoadingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Helper: Scroll to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Ensure voices are loaded
    if (synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = () => {
            // Voice list updated
        };
    }
});
 
