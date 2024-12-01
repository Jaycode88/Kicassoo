document.addEventListener('DOMContentLoaded', function () {
    const variantSelect = document.getElementById('variant-select');
    const priceDisplay = document.getElementById('product-price');

    // Set initial price on page load if there are multiple variants
    if (variantSelect) {
        const initialPrice = variantSelect.options[variantSelect.selectedIndex].getAttribute('data-price');
        priceDisplay.textContent = `£${initialPrice}`;

        // Update displayed price when variant changes
        variantSelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            const price = selectedOption.getAttribute('data-price');
            priceDisplay.textContent = `£${price}`;
        });
    }

    // Handle quantity increment and decrement buttons
    const decrementBtn = document.querySelector('.decrement-qty');
    const incrementBtn = document.querySelector('.increment-qty');
    const qtyInput = document.getElementById('quantity-input');

    decrementBtn.addEventListener('click', function () {
        let currentValue = parseInt(qtyInput.value);
        if (currentValue > 1) {
            qtyInput.value = currentValue - 1;
        }
    });

    incrementBtn.addEventListener('click', function () {
        let currentValue = parseInt(qtyInput.value);
        const maxValue = parseInt(qtyInput.getAttribute('max'));
        if (currentValue < maxValue) {
            qtyInput.value = currentValue + 1;
        }
    });
});