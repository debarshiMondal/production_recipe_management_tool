document.addEventListener('DOMContentLoaded', function() {
    const categoryButtons = document.querySelectorAll('.dropdown-toggle');

    categoryButtons.forEach(button => {
        console.log('Attaching event listener to button:', button.textContent.trim());
        button.addEventListener('click', function() {
            const category = this.textContent.trim();
            const dropdownMenu = this.nextElementSibling;

            // Clear previous items
            dropdownMenu.innerHTML = '';

            console.log(`Fetching ingredients for category: ${category}`);
            fetch(`/instruction-manual-generator/get-ingredients?category=${category}`)
                .then(response => {
                    console.log(`Received response for category: ${category}`);
                    return response.json();
                })
                .then(data => {
                    console.log(`Ingredients for category ${category}:`, data.ingredients);

                    if (data.ingredients.length === 0) {
                        const noItems = document.createElement('a');
                        noItems.classList.add('dropdown-item');
                        noItems.textContent = 'No items found';
                        dropdownMenu.appendChild(noItems);
                    } else {
                        data.ingredients.forEach(ingredient => {
                            const item = document.createElement('a');
                            item.classList.add('dropdown-item');
                            item.href = '#'; // Add this line to make the items clickable
                            item.textContent = ingredient;
                            dropdownMenu.appendChild(item);
                        });
                    }
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
});
