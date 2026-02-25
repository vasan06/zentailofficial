// --- Chatbot Elements ---
const ZT_ConfettiBtn = document.querySelector('.confetti-btn');
const ZT_Chatbot = document.getElementById('chatbot-popup');
const ZT_Close = document.getElementById('chatbot-close');
const ZT_Input = document.getElementById('chatbot-input');
const ZT_Send = document.getElementById('chatbot-send');
const ZT_Messages = document.getElementById('chatbot-messages');

// --- Append Message ---
function ZT_AppendMessage(sender, text){
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('zt-msg', sender);
    msgDiv.innerText = text;
    ZT_Messages.appendChild(msgDiv);
    ZT_Messages.scrollTop = ZT_Messages.scrollHeight;
}

// --- Bot Response Logic ---
// ----------------------
// ZenTail Chatbot Logic
// ----------------------
function ZT_BotReply(userMsg) {
    userMsg = userMsg.toLowerCase().trim();

    // --- Initial Greetings ---
    const greetingsKeywords = ['hello','hi','hey','greetings'];
    if (greetingsKeywords.some(word => userMsg.includes(word))) {
        return "Hello! 👋 I'm your ZenTail assistant. How can I make your pet care experience smoother today?";
    }

    if (userMsg.includes('how are you') || userMsg.includes('how is it going')) {
        return "I'm doing great, thank you! 🐾 Ready to help you with pet care, products, or booking appointments.";
    }

    // --- Products ---
    if (userMsg.includes('product') || userMsg.includes('products') || userMsg.includes('buy')) {
        return "We have a variety of curated pet products! 🐶🐱\n\n" +
               "1️⃣ Visit the PRODUCTS section from the main menu.\n" +
               "2️⃣ Browse categories like Food, Toys, and Accessories.\n" +
               "3️⃣ Click on a product to see details.\n" +
               "4️⃣ Add to cart and proceed to checkout.\n\n" +
               "Do you want me to guide you to a specific product type?";
    }

    // --- Breeds Info ---
    if (userMsg.includes('breed') || userMsg.includes('breeds') || userMsg.includes('dog breed') || userMsg.includes('cat breed')) {
        return "We have detailed info on various pet breeds! 🐕🐈\n\n" +
               "1️⃣ Go to the BREEDS section.\n" +
               "2️⃣ Select Dog or Cat.\n" +
               "3️⃣ Browse through breeds with images, personality traits, and care tips.\n\n" +
               "Would you like me to suggest a breed based on your lifestyle?";
    }

    // --- Vet Locator ---
    if (userMsg.includes('vet') || userMsg.includes('veterinarian') || userMsg.includes('clinic') || userMsg.includes('hospital')) {
        return "Finding a vet is easy! 🏥\n\n" +
               "1️⃣ Go to the VET LOCATOR section.\n" +
               "2️⃣ Enter your city or zip code.\n" +
               "3️⃣ Browse the list of nearby veterinary clinics.\n" +
               "4️⃣ Click a clinic for contact info and directions.\n\n" +
               "Do you want me to suggest the closest clinic to you?";
    }

    // --- Booking Appointment ---
    if ((userMsg.includes('book') && userMsg.includes('appointment')) || userMsg.includes('schedule') || userMsg.includes('slot')) {
        return "Sure! Let's get your appointment booked. 📅\n\n" +
               "1️⃣ Go to the BOOK SLOT page.\n" +
               "2️⃣ Choose the type of service (Vet Consultation, Grooming, etc.).\n" +
               "3️⃣ Select a preferred date and time.\n" +
               "4️⃣ Fill in your pet's details.\n" +
               "5️⃣ Confirm your booking and you'll receive a notification.\n\n" +
               "Do you want me to guide you through the booking process step by step?";
    }

    // --- Account Management ---
    if (userMsg.includes('account') || userMsg.includes('login') || userMsg.includes('signup') || userMsg.includes('register')) {
        return "Managing your account is simple! 📝\n\n" +
               "1️⃣ Click on 'Account' in the top menu.\n" +
               "2️⃣ Log in with your email and password.\n" +
               "3️⃣ You can update your details, view bookings, and access products.\n\n" +
               "Need help with a specific account issue?";
    }

    // --- Orders, Shipping & Refunds ---
    if (userMsg.includes('order') || userMsg.includes('shipping') || userMsg.includes('delivery')) {
        return "For your orders and shipping info:\n\n" +
               "1️⃣ Visit the PRODUCTS section and check your cart or past orders.\n" +
               "2️⃣ Click on an order to see status and tracking.\n" +
               "3️⃣ For delays or issues, contact our support at zentailofficials@gmail.com.\n\n" +
               "Do you want me to check a specific order for you?";
    }

    if (userMsg.includes('pay') || userMsg.includes('payment') || userMsg.includes('refund') || userMsg.includes('return')) {
        return "Payment and refunds are straightforward:\n\n" +
               "1️⃣ Complete checkout using card, UPI, or net banking.\n" +
               "2️⃣ For refunds, open your order and click 'Request Refund'.\n" +
               "3️⃣ Follow the instructions to return the product.\n" +
               "4️⃣ Refunds are processed within 5-7 business days.\n\n" +
               "Need help initiating a refund?";
    }

    // --- Thank You / Goodbye ---
    if (userMsg.includes('thank') || userMsg.includes('thanks')) {
        return "You're welcome! 😊 Always happy to help you and your pets!";
    }

    if (userMsg.includes('bye') || userMsg.includes('see you')) {
        return "Goodbye! 🐾 Take care of your furry friend and come back anytime!";
    }

    // --- Fallback for unrecognized input ---
    return "I want to help you better! Could you please rephrase your question or tell me specifically what you need help with? " +
           "For example, you can ask about products, breeds, vet locator, booking an appointment, or account help.";
}


