document.addEventListener('DOMContentLoaded', function() {
    const selectRecipeBox = document.getElementById('selectRecipeBox');
    const selectRecipe = document.getElementById('selectRecipe');
    const selectUnitBox = document.getElementById('selectUnitBox');
    const unit = document.getElementById('unit');
    const quantityBox = document.getElementById('quantityBox');
    const quantity = document.getElementById('quantity');
    const addToPalette = document.getElementById('addToPalette');
    const palette = document.getElementById('palette');
    const costValue = document.getElementById('costValue');
    const generateShoppingList = document.getElementById('generateShoppingList');
    const downloadLinks = document.getElementById('downloadLinks');
    const warningMessage = document.createElement('div');

    let totalCost = 0;
    let recipesInPalette = [];

    warningMessage.style.color = 'red';
    warningMessage.style.display = 'none';
    warningMessage.textContent = 'Please fill out all mandatory fields.';
    document.querySelector('.form-section').appendChild(warningMessage);

    // Toggle dropdown on click
    selectRecipeBox.addEventListener('click', function() {
        selectRecipe.style.display = selectRecipe.style.display === 'block' ? 'none' : 'block';
        selectRecipeBox.classList.toggle('active');
    });

    selectUnitBox.addEventListener('click', function() {
        unit.style.display = unit.style.display === 'block' ? 'none' : 'block';
        selectUnitBox.classList.toggle('active');
    });

    quantityBox.addEventListener('click', function() {
        quantityBox.style.display = 'none';
        quantity.style.display = 'block';
        quantity.focus();
    });

    quantity.addEventListener('blur', function() {
        if (!quantity.value) {
            quantity.style.display = 'none';
            quantityBox.style.display = 'block';
        }
    });

    // Update box text and hide dropdown on selection
    selectRecipe.addEventListener('change', function() {
        selectRecipeBox.innerHTML = selectRecipe.options[selectRecipe.selectedIndex].text;
        selectRecipe.style.display = 'none';
        selectRecipeBox.classList.remove('active');
    });

    unit.addEventListener('change', function() {
        selectUnitBox.innerHTML = unit.options[unit.selectedIndex].text;
        unit.style.display = 'none';
        selectUnitBox.classList.remove('active');
    });

    addToPalette.addEventListener('click', function() {
        const selectedUnit = unit.value;
        const selectedQuantity = parseFloat(quantity.value);
        const recipeName = selectRecipe.options[selectRecipe.selectedIndex].text;
        const recipeFilename = selectRecipe.value;

        // Check if all fields are filled
        if (!recipeFilename || !selectedUnit || !selectedQuantity) {
            warningMessage.style.display = 'block';
            return;
        } else {
            warningMessage.style.display = 'none';
        }

        // Calculate subtotal for the selected item
        fetch(`/get-unit-cost?filename=${recipeFilename}`)
            .then(response => response.json())
            .then(data => {
                const unitCost = data.unit_cost;
                const subtotal = unitCost * selectedQuantity;

                // Update total cost
                totalCost += subtotal;
                costValue.textContent = totalCost.toFixed(2);

                // Add item to palette
                const paletteRow = document.createElement('div');
                paletteRow.classList.add('palette-row');
                paletteRow.innerHTML = `
                    <div class="palette-item">${recipeName}</div>
                    <div class="palette-quantity">${selectedQuantity} ${selectedUnit}</div>
                    <div class="palette-subtotal">${subtotal.toFixed(2)}</div>
                    <div class="palette-action">
                        <a href="#" class="scaled-recipe-link">Download</a>
                        <button class="delete-btn">Delete</button>
                    </div>
                `;
                palette.appendChild(paletteRow);

                const recipeData = {
                    filename: recipeFilename,
                    unit: selectedUnit,
                    quantity: selectedQuantity,
                    item: recipeName,
                    subtotal: subtotal
                };

                recipesInPalette.push(recipeData);

                // Add event listener for scaled recipe link
                paletteRow.querySelector('.scaled-recipe-link').addEventListener('click', function(event) {
                    event.preventDefault();
                    fetch('/recipe-management/generate-scaled-recipe', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ recipes: [recipeData] }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.downloadLink) {
                            const a = document.createElement('a');
                            a.href = data.downloadLink;
                            a.download = data.downloadLink.split('/').pop();
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                        } else {
                            alert('Error generating scaled recipe');
                        }
                    });
                });

                // Add event listener for delete button
                paletteRow.querySelector('.delete-btn').addEventListener('click', function() {
                    palette.removeChild(paletteRow);
                    totalCost -= subtotal;
                    costValue.textContent = totalCost.toFixed(2);
                    recipesInPalette = recipesInPalette.filter(recipe => recipe.filename !== recipeFilename);
                });
            });
    });

    generateShoppingList.addEventListener('click', function() {
        // Clear existing download links
        downloadLinks.innerHTML = '';

        fetch('/recipe-management/generate-shopping-list', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ recipes: recipesInPalette }),
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const date = new Date().toISOString().slice(0, 10); // Get current date in YYYY-MM-DD format
            const shoppingListFilename = `shopping_list_${date}.xlsx`;

            const a = document.createElement('a');
            a.href = url;
            a.download = shoppingListFilename;
            a.textContent = 'Download Shopping List';
            downloadLinks.appendChild(a);
        });

        fetch('/recipe-management/generate-estimation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ recipes: recipesInPalette }),
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const date = new Date().toISOString().slice(0, 10); // Get current date in YYYY-MM-DD format
            const estimationFilename = `estimation_of_production_${date}.pdf`;

            const a = document.createElement('a');
            a.href = url;
            a.download = estimationFilename;
            a.textContent = 'Estimation of Production';
            downloadLinks.appendChild(a);
        });

        // Show download links
        downloadLinks.style.display = 'block';
    });
});
