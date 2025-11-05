document.addEventListener('DOMContentLoaded', function() {
    // Close alert messages
    const closeButtons = document.querySelectorAll('.alert .close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // Handle form submission and validation
    const urlForm = document.getElementById('urlForm');
    if (urlForm) {
        urlForm.addEventListener('submit', function(e) {
            const urlInput = this.querySelector('input[type="url"]');
            
            if (!isValidURL(urlInput.value)) {
                e.preventDefault();
                showError('Please enter a valid URL including http:// or https://');
                return;
            }

            // Show loading spinner
            document.getElementById('loading').classList.remove('hidden');
            
            // Disable submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            }
        });
    }

    // Results page functionality
    const searchInput = document.getElementById('searchInput');
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTableRows();
        });
    }

    if (filterButtons) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                filterTableRows();
            });
        });
    }

    // Helper Functions
    function isValidURL(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="close-btn">&times;</button>
        `;

        const form = document.querySelector('.analysis-form');
        form.insertBefore(errorDiv, form.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);

        // Add click handler for close button
        errorDiv.querySelector('.close-btn').addEventListener('click', function() {
            errorDiv.style.display = 'none';
        });
    }

    function filterTableRows() {
        const searchTerm = searchInput.value.toLowerCase();
        const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
        const rows = document.querySelectorAll('.test-row');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const status = row.querySelector('.status-badge').textContent.trim();
            const matchesSearch = text.includes(searchTerm);
            const matchesFilter = activeFilter === 'all' || status === activeFilter;

            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        });
    }
});