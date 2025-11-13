/* script.js
   Формирование заказа, отправка в бот и создание invoice через CryptoBot API.
   В проде НЕ храните CRYPTO_PAY_API_TOKEN в клиенте — проксируйте запрос на сервер.
*/
const CART_KEY = 'continental_cart_v1';
let cart = JSON.parse(localStorage.getItem(CART_KEY) || '[]');

function saveCart(){ localStorage.setItem(CART_KEY, JSON.stringify(cart)); }
function calculateTotal(c){ return (c || cart).reduce((s,i)=> s + (Number(i.price || i.item_price || 0) * (i.quantity || i.qty || 1)), 0); }

function generateOrderId(){
  return 'ORD-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).substr(2,5).toUpperCase();
}

async function createInvoiceClient(order){
  const CRYPTO_TOKEN = 'REPLACE_WITH_CRYPTO_PAY_API_TOKEN'; // временно для теста
  const body = {
    asset: "USDT",
    amount: order.total,
    description: `Оплата заказа ${order.order_id}`,
    payload: JSON.stringify(order),
    allow_comments: false,
    allow_anonymous: false
  };
  const r = await fetch("https://pay.crypt.bot/api/createInvoice", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Crypto-Pay-API-Token": CRYPTO_TOKEN
    },
    body: JSON.stringify(body)
  });
  return r.json();
}

async function checkout(){
  const fullname = document.getElementById('fullName')?.value?.trim() || '';
  const address = document.getElementById('address')?.value?.trim() || '';
  const phone = document.getElementById('phone')?.value?.trim() || '';
  const email = document.getElementById('email')?.value?.trim() || '';

  if(!fullname || !address){
    alert('Пожалуйста, заполните имя и адрес доставки');
    return;
  }

  const order = {
    order_id: generateOrderId(),
    fullname,
    address,
    phone,
    email,
    items: cart,
    total: Number(calculateTotal(cart).toFixed(2)),
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString(),
    language: (window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code) || 'ru',
    user_agent: navigator.userAgent
  };

  console.log('ORDER sendData', order);

  try{
    if(window.Telegram && Telegram.WebApp && Telegram.WebApp.sendData){
      Telegram.WebApp.sendData(JSON.stringify(order));
    }
  }catch(e){ console.warn('sendData failed', e); }

  // Создаём invoice (для продакшена — проксировать этот вызов на сервер)
  try{
    const res = await createInvoiceClient(order);
    console.log('createInvoice response', res);
    if(res && res.ok && res.result && res.result.bot_invoice_url){
      window.open(res.result.bot_invoice_url, '_blank');
      // Optionally close modal: closeDeliveryModal();
    } else {
      console.error('createInvoice failed', res);
      alert('Не удалось создать счёт для оплаты. Проверь консоль.');
    }
  }catch(err){
    console.error('createInvoice error', err);
    alert('Ошибка при создании счёта. Попробуйте позже.');
  }
}
