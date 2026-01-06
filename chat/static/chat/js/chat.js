/**
 * StreamEvents Chat System
 * JavaScript per al xat en temps real
 */

// Variables globals
let messagePollingInterval = null;

/**
 * Escapar HTML per prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Fer scroll al final del contenidor de missatges
 */
function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

/**
 * Actualitzar el comptador de missatges
 */
function updateMessageCount(count) {
    const countElement = document.getElementById('message-count');
    if (countElement) {
        countElement.textContent = count + ' ' + (count === 1 ? 'missatge' : 'missatges');
    }
}

/**
 * Crear element HTML per a un missatge
 */
function createMessageElement(msg) {
    const div = document.createElement('div');
    div.className = 'chat-message' + (msg.is_highlighted ? ' highlighted' : '');
    div.dataset.messageId = msg.id;

    let actionsHtml = '';
    if (msg.can_delete) {
        actionsHtml = `
            <div class="message-actions">
                <button class="btn btn-sm btn-outline-danger delete-message" 
                        data-message-id="${msg.id}" title="Eliminar missatge">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
    }

    div.innerHTML = `
        <div class="message-header">
            <strong class="message-username">${escapeHtml(msg.display_name)}</strong>
            <small class="message-time text-muted">${escapeHtml(msg.created_at)}</small>
        </div>
        <div class="message-content">${escapeHtml(msg.message)}</div>
        ${actionsHtml}
    `;

    return div;
}

/**
 * Carregar missatges del servidor
 */
function loadMessages() {
    if (typeof eventId === 'undefined') {
        console.error('eventId no definit');
        return;
    }

    fetch(`/chat/${eventId}/messages/`)
        .then(response => response.json())
        .then(data => {
            const chatMessages = document.getElementById('chat-messages');
            if (!chatMessages) return;

            // Guardar posició de scroll
            const wasAtBottom = chatMessages.scrollHeight - chatMessages.clientHeight <= chatMessages.scrollTop + 10;

            // Netejar contenidor
            chatMessages.innerHTML = '';

            // Afegir missatges
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    chatMessages.appendChild(createMessageElement(msg));
                });

                // Fer scroll al final si ja ho era o és el primer càrrega
                if (wasAtBottom) {
                    scrollToBottom();
                }
            } else {
                chatMessages.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-comments fa-2x mb-2"></i>
                        <p class="mb-0">Encara no hi ha missatges. Sigues el primer!</p>
                    </div>
                `;
            }

            // Actualitzar comptador
            updateMessageCount(data.messages ? data.messages.length : 0);
        })
        .catch(error => {
            console.error('Error carregant missatges:', error);
        });
}

/**
 * Enviar missatge al servidor
 */
function sendMessage(event) {
    event.preventDefault();

    const form = document.getElementById('chat-form');
    if (!form) return;

    const messageInput = form.querySelector('textarea[name="message"]');
    const errorsDiv = document.getElementById('chat-errors');
    const message = messageInput ? messageInput.value.trim() : '';

    if (!message) {
        if (errorsDiv) errorsDiv.textContent = 'El missatge no pot estar buit.';
        return;
    }

    // Obtenir CSRF token
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    // Crear FormData
    const formData = new FormData();
    formData.append('message', message);
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(`/chat/${eventId}/send/`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Netejar formulari
                if (messageInput) messageInput.value = '';
                if (errorsDiv) errorsDiv.textContent = '';

                // Recarregar missatges
                loadMessages();
                scrollToBottom();
            } else {
                // Mostrar errors
                if (errorsDiv && data.errors) {
                    let errorText = '';
                    for (const key in data.errors) {
                        if (Array.isArray(data.errors[key])) {
                            errorText += data.errors[key].join(', ') + ' ';
                        } else {
                            errorText += data.errors[key] + ' ';
                        }
                    }
                    errorsDiv.textContent = errorText.trim();
                }
            }
        })
        .catch(error => {
            console.error('Error enviant missatge:', error);
            if (errorsDiv) {
                errorsDiv.textContent = 'Error de connexió. Torna-ho a provar.';
            }
        });
}

/**
 * Eliminar missatge
 */
function deleteMessage(messageId) {
    if (!confirm('Segur que vols eliminar aquest missatge?')) {
        return;
    }

    // Obtenir CSRF token del formulari
    const form = document.getElementById('chat-form');
    let csrfToken = '';

    if (form) {
        const csrfInput = form.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) csrfToken = csrfInput.value;
    }

    // Si no trobem el token al formulari, buscar-lo a les cookies
    if (!csrfToken) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith('csrftoken=')) {
                csrfToken = cookie.substring('csrftoken='.length);
                break;
            }
        }
    }

    fetch(`/chat/message/${messageId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recarregar missatges
                loadMessages();
            } else {
                alert(data.error || 'Error eliminant el missatge.');
            }
        })
        .catch(error => {
            console.error('Error eliminant missatge:', error);
            alert('Error de connexió. Torna-ho a provar.');
        });
}

/**
 * Inicialització quan el DOM està carregat
 */
document.addEventListener('DOMContentLoaded', function () {
    // Event listener per al formulari d'enviar
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', sendMessage);
    }

    // Event delegation per eliminar missatges
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.addEventListener('click', function (e) {
            const deleteBtn = e.target.closest('.delete-message');
            if (deleteBtn) {
                const messageId = deleteBtn.dataset.messageId;
                if (messageId) {
                    deleteMessage(messageId);
                }
            }
        });
    }

    // Carregar missatges inicial
    loadMessages();

    // Iniciar polling cada 3 segons
    messagePollingInterval = setInterval(loadMessages, 3000);

    // Aturar polling quan es tanca la pàgina
    window.addEventListener('beforeunload', function () {
        if (messagePollingInterval) {
            clearInterval(messagePollingInterval);
        }
    });
});
