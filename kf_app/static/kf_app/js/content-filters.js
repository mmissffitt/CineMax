class ContentFilter {
    constructor() {
        this.contentType = window.contentData.contentType;
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        this.selectedGenres = new Set();
        this.searchTerm = '';
        this.sortBy = '-release_date';
        
        this.init();
    }

    init() {
        // Получаем элементы
        this.contentGrid = document.getElementById('contentGrid');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.noResults = document.getElementById('noResults');
        this.searchInput = document.getElementById('searchInput');
        this.sortSelect = document.getElementById('sortSelect');
        this.genresFilter = document.getElementById('genresFilter');
        this.filtersToggle = document.querySelector('.filters-toggle');
        
        // Инициализируем жанры
        this.initGenres();
        
        // Добавляем обработчики событий
        this.addEventListeners();
        
        // Проверяем, есть ли кнопка "Загрузить еще"
        if (this.loadMoreBtn) {
            this.loadMoreBtn.addEventListener('click', () => this.loadMore());
        }
        
        // Infinite scroll
        this.initInfiniteScroll();
    }

    initGenres() {
        const genresList = document.getElementById('genresList');
        if (!genresList) return;
        
        const genres = window.contentData.initialGenres || [];
        genresList.innerHTML = genres.map(genre => `
            <label class="genre-checkbox">
                <input type="checkbox" value="${genre.id}">
                ${genre.name}
            </label>
        `).join('');
    }

    addEventListeners() {
        // Поиск с debounce
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(() => {
                this.searchTerm = this.searchInput.value;
                this.resetAndFilter();
            }, 300));
        }

        // Сортировка
        if (this.sortSelect) {
            this.sortSelect.addEventListener('change', () => {
                this.sortBy = this.sortSelect.value;
                this.resetAndFilter();
            });
        }

        // Фильтры по жанрам
        const genresList = document.getElementById('genresList');
        if (genresList) {
            genresList.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    const genreId = e.target.value;
                    if (e.target.checked) {
                        this.selectedGenres.add(genreId);
                    } else {
                        this.selectedGenres.delete(genreId);
                    }
                    this.resetAndFilter();
                }
            });
        }

        // Кнопка сброса
        const clearBtn = document.getElementById('clearFilters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFilters());
        }

        // Toggle фильтров
        if (this.filtersToggle) {
            this.filtersToggle.addEventListener('click', () => {
                const isHidden = this.genresFilter.style.display === 'none';
                this.genresFilter.style.display = isHidden ? 'block' : 'none';
                this.filtersToggle.textContent = isHidden ? 'Фильтры по жанрам ▲' : 'Фильтры по жанрам ▼';
            });
        }
    }

    initInfiniteScroll() {
        window.addEventListener('scroll', this.debounce(() => {
            if (this.isLoading || !this.hasMore) return;
            
            const scrollY = window.scrollY;
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight;
            
            // Загружаем когда дошли до 200px от низа
            if (scrollY + windowHeight >= documentHeight - 200) {
                this.loadMore();
            }
        }, 100));
    }

    async loadMore() {
        if (this.isLoading || !this.hasMore) return;
        
        this.isLoading = true;
        this.showLoading();
        
        const nextPage = this.currentPage + 1;
        
        try {
            const data = await this.fetchContent(nextPage);
            
            if (data.html) {
                this.appendContent(data.html);
                this.currentPage = nextPage;
                this.hasMore = data.has_next;
            }
            
            if (!this.hasMore && this.loadMoreBtn) {
                this.loadMoreBtn.style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading more:', error);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    async resetAndFilter() {
        this.currentPage = 1;
        this.hasMore = true;
        
        this.showLoading();
        this.contentGrid.innerHTML = '';
        
        if (this.loadMoreBtn) {
            this.loadMoreBtn.style.display = 'none';
        }
        
        try {
            const data = await this.fetchContent(1);
            
            if (data.html) {
                this.contentGrid.innerHTML = data.html;
                this.currentPage = 1;
                this.hasMore = data.has_next;
                
                if (this.hasMore && this.loadMoreBtn) {
                    this.loadMoreBtn.style.display = 'inline-block';
                }
                
                this.noResults.style.display = 'none';
            } else {
                this.noResults.style.display = 'block';
            }
        } catch (error) {
            console.error('Error filtering:', error);
        } finally {
            this.hideLoading();
        }
    }

    async fetchContent(page) {
        const params = new URLSearchParams({
            type: this.contentType,
            page: page,
            search: this.searchTerm,
            sort: this.sortBy
        });
        
        // Добавляем выбранные жанры
        this.selectedGenres.forEach(genreId => {
            params.append('genres[]', genreId);
        });
        
        const response = await fetch(`/api/filter-content/?${params.toString()}`);
        return await response.json();
    }

    appendContent(html) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        while (tempDiv.firstChild) {
            this.contentGrid.appendChild(tempDiv.firstChild);
        }
    }

    clearFilters() {
        // Сброс чекбоксов
        document.querySelectorAll('.genre-checkbox input').forEach(cb => {
            cb.checked = false;
        });
        
        // Сброс поиска
        if (this.searchInput) {
            this.searchInput.value = '';
            this.searchTerm = '';
        }
        
        // Сброс сортировки
        if (this.sortSelect) {
            this.sortSelect.value = '-release_date';
            this.sortBy = '-release_date';
        }
        
        this.selectedGenres.clear();
        this.resetAndFilter();
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'block';
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'none';
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    if (window.contentData) {
        new ContentFilter();
    }
});

// Добавим обработку поиска из хедера
class HeaderSearch {
    constructor() {
        this.searchInput = document.getElementById('headerSearchInput');
        this.searchForm = document.getElementById('headerSearchForm');
        this.searchResults = document.getElementById('searchResults');
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        this.searchInput.addEventListener('input', this.debounce(() => {
            this.performSearch();
        }, 300));
        
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
        
        // Закрываем результаты при клике вне
        document.addEventListener('click', (e) => {
            if (!this.searchForm.contains(e.target)) {
                this.searchResults.style.display = 'none';
            }
        });
    }
    
    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (query.length < 2) {
            this.searchResults.style.display = 'none';
            return;
        }
        
        try {
            const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.showResults(data.results);
        } catch (error) {
            console.error('Search error:', error);
        }
    }
    
    showResults(results) {
        if (results.length === 0) {
            this.searchResults.innerHTML = '<div class="search-result-item">Ничего не найдено</div>';
        } else {
            this.searchResults.innerHTML = results.map(item => `
                <div class="search-result-item" onclick="window.location.href='/${item.type}/${item.id}/'">
                    <img src="${item.poster || '/static/kf_app/images/default_poster.jpg'}" 
                         alt="${item.title}" 
                         class="search-result-poster"
                         onerror="this.src='/static/kf_app/images/default_poster.jpg'">
                    <div class="search-result-info">
                        <div class="search-result-title">${item.title}</div>
                        <div class="search-result-meta">
                            ${item.year} • ${item.rating} ★
                            <span class="search-result-type">${item.type === 'movie' ? 'Фильм' : 'Сериал'}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        this.searchResults.style.display = 'block';
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    new HeaderSearch();
});