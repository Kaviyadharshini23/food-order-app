async function updateCart(itemId, action) {
  const res = await fetch('/cart/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_id: itemId, action })
  });
  if (res.ok) {
    window.location.reload();
  }
}
