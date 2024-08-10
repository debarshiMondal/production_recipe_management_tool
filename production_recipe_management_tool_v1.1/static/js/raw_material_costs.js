document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('raw-material-costs-form').addEventListener('submit', submitForm);
    document.getElementById('update-cost-table').addEventListener('click', updateCostTable);
});

let currentTableData = [];

function submitForm(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);
    var action = '/sales-management/procurement-costs/raw-material-costs/submit';

    fetch(action, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              currentTableData = data.data;
              document.getElementById('results-table').innerHTML = data.table_html;
              document.getElementById('subtotal').innerText = data.subtotal.toFixed(2);
              document.getElementById('results').style.display = 'block';
          } else {
              alert('Failed to submit form');
          }
      });
}

function updateCostTable() {
    var date = document.getElementById('date').value;
    var action = '/sales-management/procurement-costs/raw-material-costs/update';

    fetch(action, {
        method: 'POST',
        body: JSON.stringify({ date: date, data: currentTableData }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              alert('Cost table updated successfully');
          } else {
              alert('Failed to update cost table');
          }
      });
}
