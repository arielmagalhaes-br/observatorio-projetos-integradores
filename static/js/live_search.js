/**
 * Live Search Global - Conecta PI
 * Implementa busca em tempo real com debounce para inputs com classe .live-search-input.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInputs = document.querySelectorAll('.live-search-input');
    
    searchInputs.forEach(input => {
        const form = input.closest('form');
        const grid = document.getElementById('projetos-grid');
        
        if (!form || !grid) return;
        
        let debounceTimer;
        
        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {
                // Serializa todos os campos do formulário (incluindo inputs ocultos dos dropdowns)
                const formData = new FormData(form);
                
                // Remove campos vazios para limpar a URL
                for (const [key, value] of [...formData.entries()]) {
                    if (!value) {
                        formData.delete(key);
                    }
                }
                
                const params = new URLSearchParams(formData);
                const actionUrl = form.getAttribute('action') || window.location.pathname;
                const fetchUrl = `${actionUrl}?${params.toString()}`;
                
                // Dispara a busca AJAX
                fetch(fetchUrl, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) throw new Error('Erro na requisição de busca.');
                    return response.text();
                })
                .then(html => {
                    // Substitui o conteúdo do grid com os novos cards/estado vazio
                    grid.innerHTML = html;
                    
                    // Atualiza a URL do navegador sem recarregar a página para manter histórico e compartilhamento
                    const newUrl = params.toString() ? `${actionUrl}?${params.toString()}` : actionUrl;
                    window.history.replaceState({ path: newUrl }, '', newUrl);
                    
                    // Atualiza o contador de resultados no cabeçalho
                    const cardsCount = grid.querySelectorAll('.projeto-card').length;
                    const resultsInfo = document.querySelector('.vitrine-results-info');
                    if (resultsInfo) {
                        if (cardsCount > 0) {
                            const plural = cardsCount !== 1 ? 's' : '';
                            resultsInfo.innerHTML = `Exibindo <strong>${cardsCount}</strong> projeto${plural} encontrado${plural}`;
                        } else {
                            resultsInfo.innerHTML = '';
                        }
                    }
                })
                .catch(error => {
                    console.error('Erro na busca em tempo real:', error);
                });
            }, 300); // Debounce de 300ms
        });
    });
});
