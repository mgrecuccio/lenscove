const quantityInput = document.getElementById('quantityInput');
document.getElementById('increaseBtn').addEventListener('click', () => {
   let currentVal = parseInt(quantityInput.value);
   if (!isNaN(currentVal) && currentVal < 99) {
      quantityInput.value = currentVal + 1;
   }
});

document.getElementById('decreaseBtn').addEventListener('click', () => {
   let currentVal = parseInt(quantityInput.value);
   if (!isNaN(currentVal) && currentVal > 1) {
      quantityInput.value = currentVal - 1;
   }
});

document.addEventListener('click', () => {
   let currentVal = parseInt(quantityInput.value);
   if (!isNaN(currentVal) && currentVal > 99) {
      quantityInput.value = 99;
   }
});