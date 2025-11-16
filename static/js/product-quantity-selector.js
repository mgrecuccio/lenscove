const quantityInput = document.getElementById('quantityInput');
const totalPriceInput = document.getElementById('totalPriceInput');
const unitPrice = parseFloat(document.getElementById('unitPrice').innerText);

document.getElementById('increaseBtn').addEventListener('click', () => {
   let currentVal = parseInt(quantityInput.value);
   if (!isNaN(currentVal) && currentVal < 99) {
      quantityInput.value = currentVal + 1;
      updateTotalPrice();
   }
});

document.getElementById('decreaseBtn').addEventListener('click', () => {
   let currentVal = parseInt(quantityInput.value);
   if (!isNaN(currentVal) && currentVal > 1) {
      quantityInput.value = currentVal - 1;
      updateTotalPrice();
   }
});

document.addEventListener('click', () => {
   let currentVal = parseInt(quantityInput.value);
   if (!isNaN(currentVal)) {
      if (currentVal > 99) quantityInput.value = 99;
      if (currentVal < 1) quantityInput.value = 1;
      updateTotalPrice();
   }
});

function updateTotalPrice() {
   let quantity = parseInt(quantityInput.value);
   if (!isNaN(quantity) && quantity > 0) {
      totalPriceInput.value = (unitPrice * quantity).toFixed(2);
   }
}