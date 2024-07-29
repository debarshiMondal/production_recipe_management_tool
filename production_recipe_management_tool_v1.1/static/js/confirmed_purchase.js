document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('shopping-list-form').addEventListener('submit', submitForm);
    document.getElementById('update-inventory-form').addEventListener('submit', submitUpdateForm);
});

function toggleDropdown() {
    var dropdown = document.getElementById('dropdown-container');
    dropdown.style.display = dropdown.style.display === 'none' ? 'flex' : 'none';
}

function showForm(materialType) {
    var formContainer = document.getElementById('form-container');
    var formInstructions = document.getElementById('form-instructions');
    var formAction = '/submit_' + materialType + '_form';

    var instructionsText = '';
    switch(materialType) {
        case 'raw_material':
            instructionsText = 'Please submit the raw material form in either .xlsx or .csv format:';
            break;
        case 'packaging_material':
            instructionsText = 'Please submit the packaging material form in either .xlsx or .csv format:';
            break;
        case 'outsourced_products':
            instructionsText = 'Please submit the outsourced products form in either .xlsx or .csv format:';
            break;
        case 'own_production':
            instructionsText = 'Please submit the own production form in either .xlsx or .csv format:';
            break;
    }

    formInstructions.innerText = instructionsText;
    var form = document.getElementById('shopping-list-form');
    form.action = formAction;
    formContainer.style.display = 'block';
}

function submitForm(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);
    var action = form.action;

    fetch(action, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              document.getElementById('results-table').innerHTML = data.table_html;
              document.getElementById('download-link').href = data.download_url;
              document.getElementById('results').style.display = 'block';
              if (data.missing_products.length > 0) {
                  var missingProductsList = document.getElementById('missing-products-list');
                  missingProductsList.innerHTML = '';
                  data.missing_products.forEach(product => {
                      var li = document.createElement('li');
                      li.textContent = product;
                      missingProductsList.appendChild(li);
                  });
                  document.getElementById('missing-products').style.display = 'block';
              }
          } else {
              alert('Failed to submit form');
          }
      });
}

function toggleUpdateDropdown() {
    var dropdown = document.getElementById('update-dropdown-container');
    dropdown.style.display = dropdown.style.display === 'none' ? 'flex' : 'none';
}

function showUpdateForm(materialType) {
    var formContainer = document.getElementById('update-form-container');
    var formInstructions = document.getElementById('update-form-instructions');
    var formAction = '/update_' + materialType + '_inventory';

    var instructionsText = '';
    switch(materialType) {
        case 'raw_material':
            instructionsText = 'Please submit the raw material form in either .xlsx or .csv format:';
            break;
        case 'packaging_material':
            instructionsText = 'Please submit the packaging material form in either .xlsx or .csv format:';
            break;
        case 'outsourced_products':
            instructionsText = 'Please submit the outsourced products form in either .xlsx or .csv format:';
            break;
        case 'own_production':
            instructionsText = 'Please submit the own production form in either .xlsx or .csv format:';
            break;
    }

    formInstructions.innerText = instructionsText;
    var form = document.getElementById('update-inventory-form');
    form.action = formAction;
    formContainer.style.display = 'block';
}

function submitUpdateForm(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);
    var action = form.action;

    fetch(action, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              document.getElementById('update-results-table').innerHTML = data.table_html;
              document.getElementById('update-results').style.display = 'block';
          } else {
              alert('Failed to submit form');
          }
      });
}

function updateInventory() {
    fetch('/update_inventory', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              alert('Inventory updated successfully');
          } else {
              alert('Failed to update inventory');
          }
      });
}
