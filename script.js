/* script.js — frontend: формирование order, sendData и createInvoice */
const CART_KEY = 'continental_cart_v1';
let cart = JSON.parse(localStorage.getItem(CART_KEY) || '[]');

function saveCart() { localStorage.setItem(CART_KEY, JSON.stringify(cart)); }
function calculateTotal(cart) {
  return cart.reduce((sum, item) => sum + (Number(item.price || item.item_price || 0) * (item.quantity || item.qty || 1)), 0);
}

function generateOrderId(){
  return 'ORD-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).substr(2,5).toUpperCase();
}

async function createInvoice(order) {
  // Лучше: проксировать этот запрос через ваш сервер, чтобы не раскрывать токен в клиенте.
  const CRYPTO_TOKEN = 'REPLACE_WITH_CRYPTO_PAY_API_TOKEN'; // ← временно/только для тестов
  const body = {
    asset: "USDT",
    amount: order.total,
    description: `Оплата заказа ${order.order_id}`,
    payload: JSON.stringify(order),
    allow_comments: false,
    allow_anonymous: false
  };

  const resp = await fetch("https://pay.crypt.bot/api/createInvoice", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Crypto-Pay-API-Token": CRYPTO_TOKEN
    },
    body: JSON.stringify(body)
  });
  const data = await resp.json();
  return data;
}

async function checkout() {
  const fullname = document.getElementById('fullName')?.value?.trim() || '';
  const address = document.getElementById('address')?.value?.trim() || '';
  const phone = document.getElementById('phone')?.value?.trim() || '';
  const email = document.getElementById('email')?.value?.trim() || '';
  if (!fullname || !address) {
    alert('Пожалуйста, заполните имя и адрес доставки');
    return;
  }

  const order_id = generateOrderId();
  const order = {
    order_id,
    fullname,
    address,
    phone,
    email,
    items: cart,
    total: calculateTotal(cart),
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString(),
    language: (window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code) || 'ru',
    user_agent: navigator.userAgent
  };

  console.log('ORDER -> sendData & createInvoice', order);

  // 1) отправляем в бот (чтобы бот уже видел заказ в orders_store)
  try {
    if (window.Telegram && Telegram.WebApp && Telegram.WebApp.sendData) {
      Telegram.WebApp.sendData(JSON.stringify(order));
    } else {
      console.warn('Telegram.WebApp.sendData not available (are you testing outside WebApp?)');
    }
  } catch (e) {
    console.warn('sendData failed', e);
  }

  // 2) создаём invoice через CryptoBot API
  try {
    const res = await createInvoice(order);
    console.log('createInvoice response', res);
    if (res && res.ok && res.result && res.result.bot_invoice_url) {
      // открываем окно оплаты
      window.open(res.result.bot_invoice_url, '_blank');
      // закрываем/скрываем модалку при желании
      if (typeof closeDeliveryModal === 'function') closeDeliveryModal();
    } else {
      console.error('createInvoice failed', res);
      alert('Не удалось создать счёт для оплаты. Проверьте консоль.');
    }
  } catch (err) {
    console.error('createInvoice error', err);
    alert('Ошибка при создании счёта. Попробуйте позже.');
  }
}
