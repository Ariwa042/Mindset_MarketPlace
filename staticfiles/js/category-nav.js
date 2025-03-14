document.addEventListener('DOMContentLoaded', function() {
    // Category item click handling
    document.querySelectorAll('.category-item:not(.has-dropdown)').forEach(item => {
        item.addEventListener('click', function() {
            // Update active state
            document.querySelectorAll('.category-item').forEach(el => {
                el.classList.remove('active', 'animate__animated', 'animate__pulse');
            });
            this.classList.add('active', 'animate__animated', 'animate__pulse');
            
            // Filter products
            const category = this.dataset.category;
            filterProducts(category, null);
        });
    });

    // ...existing dropdown handling code...

    // Filter products function - integrates with Django
    function filterProducts(category, subcategory) {
        const url = `/products/filter/?category=${category}${subcategory ? `&subcategory=${subcategory}` : ''}`;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(url, {
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            document.getElementById('products-grid').innerHTML = html;
        })
        .catch(error => console.error('Error fetching products:', error));
    }
});
