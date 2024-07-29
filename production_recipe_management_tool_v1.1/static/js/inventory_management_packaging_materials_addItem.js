document.addEventListener('DOMContentLoaded', function () {
    const addProductButton = document.getElementById('addProductButton');
    const setThresholdsButton = document.getElementById('setThresholdsButton');
    const thresholdGmInput = document.getElementById('thresholdGm');
    const thresholdPiecesInput = document.getElementById('thresholdPieces');

    // Add Product Functionality
    addProductButton.addEventListener('click', function (event) {
        event.preventDefault();

        const product = {
            Product: document.getElementById('newProductName').value,
            Unit: document.getElementById('newProductUnit').value,
            'Unit Cost': parseFloat(document.getElementById('newProductUnitCost').value),
            'Current Stock (gm)': 0,
            'Current Stock (Pieces)': 0,
        };

        fetch('/add-packaging-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(product),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Product added successfully');
                location.reload();
            } else {
                alert('Error adding product');
            }
        })
        .catch(error => {
            console.error('Error adding product:', error);
        });
    });

    // Set Thresholds Functionality
    setThresholdsButton.addEventListener('click', function (event) {
        event.preventDefault();

        const thresholds = {
            thresholdGm: parseFloat(thresholdGmInput.value) || 0,
            thresholdPieces: parseFloat(thresholdPiecesInput.value) || 0,
        };

        fetch('/set-packaging-materials-thresholds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(thresholds),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Thresholds set successfully');
                location.reload();
            } else {
                console.error('Error setting thresholds');
            }
        })
        .catch(error => {
            console.error('Error setting thresholds:', error);
        });
    });
});
