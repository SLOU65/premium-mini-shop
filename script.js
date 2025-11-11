// Корзина — можно заменить на динамическую
const cart = [
  { name: "Utharaa Stone island", price: 70.00, quantity: 2 }
];

// Подсчёт суммы
function calculateTotal(cart) {
  return cart.reduce((sum, item) => sum + item.price * (item.quantity || 1), 0);
}

// Основная функция оформления заказа
async function checkout() {
  const name = document.getElementById("fullName").value;
  const address = document.getElementById("address").value;
  const phone = document.getElementById("phone").value;
  const email = document.getElementById("email").value;

  const order = {
    order_id: "ORD-" + Date.now().toString(36).toUpperCase(),
    fullname: name,
    address: address,
    phone: phone,
    email: email,
    items: cart,
    total: calculateTotal(cart),
    date: new Date().toLocaleDateString(),
    time: new Date().toLocaleTimeString(),
    language: Telegram.WebApp.initDataUnsafe.user?.language_code || "ru"
  };

  // Отправка заказа в Telegram-бот
  Telegram.WebApp.sendData(JSON.stringify(order));

  // Создание счёта через CryptoBot API
  const response = await fetch("https://pay.crypt.bot/api/createInvoice", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Crypto-Pay-API-Token": "ТВОЙ_API_ТОКЕН" // ← замени на свой токен
    },
    body: JSON.stringify({
      asset: "USDT", // можно BTC, TON, ETH
      amount: order.total,
      description: `Оплата заказа ${order.order_id}`,
      payload: JSON.stringify(order),
      allow_comments: false,
      allow_anonymous: false
    })
  });

  const data = await response.json();
  if (data.ok) {
    window.open(data.result.bot_invoice_url, "_blank");
  } else {
    console.error("Ошибка создания счёта:", data.error);
  }
}
