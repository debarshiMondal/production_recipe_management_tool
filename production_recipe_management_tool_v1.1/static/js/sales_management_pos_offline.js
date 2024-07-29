document.addEventListener('DOMContentLoaded', function () {
    function calculateSubtotal() {
        let subtotal = 0;

        document.querySelectorAll('.dish-select:checked').forEach(checkbox => {
            const row = checkbox.closest('tr');
            const price = parseFloat(row.querySelector('.dish-price').textContent.replace('₹', ''));
            subtotal += price;

            const addOnDetails = row.querySelector('.add-on-details:not(.d-none)');
            if (addOnDetails) {
                const qty = parseFloat(addOnDetails.querySelector('.add-on-qty').value) || 0;
                const unitCost = parseFloat(addOnDetails.querySelector('.add-on-price').value) || 0;
                const grossMargin = parseFloat(addOnDetails.querySelector('.add-on-gross-margin').value) || 0;
                subtotal += qty * unitCost * (1 + grossMargin / 100);
            }
        });

        const discount = parseFloat(document.getElementById('discount').value) || 0;
        const discountType = document.getElementById('discountType').value;
        const tax = parseFloat(document.getElementById('tax').value) || 0;

        let discountedSubtotal = subtotal;
        if (discountType === 'percent') {
            discountedSubtotal -= (subtotal * discount / 100);
        } else {
            discountedSubtotal -= discount;
        }

        const totalWithTax = discountedSubtotal + (discountedSubtotal * tax / 100);

        document.getElementById('subtotal').value = subtotal.toFixed(2);
        document.getElementById('finalSubtotal').value = totalWithTax.toFixed(2);
    }

    document.querySelectorAll('.add-on-select').forEach(select => {
        select.addEventListener('change', function () {
            const details = this.closest('tr').querySelector('.add-on-details');
            if (this.value) {
                details.classList.remove('d-none');
                const addOn = JSON.parse(this.value);
                this.closest('tr').querySelector('.add-on-price').value = addOn['Unit Cost'];
            } else {
                details.classList.add('d-none');
            }
            calculateSubtotal();
        });
    });

    document.querySelectorAll('.add-on-qty, .add-on-price, .add-on-gross-margin').forEach(input => {
        input.addEventListener('input', calculateSubtotal);
    });

    document.querySelectorAll('.dish-select').forEach(checkbox => {
        checkbox.addEventListener('change', calculateSubtotal);
    });

    document.getElementById('discount').addEventListener('input', calculateSubtotal);
    document.getElementById('discountType').addEventListener('change', calculateSubtotal);
    document.getElementById('tax').addEventListener('input', calculateSubtotal);

    document.getElementById('generateBill').addEventListener('click', async function () {
        const customerName = document.getElementById('customerName').value;
        const customerPhone = document.getElementById('customerPhone').value;
        const companyName = document.getElementById('companyName').value;
        const companyPhone = document.getElementById('companyPhone').value;
        const companyEmail = document.getElementById('companyEmail').value;
        const companyAddress = document.getElementById('companyAddress').value;
        const outlet = document.querySelector('input[name="outlet"]').value;

        const selectedDishes = Array.from(document.querySelectorAll('.dish-select:checked')).map(dish => {
            return {
                name: dish.closest('tr').querySelector('.dish-name').textContent,
                price: parseFloat(dish.closest('tr').querySelector('.dish-price').textContent.replace('₹', ''))
            };
        });

        const selectedAddOns = Array.from(document.querySelectorAll('.add-on-details:not(.d-none)')).map(details => {
            return {
                name: JSON.parse(details.closest('tr').querySelector('.add-on-select').value)['Product'],
                qty: parseFloat(details.querySelector('.add-on-qty').value) || 0,
                unit: details.querySelector('.add-on-unit').value,
                price: parseFloat(details.querySelector('.add-on-price').value) || 0
            };
        });

        const data = {
            outlet,
            customerName,
            customerPhone,
            companyName,
            companyPhone,
            companyEmail,
            companyAddress,
            dishes: selectedDishes,
            add_ons: selectedAddOns,
            discount: parseFloat(document.getElementById('discount').value) || 0,
            discountType: document.getElementById('discountType').value,
            tax: parseFloat(document.getElementById('tax').value) || 0,
            finalSubtotal: parseFloat(document.getElementById('finalSubtotal').value) || 0
        };

        const response = await fetch('/generate-bill', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.success) {
            document.getElementById('billLink').href = result.billLink;
            document.getElementById('billLink').style.display = 'block';
        } else {
            console.error('Error generating bill:', result.error);
        }
    });

    document.getElementById('generateKOT').addEventListener('click', async function () {
        const outlet = document.querySelector('input[name="outlet"]').value;
        const selectedDishes = Array.from(document.querySelectorAll('.dish-select:checked')).map(dish => {
            return {
                name: dish.closest('tr').querySelector('.dish-name').textContent
            };
        });

        const selectedAddOns = Array.from(document.querySelectorAll('.add-on-details:not(.d-none)')).map(details => {
            return {
                name: JSON.parse(details.closest('tr').querySelector('.add-on-select').value)['Product'],
                qty: parseFloat(details.querySelector('.add-on-qty').value) || 0,
                unit: details.querySelector('.add-on-unit').value
            };
        });

        const data = {
            outlet,
            dishes: selectedDishes,
            add_ons: selectedAddOns
        };

        const response = await fetch('/generate-kot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.success) {
            document.getElementById('kotLink').href = result.kotLink;
            document.getElementById('kotLink').style.display = 'block';
        } else {
            console.error('Error generating KOT:', result.error);
        }
    });

    // Fetch add-ons on page load
    fetch('/get-add-ons')
        .then(response => response.json())
        .then(data => {
            const addOnSelects = document.querySelectorAll('.add-on-select');
            addOnSelects.forEach(select => {
                data.add_ons.forEach(addOn => {
                    const option = document.createElement('option');
                    option.value = JSON.stringify(addOn);
                    option.textContent = addOn['Product'];
                    select.appendChild(option);
                });
            });
        })
        .catch(error => {
            console.error('Error fetching add-ons:', error);
        });
});
