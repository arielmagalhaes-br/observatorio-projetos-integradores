document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.curadoria-filtros');
    const searchInput = document.querySelector('.curadoria-live-search');
    const filters = document.querySelectorAll('.curadoria-filter');
    const tableBody = document.getElementById('curadoria-table-body');
    const headerCount = document.getElementById('curadoria-count');
    const footerCount = document.getElementById('curadoria-footer-count');

    if (!form || !searchInput || !tableBody) return;

    let debounceTimer;

    const updateCounters = () => {
        const emptyRow = tableBody.querySelector('.curadoria-empty-row');
        const count = emptyRow ? 0 : tableBody.querySelectorAll('tr').length;
        const plural = count === 1 ? '' : 's';

        if (headerCount) {
            headerCount.textContent = `Exibindo ${count} projeto${plural}`;
        }

        if (footerCount) {
            footerCount.textContent = `Mostrando ${count} resultado${plural}`;
        }
    };

    const cleanParams = (formData) => {
        for (const [key, value] of [...formData.entries()]) {
            if (!value) {
                formData.delete(key);
            }
        }
    };

    const runSearch = () => {
        const formData = new FormData(form);
        cleanParams(formData);

        const params = new URLSearchParams(formData);
        const actionUrl = form.getAttribute('action') || window.location.pathname;
        const queryString = params.toString();
        const fetchUrl = queryString ? `${actionUrl}?${queryString}` : actionUrl;

        fetch(fetchUrl, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then((response) => {
                if (!response.ok) throw new Error('Erro ao buscar projetos da curadoria.');
                return response.text();
            })
            .then((html) => {
                tableBody.innerHTML = html;
                updateCounters();
                window.history.replaceState({ path: fetchUrl }, '', fetchUrl);
            })
            .catch((error) => {
                console.error('Erro na busca da curadoria:', error);
            });
    };

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(runSearch, 300);
    });

    filters.forEach((filter) => {
        filter.addEventListener('change', runSearch);
    });
});
