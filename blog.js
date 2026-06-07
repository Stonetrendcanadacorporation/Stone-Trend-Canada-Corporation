/**
 * Stone Trend Blog - Index page logic
 * Loads blog-index.json and renders article list with filtering and pagination.
 * Uses sessionStorage cache for instant repeat loads; fallback script only on fetch error.
 */

(function () {
  const ARTICLES_PER_PAGE = 24;
  const CACHE_KEY = 'stonetrend_blog_index';
  const CACHE_MAX_AGE_MS = 5 * 60 * 1000; // 5 minutes
  let allArticles = [];
  let filteredArticles = [];
  let currentPage = 1;

  const listEl = document.getElementById('blog-list');
  const paginationEl = document.getElementById('blog-pagination');
  const categoryFilter = document.getElementById('blog-category-filter');
  const searchInput = document.getElementById('blog-search');

  if (!listEl) return;

  function renderArticleCard(article) {
    const href = window.location.pathname.includes('/blog/') ? `articles/${article.slug}.html` : `blog/articles/${article.slug}.html`;
    return `
      <article class="blog-card" data-slug="${escapeHtml(article.slug)}">
        <a href="${href}" class="blog-card-link">
          <span class="blog-card-category">${escapeHtml(article.category)}</span>
          <h3 class="blog-card-title">${escapeHtml(article.title)}</h3>
          <span class="blog-card-cta">Read article →</span>
        </a>
      </article>
    `;
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function filterArticles() {
    const category = categoryFilter ? categoryFilter.value : '';
    const search = searchInput ? searchInput.value.trim().toLowerCase() : '';

    filteredArticles = allArticles.filter((a) => {
      const matchCategory = !category || a.category === category;
      const matchSearch = !search || a.title.toLowerCase().includes(search) || a.category.toLowerCase().includes(search);
      return matchCategory && matchSearch;
    });

    currentPage = 1;
    render();
  }

  function render() {
    const start = (currentPage - 1) * ARTICLES_PER_PAGE;
    const end = start + ARTICLES_PER_PAGE;
    const pageArticles = filteredArticles.slice(start, end);

    if (filteredArticles.length === 0) {
      listEl.innerHTML = '<p class="blog-empty">No articles match your filters. Try a different category or search term.</p>';
      paginationEl.innerHTML = '';
      return;
    }

    listEl.innerHTML = pageArticles.map(renderArticleCard).join('');
    renderPagination();
  }

  function renderPagination() {
    const totalPages = Math.ceil(filteredArticles.length / ARTICLES_PER_PAGE);

    if (totalPages <= 1) {
      paginationEl.innerHTML = '';
      return;
    }

    let html = '<div class="blog-pagination-inner">';
    if (currentPage > 1) {
      html += `<button type="button" class="blog-pagination-btn" data-page="${currentPage - 1}" aria-label="Previous page">← Previous</button>`;
    }
    html += `<span class="blog-pagination-info">Page ${currentPage} of ${totalPages}</span>`;
    if (currentPage < totalPages) {
      html += `<button type="button" class="blog-pagination-btn" data-page="${currentPage + 1}" aria-label="Next page">Next →</button>`;
    }
    html += '</div>';
    paginationEl.innerHTML = html;

    paginationEl.querySelectorAll('.blog-pagination-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        currentPage = parseInt(btn.dataset.page, 10);
        render();
        listEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  function init() {
    const loadArticles = (articles) => {
      allArticles = articles || [];
      filteredArticles = [...allArticles];
      render();
      try {
        window.dispatchEvent(new CustomEvent('blog-rendered'));
      } catch (e) {}
    };

    const saveCache = (articles) => {
      try {
        sessionStorage.setItem(CACHE_KEY, JSON.stringify({
          t: Date.now(),
          articles: articles || []
        }));
      } catch (e) {}
    };

    const readCache = () => {
      try {
        const raw = sessionStorage.getItem(CACHE_KEY);
        if (!raw) return null;
        const obj = JSON.parse(raw);
        if (!obj || !Array.isArray(obj.articles)) return null;
        if (Date.now() - (obj.t || 0) > CACHE_MAX_AGE_MS) return null;
        return obj.articles;
      } catch (e) {
        return null;
      }
    };

    const loadFallbackScript = (done) => {
      const script = document.createElement('script');
      script.src = 'blog-data.js'; // same folder as blog/index.html
      script.onload = () => {
        if (typeof window.BLOG_ARTICLES !== 'undefined' && window.BLOG_ARTICLES.length) {
          done(window.BLOG_ARTICLES);
        } else {
          done(null);
        }
      };
      script.onerror = () => done(null);
      document.head.appendChild(script);
    };

    window.__blogArticles = {
      add: (article) => {
        allArticles.unshift(article);
        filteredArticles = [...allArticles];
        saveCache(allArticles);
        render();
      },
      remove: (slug) => {
        allArticles = allArticles.filter((a) => a.slug !== slug);
        filteredArticles = filteredArticles.filter((a) => a.slug !== slug);
        saveCache(allArticles);
        render();
      },
      update: (slug, data) => {
        const a = allArticles.find((x) => x.slug === slug);
        if (a) {
          if (data.title !== undefined) a.title = data.title;
          if (data.category !== undefined) a.category = data.category;
        }
        const f = filteredArticles.find((x) => x.slug === slug);
        if (f) {
          if (data.title !== undefined) f.title = data.title;
          if (data.category !== undefined) f.category = data.category;
        }
        saveCache(allArticles);
        render();
      },
      getList: () => allArticles,
    };

    const cached = readCache();
    if (cached && cached.length) {
      loadArticles(cached);
    }

    fetch('blog-index.json')
      .then((res) => res.ok ? res.json() : Promise.reject())
      .then((data) => {
        const articles = data && data.articles ? data.articles : [];
        saveCache(articles);
        loadArticles(articles);
      })
      .catch(() => {
        if (allArticles.length) return; // already have cache
        loadFallbackScript((articles) => {
          if (articles && articles.length) {
            loadArticles(articles);
          } else {
            listEl.innerHTML = '<p class="blog-error">Unable to load articles. Please try again later.</p>';
            try {
              window.dispatchEvent(new CustomEvent('blog-rendered'));
            } catch (e) {}
          }
        });
      });

    if (categoryFilter) {
      categoryFilter.addEventListener('change', filterArticles);
    }
    if (searchInput) {
      searchInput.addEventListener('input', debounce(filterArticles, 300));
    }
  }

  function debounce(fn, ms) {
    let timeout;
    return function () {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, arguments), ms);
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
