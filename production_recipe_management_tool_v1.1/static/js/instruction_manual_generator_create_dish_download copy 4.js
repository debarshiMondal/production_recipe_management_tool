document.addEventListener('DOMContentLoaded', function() {
    const calculateSellingPriceButton = document.getElementById('calculateSellingPrice');
    const downloadIngredientsButton = document.getElementById('downloadIngredients');
    const dishNameInput = document.getElementById('dishNameInput'); // Make sure to get the input element

    calculateSellingPriceButton.addEventListener('click', function() {
        // Show the download button after calculating the price
        downloadIngredientsButton.style.display = 'inline-block';

        // Remove any previous click event listeners
        const newDownloadButton = downloadIngredientsButton.cloneNode(true);
        downloadIngredientsButton.parentNode.replaceChild(newDownloadButton, downloadIngredientsButton);

        // Add event listener to the new download button
        newDownloadButton.addEventListener('click', function() {
            const dishName = dishNameInput.value; // Get the latest dish name from the input

            // Generate and set download link for ingredients text file
            const ingredientsText = generateIngredientsText();
            const ingredientsBlob = new Blob([ingredientsText], { type: 'text/plain' });
            const ingredientsTextUrl = URL.createObjectURL(ingredientsBlob);

            // Generate and set download link for ingredients Excel file
            const excelUrl = generateExcelFile();

            // Download text file
            const textLink = document.createElement('a');
            textLink.href = ingredientsTextUrl;
            textLink.download = `${dishName}.txt`;
            textLink.click();

            // Download Excel file
            const excelLink = document.createElement('a');
            excelLink.href = excelUrl;
            excelLink.download = `${dishName}-OffSP-${document.getElementById('offlineSellingPrice').textContent.split('₹')[1]}OnSP-${document.getElementById('onlineSellingPrice').textContent.split('₹')[1]}.xlsx`;
            excelLink.click();
        });
    });

    function generateIngredientsText() {
        let ingredientsText = '';
        ingredientsText += "Main Products\n________________\n";
        // Collect ingredients data from selected main products
        const selectedProducts = document.querySelectorAll('#selected-products .selected-product');
        selectedProducts.forEach(product => {
            const name = product.querySelector('span').textContent.split(': ')[1];
            const qty = product.querySelector('input').value;
            const unit = product.querySelector('select').value;
            ingredientsText += `${name} ${qty} ${unit}\n`;
        });

        ingredientsText += "\nRaw Material\n________________\n";
        // Collect ingredients data from selected raw materials
        const selectedRawMaterials = document.querySelectorAll('#selected-raw-materials .selected-product');
        selectedRawMaterials.forEach(rawMaterial => {
            const name = rawMaterial.querySelector('span').textContent;
            const qty = rawMaterial.querySelector('input').value;
            const unit = rawMaterial.querySelector('select').value;
            ingredientsText += `${name} ${qty} ${unit}\n`;
        });

        ingredientsText += "\nPackaging Material\n_____________________\n";
        // Collect ingredients data from selected packaging materials
        const selectedPackagingMaterials = document.querySelectorAll('#selected-packaging-materials .selected-product');
        selectedPackagingMaterials.forEach(packagingMaterial => {
            const name = packagingMaterial.querySelector('span').textContent;
            const qty = packagingMaterial.querySelector('input').value;
            const unit = packagingMaterial.querySelector('select').value;
            ingredientsText += `${name} ${qty} ${unit}\n`;
        });

        return ingredientsText;
    }

    function generateExcelFile() {
        const XLSX = window.XLSX;
        const workbook = XLSX.utils.book_new();
        const worksheetData = [
            ["Product Category", "Product Name", "Qty", "Unit"],
        ];

        // Collect ingredients data from selected main products
        const selectedProducts = document.querySelectorAll('#selected-products .selected-product');
        selectedProducts.forEach(product => {
            const category = "Main Products";
            const name = product.querySelector('span').textContent.split(': ')[1];
            const qty = product.querySelector('input').value;
            const unit = product.querySelector('select').value;
            worksheetData.push([category, name, qty, unit]);
        });

        // Collect ingredients data from selected raw materials
        const selectedRawMaterials = document.querySelectorAll('#selected-raw-materials .selected-product');
        selectedRawMaterials.forEach(rawMaterial => {
            const category = "Raw Material";
            const name = rawMaterial.querySelector('span').textContent;
            const qty = rawMaterial.querySelector('input').value;
            const unit = rawMaterial.querySelector('select').value;
            worksheetData.push([category, name, qty, unit]);
        });

        // Collect ingredients data from selected packaging materials
        const selectedPackagingMaterials = document.querySelectorAll('#selected-packaging-materials .selected-product');
        selectedPackagingMaterials.forEach(packagingMaterial => {
            const category = "Packaging Material";
            const name = packagingMaterial.querySelector('span').textContent;
            const qty = packagingMaterial.querySelector('input').value;
            const unit = packagingMaterial.querySelector('select').value;
            worksheetData.push([category, name, qty, unit]);
        });

        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
        XLSX.utils.book_append_sheet(workbook, worksheet, "Ingredients");

        const excelBlob = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelBlob], { type: 'application/octet-stream' });
        return URL.createObjectURL(blob);
    }
});
