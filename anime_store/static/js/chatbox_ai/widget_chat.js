const BLOCKED = [
    "database",
    "sql",
    "schema",
    "source code",
    "api key",
    "token",
    "password",
    ".env",
    "administrator",
    "admin panel",
    "server",
    "backend",
    "secret"
];

const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const suggestionsEl = document.getElementById('suggestions');

let busy = false;

function scrollDown() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMsg(role, text, isTyping = false) {

    const wrap = document.createElement('div');
    wrap.className = `msg ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    if (isTyping) {

        bubble.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;

    } else {

        bubble.textContent = text;
    }

    wrap.appendChild(bubble);
    messagesEl.appendChild(wrap);

    scrollDown();

    return bubble;
}

function sendSuggestion(btn) {

    inputEl.value = btn.textContent;

    suggestionsEl.style.display = 'none';

    send();
}

function renderProducts(products) {

    if (!products || products.length === 0)
        return '';

    let html = `
        <div class="product-container">
    `;

    products.forEach(product => {

        html += `
            <div class="product-card">

                <img
                    class="product-image"
                    src="${
                        product.image
                        ? product.image
                        : '/static/img/no-image.png'
                    }"
                    alt="${product.name}"
                >

                <div class="product-content">

                    <div class="product-title">
                        ${product.name}
                    </div>

                    <div class="product-meta">
                        Anime: ${product.anime}
                    </div>

                    <div class="product-meta">
                        Kategori: ${product.category}
                    </div>

                    <div class="product-price">
                        Rp${Number(product.price).toLocaleString('id-ID')}
                    </div>

                    <a
                        href="/product/${product.id}/"
                        class="product-btn"
                    >
                        Lihat Detail
                    </a>

                </div>

            </div>
        `;
    });

    html += `</div>`;

    return html;
}

async function send() {

    const text = inputEl.value.trim();

    if (!text || busy)
        return;

    busy = true;

    sendBtn.disabled = true;

    suggestionsEl.style.display = 'none';

    inputEl.value = '';

    inputEl.style.height = '';

    addMsg('user', text);

    if (
        BLOCKED.some(
            keyword =>
            text.toLowerCase().includes(
                keyword
            )
        )
    ) {

        addMsg(
            'bot',
            'Maaf, informasi internal sistem tidak dapat diakses.'
        );

        busy = false;

        sendBtn.disabled = false;

        return;
    }

    const typingBubble =
        addMsg('bot', '', true);

    try {

        const res = await fetch(
            '/chatbox_ai/widget_chat/',
            {
                method: 'POST',

                headers: {
                    'Content-Type':
                    'application/json'
                },

                body: JSON.stringify({
                    message: text
                })
            }
        );

        if (!res.ok) {

            typingBubble.className =
                'bubble error';

            typingBubble.textContent =
                'Terjadi kesalahan pada server.';

            busy = false;

            sendBtn.disabled = false;

            return;
        }

        const data =
            await res.json();

        console.log(
            "Response AI:",
            data
        );

        const formattedAnswer =
            (data.answer || '')
            .replace(/\n/g, '<br>');

        typingBubble.innerHTML = `
            <div>
                ${formattedAnswer}
            </div>

            ${renderProducts(data.products)}
        `;

    }
    catch(error) {

        console.error(error);

        typingBubble.className =
            'bubble error';

        typingBubble.textContent =
            'Koneksi gagal. Pastikan server Django berjalan.';
    }

    busy = false;

    sendBtn.disabled = false;

    scrollDown();
}

inputEl.addEventListener(
    'keydown',
    e => {

        if (
            e.key === 'Enter' &&
            !e.shiftKey
        ) {

            e.preventDefault();

            send();
        }
    }
);

inputEl.addEventListener(
    'input',
    () => {

        inputEl.style.height = '';

        inputEl.style.height =
            Math.min(
                inputEl.scrollHeight,
                100
            ) + 'px';
    }
);