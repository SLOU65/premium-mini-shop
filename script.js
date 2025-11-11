let cart = [
  {
    name: "Utharaa Stone island",
    price: 70.00,
    quantity: 2
  }
];

function calculateTotal(cart) {
  return cart.reduce((sum, item) => sum + item.price * (item.quantity || 1), 0);
}

function checkout() {
  const name = document.getElementById("name").value;
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

  Telegram.WebApp.sendData(JSON.stringify(order));
  window.open("https://t.me/CryptoBot?start=your_payment_token", "_blank");
}
