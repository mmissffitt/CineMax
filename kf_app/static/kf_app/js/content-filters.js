class HeaderSearch {
    constructor() {
        this.input = document.getElementById('headerSearchInput');
        this.results = document.getElementById('searchResults');
        if (!this.input) return;
        
        this.input.addEventListener('input', this.debounce(() => this.search(), 300));
        document.addEventListener('click', (e) => {
            if (!this.input?.contains(e.target)) this.results.style.display = 'none';
        });
    }
    
    async search() {
        const q = this.input.value.trim();
        if (q.length < 2) return this.results.style.display = 'none';
        
        try {
            const res = await fetch(`/api/search/?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            this.results.innerHTML = data.results.length ? data.results.map(item => `
                <div class="search-result-item" onclick="location.href='/${item.type}/${item.id}/'">
                    <img src="${item.poster || '/static/kf_app/images/default_poster.jpg'}" style="width:40px;height:60px;object-fit:cover">
                    <div style="padding:0 10px"><b>${this.escape(item.title)}</b><br><small>${item.year} ★ ${item.type === 'movie' ? 'Фильм' : 'Сериал'}</small></div>
                </div>
            `).join('') : '<div class="search-result-item">Ничего не найдено</div>';
            this.results.style.display = 'block';
        } catch(e) { console.error(e); }
    }
    
    escape(t) { return t.replace(/[&<>]/g, function(m) { return {'&':'&amp;','<':'&lt;','>':'&gt;'}[m]; }); }
    debounce(fn, ms) { let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); }; }
}

class ContentBrowser {
    constructor() {
        this.grid = document.getElementById('contentGrid');
        if (!this.grid || !window.contentData) return;
        
        this.type = window.contentData.contentType;
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        this.genres = new Set();
        this.sort = '-release_date';
        
        this.init();
    }
    
    init() {

        const list = document.getElementById('genresList');
        if (list && window.contentData.initialGenres) {
            list.innerHTML = window.contentData.initialGenres.map(g => 
                `<label><input type="checkbox" value="${g.id}"> ${g.name}</label>`
            ).join('');
            list.onchange = (e) => { if(e.target.type === 'checkbox') {
                e.target.checked ? this.genres.add(e.target.value) : this.genres.delete(e.target.value);
                this.reset();
            }};
        }
        
        const sortSelect = document.getElementById('sortSelect');
        if(sortSelect) sortSelect.onchange = () => { this.sort = sortSelect.value; this.reset(); };
        
        const clearBtn = document.getElementById('clearFilters');
        if(clearBtn) clearBtn.onclick = () => {
            document.querySelectorAll('#genresList input').forEach(cb => cb.checked = false);
            this.genres.clear();
            if(sortSelect) sortSelect.value = '-release_date';
            this.sort = '-release_date';
            this.reset();
        };

        const toggle = document.querySelector('.filters-toggle');
        const filterPanel = document.getElementById('genresFilter');
        if(toggle && filterPanel) toggle.onclick = () => {
            const show = filterPanel.style.display === 'none';
            filterPanel.style.display = show ? 'block' : 'none';
            toggle.textContent = show ? 'Фильтры по жанрам ▲' : 'Фильтры по жанрам ▼';
        };
        
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        if(this.loadMoreBtn) this.loadMoreBtn.onclick = () => this.loadMore();
        window.addEventListener('scroll', this.debounce(() => {
            if(!this.loading && this.hasMore && window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) this.loadMore();
        }, 100));
    }
    
    async reset() {
        this.page = 1;
        this.hasMore = true;
        this.grid.innerHTML = '';
        this.showLoading(true);
        await this.loadMore();
        this.showLoading(false);
    }
    
    async loadMore() {
        if(this.loading || !this.hasMore) return;
        this.loading = true;
        this.showLoading(true);
        
        try {
            const params = new URLSearchParams({ type: this.type, page: this.page, sort: this.sort });
            this.genres.forEach(g => params.append('genres[]', g));
            
            const res = await fetch(`/api/filter-content/?${params}`);
            const data = await res.json();
            
            if(data.html) {
                this.grid.insertAdjacentHTML('beforeend', data.html);
                this.page++;
                this.hasMore = data.has_next;
                if(this.loadMoreBtn) this.loadMoreBtn.style.display = this.hasMore ? 'inline-block' : 'none';
            }
        } catch(e) { console.error(e); }
        finally { this.loading = false; this.showLoading(false); }
    }
    
    showLoading(show) {
        const loader = document.getElementById('loadingIndicator');
        if(loader) loader.style.display = show ? 'block' : 'none';
    }
    
    debounce(fn, ms) { let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); }; }
}

document.addEventListener('DOMContentLoaded', () => {
    new HeaderSearch();
    new ContentBrowser();
});