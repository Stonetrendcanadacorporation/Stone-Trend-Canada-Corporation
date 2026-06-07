/**
 * Load site content from data/site-content.json and apply to the DOM.
 * Runs on every page load. If file exists, applies saved content so visitors see persisted edits.
 */
(function () {
  const CONTENT_URL = 'data/site-content.json';

  function applyContent(data) {
    if (!data || !Array.isArray(data.sections)) return;
    const main = document.getElementById('page-main');
    if (!main) return;

    data.sections.forEach(function (sectionData) {
      const id = sectionData.id;
      const content = sectionData.content;
      if (!id || !content) return;

      const section = main.querySelector('[data-section-id="' + id + '"]');
      if (!section) return;

      Object.keys(content).forEach(function (field) {
        const value = content[field];
        if (value == null || value === '') return;

        const el = section.querySelector('[data-content-field="' + field + '"]');
        if (!el) return;

        if (el.tagName === 'IMG') {
          el.src = value;
          if (el.alt !== undefined) el.alt = value;
        } else if (el.getAttribute('data-content-type') === 'html') {
          el.innerHTML = value;
        } else {
          el.textContent = value;
        }
      });
    });
  }

  function load() {
    fetch(CONTENT_URL, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (data) applyContent(data);
      })
      .catch(function () {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
