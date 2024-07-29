document.addEventListener('DOMContentLoaded', () => {
    const searchBox = document.getElementById('search-box');
    const table = document.querySelector('table');

    searchBox.addEventListener('input', () => {
        const searchTerm = searchBox.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let match = false;
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchTerm)) {
                    match = true;
                }
            });
            row.style.display = match ? '' : 'none';
        });
    });
});

function setThreshold() {
    const thresholdGm = parseFloat(document.getElementById('threshold-input-gm').value);
    const thresholdPieces = parseFloat(document.getElementById('threshold-input-pieces').value);

    const rows = document.querySelectorAll('table tbody tr');

    rows.forEach(row => {
        const currentStockGm = parseFloat(row.cells[3].innerText) || 0;
        const currentStockPieces = parseFloat(row.cells[4].innerText) || 0;

        // Reset styles first
        row.cells[3].style.color = '';
        row.cells[3].style.fontWeight = '';
        row.cells[4].style.color = '';
        row.cells[4].style.fontWeight = '';

        if (!isNaN(thresholdGm) && currentStockGm < thresholdGm) {
            row.cells[3].style.color = 'red';
            row.cells[3].style.fontWeight = 'bold';
        }

        if (!isNaN(thresholdPieces) && currentStockPieces < thresholdPieces) {
            row.cells[4].style.color = 'red';
            row.cells[4].style.fontWeight = 'bold';
        }
    });
}

document.getElementById('order-ticket-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way
    const form = event.target;
    const formData = new FormData(form);
    const orderValues = {};

    formData.forEach((value, key) => {
        if (value !== '') {
            orderValues[key] = value;
        }
    });

    fetch(form.action, {
        method: form.method,
        body: JSON.stringify(orderValues),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              window.location.href = data.download_url;
          } else {
              alert('Failed to save order values.');
          }
      });
});
