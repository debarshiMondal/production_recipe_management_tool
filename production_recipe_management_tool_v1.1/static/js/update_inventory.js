document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('update-inventory-form').addEventListener('submit', submitUpdateForm);
});

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
    var updates = [];
    var rows = document.querySelectorAll('#update-results-table tr');
    rows.forEach(row => {
        var cells = row.querySelectorAll('td');
        if (cells.length > 0) {
            var update = {
                'Product': cells[0].textContent,
                'Quantity (Gm)': cells[2].textContent,
                'Quantity (Pieces)': cells[3].textContent
            };
            updates.push(update);
        }
    });

    fetch('/update_inventory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'material_type': 'packaging_material', 'updates': updates })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              alert('Inventory updated successfully');
          } else {
              alert('Failed to update inventory');
          }
      });
}
