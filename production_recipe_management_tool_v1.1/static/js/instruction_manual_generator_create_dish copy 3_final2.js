document.addEventListener('DOMContentLoaded', function() {
    const categoryButtons = document.querySelectorAll('.category-button');
    const selectedProductsContainer = document.getElementById('selected-products');
    const energyTypeSelect = document.getElementById('energyType');
    const energyFieldsContainer = document.getElementById('energy-fields');
    const rawMaterialDropdown = document.getElementById('raw-materials-dropdown');
    const selectedRawMaterialsContainer = document.getElementById('selected-raw-materials');
    const packagingMaterialDropdown = document.getElementById('packaging-material-dropdown');
    const selectedPackagingMaterialsContainer = document.getElementById('selected-packaging-materials');

    const packagingMaterialBeforePM = document.getElementById('packagingMaterialBeforePM');
    const packagingMaterialAfterPM = document.getElementById('packagingMaterialAfterPM');
    const packagingMaterialAfterOSP = document.getElementById('packagingMaterialAfterOSP');
    const profitMarginInput = document.getElementById('profitMargin');
    const onlineMarginInput = document.getElementById('onlineMargin');
    const adDiscountCoverageInput = document.getElementById('adDiscountCoverage');
    const calculateSellingPriceButton = document.getElementById('calculateSellingPrice');
    const offlineSellingPriceDisplay = document.getElementById('offlineSellingPrice');
    const onlineSellingPriceDisplay = document.getElementById('onlineSellingPrice');

    // Fetch raw materials and populate the dropdown
    fetch('/instruction-manual-generator/get-raw-materials')
        .then(response => response.json())
        .then(data => {
            data.rawMaterials.forEach(rawMaterial => {
                const item = document.createElement('a');
                item.classList.add('dropdown-item');
                item.textContent = rawMaterial;
                item.addEventListener('click', () => addSelectedRawMaterial(rawMaterial)); // Add click event
                rawMaterialDropdown.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error fetching raw materials:', error);
        });

    // Fetch packaging materials and populate the dropdown
    fetch('/instruction-manual-generator/get-packaging-materials')
        .then(response => response.json())
        .then(data => {
            data.packagingMaterials.forEach(packagingMaterial => {
                const item = document.createElement('a');
                item.classList.add('dropdown-item');
                item.textContent = packagingMaterial;
                item.addEventListener('click', () => addSelectedPackagingMaterial(packagingMaterial)); // Add click event
                packagingMaterialDropdown.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error fetching packaging materials:', error);
        });

    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.textContent.trim();
            const dropdownMenu = this.nextElementSibling;

            console.log(`Fetching ingredients for category: ${category}`); // Debugging line

            // Clear previous items
            dropdownMenu.innerHTML = '';

            fetch(`/instruction-manual-generator/get-ingredients?category=${category}`)
                .then(response => response.json())
                .then(data => {
                    console.log(`Ingredients for category ${category}:`, data.ingredients); // Debugging line

                    if (data.ingredients.length === 0) {
                        const noItems = document.createElement('a');
                        noItems.classList.add('dropdown-item');
                        noItems.textContent = 'No items found';
                        dropdownMenu.appendChild(noItems);
                    } else {
                        data.ingredients.forEach(ingredient => {
                            const item = document.createElement('a');
                            item.classList.add('dropdown-item');
                            item.textContent = ingredient;
                            item.addEventListener('click', () => addSelectedProduct(category, ingredient)); // Add click event
                            dropdownMenu.appendChild(item);
                        });
                    }

                    console.log(`Dropdown menu structure for ${category}:`, dropdownMenu); // Debugging line

                    // Re-initialize Bootstrap dropdown
                    $(dropdownMenu).dropdown('update');
                })
                .catch(error => {
                    console.error(`Error fetching ingredients for category ${category}:`, error);
                    const errorItem = document.createElement('a');
                    errorItem.classList.add('dropdown-item');
                    errorItem.textContent = 'Error loading items';
                    dropdownMenu.appendChild(errorItem);
                });
        });
    });

    function addSelectedProduct(category, product) {
        // Ensure the URL is correctly formatted
        fetch(`/instruction-manual-generator/get-unit-cost?product=${encodeURIComponent(product)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching unit cost:', data.error);
                    return;
                }

                const unitCost = data.unitCost;

                const productContainer = document.createElement('div');
                productContainer.classList.add('selected-product', 'd-flex', 'align-items-center', 'mb-2');

                const productLabel = document.createElement('span');
                productLabel.textContent = `${category}: ${product}`;
                productLabel.classList.add('mr-2');

                const qtyInput = document.createElement('input');
                qtyInput.type = 'number';
                qtyInput.placeholder = 'Qty';
                qtyInput.classList.add('form-control', 'd-inline-block', 'w-auto', 'mx-2');
                qtyInput.addEventListener('input', updateTotalCost); // Add event listener to update total cost

                const unitSelect = document.createElement('select');
                unitSelect.classList.add('form-control', 'd-inline-block', 'w-auto', 'mx-2');
                const optionGm = document.createElement('option');
                optionGm.value = 'gm';
                optionGm.textContent = 'gm';
                const optionPieces = document.createElement('option');
                optionPieces.value = 'pieces';
                optionPieces.textContent = 'pieces';
                unitSelect.appendChild(optionGm);
                unitSelect.appendChild(optionPieces);

                const costLabel = document.createElement('span');
                costLabel.textContent = `Unit Cost: ₹${unitCost}`;
                costLabel.classList.add('mr-2', 'unit-cost');

                const removeButton = document.createElement('button');
                removeButton.classList.add('btn', 'btn-danger', 'ml-2');
                removeButton.textContent = 'Remove';
                removeButton.addEventListener('click', function() {
                    productContainer.remove();
                    updateTotalCost(); // Update total cost when product is removed
                });

                productContainer.appendChild(productLabel);
                productContainer.appendChild(qtyInput);
                productContainer.appendChild(unitSelect);
                productContainer.appendChild(costLabel);
                productContainer.appendChild(removeButton);

                selectedProductsContainer.appendChild(productContainer);

                updateTotalCost(); // Update total cost when a new product is added
            })
            .catch(error => {
                console.error('Error fetching unit cost:', error);
            });
    }

    function addSelectedRawMaterial(rawMaterial) {
        // Ensure the URL is correctly formatted
        fetch(`/instruction-manual-generator/get-unit-cost?product=${encodeURIComponent(rawMaterial)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching unit cost:', data.error);
                    return;
                }

                const unitCost = data.unitCost;

                const rawMaterialContainer = document.createElement('div');
                rawMaterialContainer.classList.add('selected-product', 'd-flex', 'align-items-center', 'mb-2');

                const rawMaterialLabel = document.createElement('span');
                rawMaterialLabel.textContent = rawMaterial;
                rawMaterialLabel.classList.add('mr-2');

                const qtyInput = document.createElement('input');
                qtyInput.type = 'number';
                qtyInput.placeholder = 'Qty';
                qtyInput.classList.add('form-control', 'd-inline-block', 'w-auto', 'mx-2');
                qtyInput.addEventListener('input', updateTotalCost); // Add event listener to update total cost

                const unitSelect = document.createElement('select');
                unitSelect.classList.add('form-control', 'd-inline-block', 'w-auto', 'mx-2');
                const optionGm = document.createElement('option');
                optionGm.value = 'gm';
                optionGm.textContent = 'gm';
                const optionPieces = document.createElement('option');
                optionPieces.value = 'pieces';
                optionPieces.textContent = 'pieces';
                unitSelect.appendChild(optionGm);
                unitSelect.appendChild(optionPieces);

                const costLabel = document.createElement('span');
                costLabel.textContent = `Unit Cost: ₹${unitCost}`;
                costLabel.classList.add('mr-2', 'unit-cost');

                const removeButton = document.createElement('button');
                removeButton.classList.add('btn', 'btn-danger', 'ml-2');
                removeButton.textContent = 'Remove';
                removeButton.addEventListener('click', function() {
                    rawMaterialContainer.remove();
                    updateTotalCost(); // Update total cost when raw material is removed
                });

                rawMaterialContainer.appendChild(rawMaterialLabel);
                rawMaterialContainer.appendChild(qtyInput);
                rawMaterialContainer.appendChild(unitSelect);
                rawMaterialContainer.appendChild(costLabel);
                rawMaterialContainer.appendChild(removeButton);

                selectedRawMaterialsContainer.appendChild(rawMaterialContainer);

                updateTotalCost(); // Update total cost when a new raw material is added
            })
            .catch(error => {
                console.error('Error fetching unit cost:', error);
            });
    }

    function addSelectedPackagingMaterial(packagingMaterial) {
        // Ensure the URL is correctly formatted
        fetch(`/instruction-manual-generator/get-unit-cost?product=${encodeURIComponent(packagingMaterial)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching unit cost:', data.error);
                    return;
                }

                const unitCost = data.unitCost;

                const packagingMaterialContainer = document.createElement('div');
                packagingMaterialContainer.classList.add('selected-product', 'd-flex', 'align-items-center', 'mb-2');

                const packagingMaterialLabel = document.createElement('span');
                packagingMaterialLabel.textContent = packagingMaterial;
                packagingMaterialLabel.classList.add('mr-2');

                const qtyInput = document.createElement('input');
                qtyInput.type = 'number';
                qtyInput.placeholder = 'Qty';
                qtyInput.classList.add('form-control', 'd-inline-block', 'w-auto', 'mx-2');

                const unitSelect = document.createElement('select');
                unitSelect.classList.add('form-control', 'd-inline-block', 'w-auto', 'mx-2');
                const optionGm = document.createElement('option');
                optionGm.value = 'gm';
                optionGm.textContent = 'gm';
                const optionPieces = document.createElement('option');
                optionPieces.value = 'pieces';
                optionPieces.textContent = 'pieces';
                unitSelect.appendChild(optionGm);
                unitSelect.appendChild(optionPieces);

                const costLabel = document.createElement('span');
                costLabel.textContent = `Unit Cost: ₹${unitCost}`;
                costLabel.classList.add('mr-2', 'unit-cost');

                const removeButton = document.createElement('button');
                removeButton.classList.add('btn', 'btn-danger', 'ml-2');
                removeButton.textContent = 'Remove';
                removeButton.addEventListener('click', function() {
                    packagingMaterialContainer.remove();
                });

                packagingMaterialContainer.appendChild(packagingMaterialLabel);
                packagingMaterialContainer.appendChild(qtyInput);
                packagingMaterialContainer.appendChild(unitSelect);
                packagingMaterialContainer.appendChild(costLabel);
                packagingMaterialContainer.appendChild(removeButton);

                selectedPackagingMaterialsContainer.appendChild(packagingMaterialContainer);
            })
            .catch(error => {
                console.error('Error fetching unit cost:', error);
            });
    }

    energyTypeSelect.addEventListener('change', function() {
        const selectedType = energyTypeSelect.value;
        energyFieldsContainer.innerHTML = '';
    
        if (selectedType === 'Electricity') {
            addElectricityFields();
        } else if (selectedType === 'Gas') {
            addGasFields();
        }
        updateEnergyCost(); // Update total cost when energy type changes
    });

    function addElectricityFields() {
        energyFieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="power">Power (kW)</label>
                <input type="number" id="power" class="form-control" oninput="updateEnergyCost()">
            </div>
            <div class="form-group">
                <label for="time">Time (mins)</label>
                <input type="number" id="time" class="form-control" oninput="updateEnergyCost()">
            </div>
            <div class="form-group">
                <label for="cost-per-kwh">Cost per kWh</label>
                <input type="number" id="cost-per-kwh" class="form-control" oninput="updateEnergyCost()">
            </div>
        `;
    }

    function addGasFields() {
        energyFieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="power">Power (kW)</label>
                <input type="number" id="power" class="form-control" oninput="updateEnergyCost()">
            </div>
            <div class="form-group">
                <label for="time">Time (mins)</label>
                <input type="number" id="time" class="form-control" oninput="updateEnergyCost()">
            </div>
            <div class="form-group">
                <label for="cost-of-gas-cylinder">Cost of Gas Cylinder</label>
                <input type="number" id="cost-of-gas-cylinder" class="form-control" oninput="updateEnergyCost()">
            </div>
            <div class="form-group">
                <label for="cylinder-type">Cylinder Type (Kg)</label>
                <input type="number" id="cylinder-type" class="form-control" oninput="updateEnergyCost()">
            </div>
        `;
    }

    // Add event listener to the calculate selling price button. Here Profir Margin is Gross Margin.
    calculateSellingPriceButton.addEventListener('click', calculateSellingPrice);

    function calculateSellingPrice() {
        const totalFoodProductionCost = parseFloat(document.getElementById('total-cost').textContent.split('₹')[1]) || 0;
        let packagingMaterialCost = 0;

        // Calculate the cost of selected packaging materials. Here Profir Margin is Gross Margin.
        const selectedPackagingMaterials = document.querySelectorAll('#selected-packaging-materials .selected-product');
        selectedPackagingMaterials.forEach(packagingMaterial => {
            const qty = parseFloat(packagingMaterial.querySelector('input').value) || 0;
            const unitCost = parseFloat(packagingMaterial.querySelector('.unit-cost').textContent.split('₹')[1]) || 0;
            packagingMaterialCost += qty * unitCost;
        });

        const profitMargin = parseFloat(profitMarginInput.value) || 0;
        const onlineMargin = parseFloat(onlineMarginInput.value) || 0;
        const adDiscountCoverage = parseFloat(adDiscountCoverageInput.value) || 0;

        let offlineSellingPrice;
        let onlineSellingPrice;
        //Here Profir Margin is Gross Margin.
        if (packagingMaterialBeforePM.checked) {
            offlineSellingPrice = (totalFoodProductionCost + packagingMaterialCost) / (1 - profitMargin / 100);
            onlineSellingPrice = offlineSellingPrice / (1 - onlineMargin / 100) + adDiscountCoverage;
        } else if (packagingMaterialAfterPM.checked) {
            //Here Profir Margin is Gross Margin.
            offlineSellingPrice = (totalFoodProductionCost / (1 - profitMargin / 100) + packagingMaterialCost);
            onlineSellingPrice = offlineSellingPrice / (1 - onlineMargin / 100)  + adDiscountCoverage;
        } else if (packagingMaterialAfterOSP.checked) {
            //Here Profir Margin is Gross Margin.
            offlineSellingPrice = ((totalFoodProductionCost / (1 - profitMargin / 100)) + packagingMaterialCost);
            onlineSellingPrice = ((offlineSellingPrice-packagingMaterialCost) / (1 - onlineMargin / 100) + adDiscountCoverage + packagingMaterialCost);
        }
        offlineSellingPriceDisplay.textContent = `₹${offlineSellingPrice.toFixed(2)}`;
        onlineSellingPriceDisplay.textContent = `₹${onlineSellingPrice.toFixed(2)}`;
    }
});

function updateEnergyCost() {
    console.log('updateEnergyCost called');
    let energyCost = 0;
    const selectedType = document.getElementById('energyType').value;
    if (selectedType === 'Electricity') {
        const power = parseFloat(document.getElementById('power').value) || 0;
        const time = parseFloat(document.getElementById('time').value) || 0;
        const costPerKwh = parseFloat(document.getElementById('cost-per-kwh').value) || 0;
        console.log({ power, time, costPerKwh });
        energyCost = power * (time / 60) * costPerKwh;
    } else if (selectedType === 'Gas') {
        const power = parseFloat(document.getElementById('power').value) || 0;
        const time = parseFloat(document.getElementById('time').value) || 0;
        const costOfGasCylinder = parseFloat(document.getElementById('cost-of-gas-cylinder').value) || 0;
        const cylinderType = parseFloat(document.getElementById('cylinder-type').value) || 0;
        energyCost = power * (time / 60) * 0.08 * (costOfGasCylinder / cylinderType);
    }

    // Display energy cost
    const energyCostContainer = document.getElementById('energy-cost-container');
    energyCostContainer.innerHTML = `
        <div class="form-group d-flex align-items-center">
            <span>Energy Cost: ₹${energyCost.toFixed(2)}</span>
            <button class="btn btn-danger ml-2" onclick="removeEnergyCost()">Remove</button>
        </div>
    `;

    updateTotalCost();
}

function updateTotalCost() {
    let totalCost = 0;

    // Calculate cost of selected products
    const selectedProducts = document.querySelectorAll('#selected-products .selected-product');
    selectedProducts.forEach(product => {
        const qty = parseFloat(product.querySelector('input').value) || 0;
        const unitCost = parseFloat(product.querySelector('.unit-cost').textContent.split('₹')[1]) || 0;
        totalCost += qty * unitCost;
    });

    // Calculate cost of selected raw materials
    const selectedRawMaterials = document.querySelectorAll('#selected-raw-materials .selected-product');
    selectedRawMaterials.forEach(rawMaterial => {
        const qty = parseFloat(rawMaterial.querySelector('input').value) || 0;
        const unitCost = parseFloat(rawMaterial.querySelector('.unit-cost').textContent.split('₹')[1]) || 0;
        totalCost += qty * unitCost;
    });

    // Add energy cost to total cost
    const energyCost = parseFloat(document.querySelector('#energy-cost-container span')?.textContent.split('₹')[1]) || 0;
    totalCost += energyCost;

    // Update the total cost display
    const totalCostDisplay = document.getElementById('total-cost');
    totalCostDisplay.textContent = `₹${totalCost.toFixed(2)}`;
}

function removeEnergyCost() {
    const energyTypeSelect = document.getElementById('energyType');
    energyTypeSelect.value = "";
    const energyFieldsContainer = document.getElementById('energy-fields');
    energyFieldsContainer.innerHTML = "";
    const energyCostContainer = document.getElementById('energy-cost-container');
    energyCostContainer.innerHTML = "";
    updateTotalCost();
}
