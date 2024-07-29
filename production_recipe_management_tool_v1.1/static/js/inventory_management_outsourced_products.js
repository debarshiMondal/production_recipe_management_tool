document.addEventListener('DOMContentLoaded', function () {
    const searchBox = document.getElementById('searchBox');
    const searchButton = document.getElementById('searchButton');
    const clearAllButton = document.getElementById('clearAllButton');
    const saveButtonTop = document.getElementById('saveButtonTop');
    const saveButtonBottom = document.getElementById('saveButtonBottom');
    const productTableBody = document.getElementById('productTableBody');
    const setThresholdsButton = document.getElementById('setThresholdsButton');
    const thresholdGmInput = document.getElementById('thresholdGm');
    const thresholdPiecesInput = document.getElementById('thresholdPieces');

    let productsData = [];
    let thresholdGm = null;
    let thresholdPieces = null;

    // Function to populate the table with products
    function populateTable(products) {
        console.log("Populating table with products:", products);  // Debugging: Log the products data
        productTableBody.innerHTML = '';
        products.forEach((product, index) => {
            const row = document.createElement('tr');
            row.setAttribute('data-id', index + 1);

            const currentStockGm = product['Current Stock (gm)'] !== null ? product['Current Stock (gm)'] : 0;
            const currentStockPieces = product['Current Stock (Pieces)'] !== null ? product['Current Stock (Pieces)'] : 0;

            const gmClass = thresholdGm !== null && currentStockGm < thresholdGm ? 'threshold-exceeded' : '';
            const piecesClass = thresholdPieces !== null && currentStockPieces < thresholdPieces ? 'threshold-exceeded' : '';

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${product.Product}</td>
                <td>${product.Unit}</td>
                <td>${product['Unit Cost']}</td>
                <td class="current-stock-gm ${gmClass}">${currentStockGm}</td>
                <td class="current-stock-pieces ${piecesClass}">${currentStockPieces}</td>
                <td>
                    <input type="number" class="update-box">
                    <button class="update-btn">Update</button>
                </td>
                <td><button class="clear-btn">Clear</button></td>
                <td>${product.Vendor}</td>
                <td>${product['Vendor Phone Number'] !== null ? product['Vendor Phone Number'] : ''}</td>
            `;
            productTableBody.appendChild(row);
        });
    }

    // Fetch the initial data from the server
    fetch('/outsourced-products-dashboard', {
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("Received data:", data);  // Debugging: Log the received data
        productsData = data.products;
        populateTable(productsData);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

    // Function to filter products based on search query
    function filterProducts(query, products) {
        return products.filter(product => product.Product.toLowerCase().includes(query.toLowerCase()));
    }

    // Function to clear all stocks
    function clearAllStocks() {
        productsData.forEach(product => {
            product['Current Stock (gm)'] = 0;
            product['Current Stock (Pieces)'] = 0;
        });
        populateTable(productsData);
    }

    // Function to handle search
    function searchProducts() {
        const query = searchBox.value.toLowerCase();
        const filteredProducts = filterProducts(query, productsData);
        populateTable(filteredProducts);
    }

    // Event listeners
    searchButton.addEventListener('click', searchProducts);
    clearAllButton.addEventListener('click', clearAllStocks);
    saveButtonTop.addEventListener('click', saveUpdates);
    saveButtonBottom.addEventListener('click', saveUpdates);

    productTableBody.addEventListener('click', (event) => {
        if (event.target.classList.contains('update-btn')) {
            const row = event.target.closest('tr');
            const updateValue = parseFloat(row.querySelector('.update-box').value);
            const currentStockGmCell = row.querySelector('.current-stock-gm');
            const currentStockPiecesCell = row.querySelector('.current-stock-pieces');
            let currentStockGm = parseFloat(currentStockGmCell.textContent);
            let currentStockPieces = parseFloat(currentStockPiecesCell.textContent);

            if (!isNaN(updateValue)) {
                if (productsData[row.getAttribute('data-id') - 1].Unit === 'gm') {
                    currentStockGm += updateValue;
                    currentStockGmCell.textContent = currentStockGm;
                    productsData[row.getAttribute('data-id') - 1]['Current Stock (gm)'] = currentStockGm;
                } else {
                    currentStockPieces += updateValue;
                    currentStockPiecesCell.textContent = currentStockPieces;
                    productsData[row.getAttribute('data-id') - 1]['Current Stock (Pieces)'] = currentStockPieces;
                }
            }
        }

        if (event.target.classList.contains('clear-btn')) {
            const row = event.target.closest('tr');
            const currentStockGmCell = row.querySelector('.current-stock-gm');
            const currentStockPiecesCell = row.querySelector('.current-stock-pieces');

            currentStockGmCell.textContent = 0;
            currentStockPiecesCell.textContent = 0;

            const index = row.getAttribute('data-id') - 1;
            productsData[index]['Current Stock (gm)'] = 0;
            productsData[index]['Current Stock (Pieces)'] = 0;
        }
    });

    function saveUpdates() {
        fetch('/update-outsourced-products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ products: productsData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Data saved successfully');
            } else {
                alert('Error saving data');
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }

    // Function to set thresholds
    setThresholdsButton.addEventListener('click', function() {
        thresholdGm = parseFloat(thresholdGmInput.value);
        thresholdPieces = parseFloat(thresholdPiecesInput.value);

        if (isNaN(thresholdGm)) thresholdGm = null;
        if (isNaN(thresholdPieces)) thresholdPieces = null;

        fetch('/set-thresholds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ thresholdGm: thresholdGm, thresholdPieces: thresholdPieces })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                productsData = data.products;
                alert('Thresholds set successfully');
                populateTable(productsData);
            } else {
                alert('Error setting thresholds');
            }
        })
        .catch(error => {
            console.error('Error setting thresholds:', error);
        });
    });
});
