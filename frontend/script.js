// ==========================================
// Configuration
// ==========================================

// Telegram bot username
const TELEGRAM_BOT_USERNAME = 'site_SEO_cheker_bot';

// API endpoint для tracking сессий
const API_ENDPOINT = 'https://seo-checker-backend-production.up.railway.app/api/track-session';

// ==========================================
// CTA Button Handler
// ==========================================

const openTelegramButton = document.getElementById('openTelegramButton');
const statusMessage = document.getElementById('statusMessage');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');

openTelegramButton.addEventListener('click', async () => {
    // Генерируем уникальный session_id
    const sessionId = crypto.randomUUID();
    
    // Извлекаем UTM-метки из URL
    const urlParams = new URLSearchParams(window.location.search);
    const utmData = {
        session_id: sessionId,
        utm_source: urlParams.get('utm_source'),
        utm_medium: urlParams.get('utm_medium'),
        utm_campaign: urlParams.get('utm_campaign'),
        utm_term: urlParams.get('utm_term'),
        utm_content: urlParams.get('utm_content'),
        referrer: document.referrer || null,
        user_agent: navigator.userAgent,
    };
    
    // Отправляем на backend для сохранения
    try {
        await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(utmData),
        });
    } catch (error) {
        console.log('Failed to track session:', error);
    }
    
    // Формируем deep link для Telegram
    const telegramDeepLink = `https://t.me/${TELEGRAM_BOT_USERNAME}?start=session_${sessionId}`;
    
    // Показываем сообщение
    showStatus('success', '✅ Открываем Telegram... Отправьте боту URL сайта для проверки.');
    
    // Открываем Telegram
    window.open(telegramDeepLink, '_blank');
    
    // Трекаем событие в аналитику
    trackEvent('telegram_bot_opened', { session_id: sessionId });
});

// ==========================================
// Status Messages
// ==========================================

function showStatus(type, message) {
    statusMessage.style.display = 'block';
    statusMessage.className = `status-message status-message--${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    statusIcon.textContent = icons[type];
    statusText.textContent = message;
    
    statusMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==========================================
// Analytics
// ==========================================

function trackEvent(eventName, params = {}) {
    // Яндекс.Метрика
    if (typeof ym !== 'undefined' && window.METRIKA_ID) {
        ym(window.METRIKA_ID, 'reachGoal', eventName, params);
    }
    
    // Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, params);
    }
    
    console.log('Event tracked:', eventName, params);
}
