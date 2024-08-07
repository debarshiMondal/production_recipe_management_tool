document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('time_frame').addEventListener('change', toggleDateRange);
    document.getElementById('see-data-form').addEventListener('submit', submitSeeDataForm);
    document.getElementById('find-product-cost-form').addEventListener('submit', submitFindProductCostForm);
});

function toggleDateRange() {
    var timeFrame = document.getElementById('time_frame').value;
    var dateRange = document.getElementById('date-range');
    if (timeFrame === 'Choose Date') {
        dateRange.style.display = 'block';
    } else {
        dateRange.style.display = 'none';
    }
}

function submitSeeDataForm(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);
    var action = '/sales-management/procurement-costs/raw-material-costs/get-data';

    fetch(action, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              if (data.table_html) {
                  document.getElementById('results-table').innerHTML = data.table_html;
                  document.getElementById('total-cost').innerText = `Subtotal: ${data.subtotal}`;
              } else {
                  document.getElementById('results-table').innerText = `Total Cost: ${data.total_cost}`;
              }
              document.getElementById('results').style.display = 'block';
          } else {
              alert('No data found');
          }
      });
}

function submitFindProductCostForm(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);
    var action = '/sales-management/procurement-costs/raw-material-costs/find-product-cost';

    fetch(action, {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              var productCosts = data.product_costs;
              var tableHtml = '<table class="table table-striped"><thead><tr><th>Product</th><th>Total Cost</th></tr></thead><tbody>';
              productCosts.forEach(function(cost) {
                  tableHtml += `<tr><td>${cost.Product}</td><td>${cost['Total Cost'].toFixed(2)}</td></tr>`;
              });
              tableHtml += '</tbody></table>';
              document.getElementById('product-cost-table').innerHTML = tableHtml;
              document.getElementById('product-cost-results').style.display = 'block';
          } else {
              alert('No data found for the specified products');
          }
      });
}
