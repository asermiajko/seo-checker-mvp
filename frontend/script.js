// ==========================================
// Configuration
// ==========================================

// Telegram bot username
const TELEGRAM_BOT_USERNAME = 'site_SEO_cheker_bot';

// API endpoint для логирования (опционально)
const API_ENDPOINT = '/api/track-check';

// ==========================================
// Form Submission
// ==========================================

const form = document.getElementById('seoCheckForm');
const submitButton = document.getElementById('submitButton');
const statusMessage = document.getElementById('statusMessage');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Получить URL сайта
    const siteUrl = document.getElementById('siteUrl').value.trim();
    
    // Валидация
    if (!validateUrl(siteUrl)) {
        showStatus('error', 'Пожалуйста, введите корректный URL (например: https://example.ru)');
        return;
    }
    
    // Открыть Telegram бот с deep link
    openTelegramBot(siteUrl);
    
    // Логировать в аналитику
    trackEvent('telegram_bot_opened', { site_url: siteUrl });
    
    // Опционально: отправить на сервер для статистики
    await logCheck(siteUrl);
});

// ==========================================
// Telegram Deep Link
// ==========================================

function openTelegramBot(siteUrl) {
    // Кодируем URL для передачи в deep link
    // Формат: https://t.me/bot_name?start=check_ENCODED_URL
    const encodedUrl = encodeURIComponent(siteUrl);
    const telegramDeepLink = `https://t.me/${TELEGRAM_BOT_USERNAME}?start=check_${encodedUrl}`;
    
    // Показать сообщение
    showStatus('success', '✅ Открываем Telegram... Напишите /start боту для получения отчёта.');
    
    // Открыть Telegram
    window.open(telegramDeepLink, '_blank');
    
    // Очистить форму
    setTimeout(() => {
        form.reset();
    }, 1000);
}

// ==========================================
// API: Log Check (опционально)
// ==========================================

async function logCheck(siteUrl) {
    try {
        await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                site_url: siteUrl,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                referrer: document.referrer || 'direct'
            })
        });
    } catch (error) {
        // Не критично, просто логируем
        console.log('Failed to log check:', error);
    }
}

// ==========================================
// Validation
// ==========================================

function validateUrl(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
        return false;
    }
}

// ==========================================
// Status Messages
// ==========================================

function showStatus(type, message) {
    statusMessage.style.display = 'block';
    statusMessage.className = `status-message status-message--${type}`;
    
    // Иконки для разных статусов
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    statusIcon.textContent = icons[type];
    statusText.textContent = message;
    
    // Скролл к сообщению
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

// ==========================================
// Input Enhancement
// ==========================================

// Auto-format URL (add https:// if missing)
const urlInput = document.getElementById('siteUrl');
urlInput.addEventListener('blur', (e) => {
    let value = e.target.value.trim();
    
    // Если есть значение и нет протокола, добавить https://
    if (value && !value.match(/^https?:\/\//i)) {
        e.target.value = 'https://' + value;
    }
});
