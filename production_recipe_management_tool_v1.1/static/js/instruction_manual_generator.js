document.addEventListener('DOMContentLoaded', function() {
    const newCategoryNameInput = document.getElementById('newCategoryName');
    const createCategoryButton = document.getElementById('createCategoryBtn');
    const categoriesList = document.getElementById('categoriesList');
    const createDatabaseBtn = document.getElementById('createDatabaseBtn');

    createCategoryButton.addEventListener('click', function() {
        const newCategoryName = newCategoryNameInput.value.trim();
        if (newCategoryName) {
            fetch('/instruction-manual-generator/create-category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ category_name: newCategoryName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Clear the input field
                    newCategoryNameInput.value = '';
                    // Update the categories list
                    categoriesList.innerHTML = '';
                    data.categories.forEach(category => {
                        addCategoryToDOM(category);
                    });
                } else {
                    alert('Failed to create category');
                }
            });
        } else {
            alert('Please enter a category name');
        }
    });

    createDatabaseBtn.addEventListener('click', function() {
        fetch('/instruction-manual-generator/create-database', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Database refreshed successfully!');
            } else {
                alert('Failed to refresh the database');
            }
        });
    });

    function addCategoryToDOM(category) {
        const categoryItem = document.createElement('div');
        categoryItem.classList.add('category-item');
        categoryItem.innerHTML = `
            <span>${category}</span>
            <button class="delete-btn" data-category="${category}">Delete</button>
        `;
        categoriesList.appendChild(categoryItem);

        categoryItem.querySelector('.delete-btn').addEventListener('click', function() {
            const categoryToDelete = this.getAttribute('data-category');
            fetch('/instruction-manual-generator/delete-category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ category_name: categoryToDelete })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the categories list
                    categoriesList.innerHTML = '';
                    data.categories.forEach(category => {
                        addCategoryToDOM(category);
                    });
                } else {
                    alert('Failed to delete category');
                }
            });
        });
    }

    // Add event listeners to existing delete buttons
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const categoryToDelete = this.getAttribute('data-category');
            fetch('/instruction-manual-generator/delete-category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ category_name: categoryToDelete })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the categories list
                    categoriesList.innerHTML = '';
                    data.categories.forEach(category => {
                        addCategoryToDOM(category);
                    });
                } else {
                    alert('Failed to delete category');
                }
            });
        });
    });
});
