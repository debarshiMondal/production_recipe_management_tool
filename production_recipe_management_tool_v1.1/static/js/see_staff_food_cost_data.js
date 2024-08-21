$(document).ready(function () {
    $('#see-data-form').submit(function (e) {
        e.preventDefault();

        var timeFrame = $('#time_frame').val();
        var startDate = $('#start_date').val();
        var endDate = $('#end_date').val();

        $.post('/sales-management/procurement-costs/staff-food-costs/get-data', {
            time_frame: timeFrame,
            start_date: startDate,
            end_date: endDate
        }, function (response) {
            if (response.success) {
                $('#results-table').html(response.table_html);
                $('#total-cost').text('Total Cost: ' + response.subtotal.toFixed(2));
                $('#results').show();
            } else {
                alert('No data found for the selected time frame');
            }
        });
    });

    $('#time_frame').change(function () {
        if ($(this).val() === 'Choose Date') {
            $('#date-range').show();
        } else {
            $('#date-range').hide();
        }
    });

    $('#find-product-cost-form').submit(function (e) {
        e.preventDefault();

        var products = $('#products').val();
        var startDate = $('#start_date_find').val();
        var endDate = $('#end_date_find').val();

        $.post('/sales-management/procurement-costs/staff-food-costs/find-product-cost', {
            products: products,
            start_date: startDate,
            end_date: endDate
        }, function (response) {
            if (response.success && response.product_costs.length > 0) {
                var tableHtml = '<table class="table table-striped"><thead><tr><th>Product</th><th>Total Cost</th></tr></thead><tbody>';
                response.product_costs.forEach(function (cost) {
                    tableHtml += `<tr><td>${cost.Product}</td><td>${cost['Total Cost'].toFixed(2)}</td></tr>`;
                });
                tableHtml += '</tbody></table>';
                $('#product-cost-table').html(tableHtml);
                $('#product-cost-results').show();
            } else {
                alert('No data found for the specified products');
            }
        });
    });
});