// --- Open Chatbot and Initial Greeting ---
ZT_ConfettiBtn.addEventListener('click', () => {
    ZT_Chatbot.style.display = 'flex';
    ZT_Input.focus();

    // Send greeting only once per session
    if(!ZT_Chatbot.dataset.greeted){
        ZT_AppendMessage('bot', "Hello! 👋 I'm your ZenTail assistant. How can I help you today?");
        ZT_Chatbot.dataset.greeted = 'true';
    }
});

// --- Close Chatbot ---
ZT_Close.addEventListener('click', () => {
    ZT_Chatbot.style.display = 'none';
});

// --- Send User Message ---
ZT_Send.addEventListener('click', () => {
    const msg = ZT_Input.value.trim();
    if(!msg) return;

    ZT_AppendMessage('user', msg);
    ZT_Input.value = '';

    // Simulate typing delay
    setTimeout(() => {
        const botReply = ZT_BotReply(msg);
        ZT_AppendMessage('bot', botReply);
    }, 600);
});

// --- Enter Key Send ---
ZT_Input.addEventListener('keydown', (e) => {
    if(e.key === 'Enter') ZT_Send.click();
});
function ZT_SetTheme(dark) {
    document.body.classList.toggle('night-mode', dark);

    // Toggle chatbot dark mode
    const chatbot = document.getElementById('chatbot-popup');
    if (chatbot) chatbot.classList.toggle('night-mode', dark);

    // Optionally toggle icons if you have sun/moon icons
    const lightIcon = document.getElementById('theme-light-icon');
    const darkIcon = document.getElementById('theme-dark-icon');
    if (lightIcon && darkIcon) {
        lightIcon.style.display = dark ? 'none' : 'inline';
        darkIcon.style.display = dark ? 'inline' : 'none';
    }

    localStorage.setItem('theme', dark ? 'dark' : 'light');
}

// Apply theme on page load
window.addEventListener('DOMContentLoaded', () => {
    const isDark = localStorage.getItem('theme') === 'dark';
    ZT_SetTheme(isDark);
});

// Theme toggle button

if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
        ZT_SetTheme(!document.body.classList.contains('night-mode'));
    });
}

