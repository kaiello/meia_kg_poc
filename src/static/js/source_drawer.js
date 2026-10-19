/**
 * Archify Source Drawer
 * Manages the slide-over code & data excerpt viewer pinned to exact local files.
 */

class SourceDrawer {
  constructor(drawerEl) {
    this.drawer = drawerEl;
    this.titleEl = this.drawer.querySelector('.drawer-title');
    this.metaEl = this.drawer.querySelector('.drawer-meta');
    this.contentEl = this.drawer.querySelector('.drawer-content');
    this.closeBtn = this.drawer.querySelector('.drawer-close');

    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }

    // Close on escape key
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
  }

  isOpen() {
    return this.drawer.classList.contains('is-open');
  }

  open() {
    this.drawer.classList.add('is-open');
  }

  close() {
    this.drawer.classList.remove('is-open');
  }

  async showSource(sourceDef) {
    this.open();
    this.titleEl.textContent = sourceDef.label || `Source ${sourceDef.id}`;
    this.metaEl.textContent = `${sourceDef.file} (Lines ${sourceDef.startLine}–${sourceDef.endLine})`;
    this.contentEl.innerHTML = '<div style="color:var(--text-muted); padding:20px;">Fetching source excerpt...</div>';

    try {
      // Check if global inline source cache is available (for standalone single HTML mode)
      if (window.ARCHIFY_SOURCE_CACHE && window.ARCHIFY_SOURCE_CACHE[sourceDef.id]) {
        this.renderLines(window.ARCHIFY_SOURCE_CACHE[sourceDef.id]);
        return;
      }

      // Fetch from API
      const url = `/api/explainer/source?file=${encodeURIComponent(sourceDef.file)}&start=${sourceDef.startLine}&end=${sourceDef.endLine}`;
      const resp = await fetch(url);
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const data = await resp.json();
      if (data.error) {
        throw new Error(data.error);
      }
      this.renderLines(data);
    } catch (err) {
      this.contentEl.innerHTML = `
        <div style="color:var(--accent-rose); padding:16px; background:rgba(244,63,94,0.1); border-radius:6px;">
          Failed to load source receipt: ${err.message}<br>
          <span style="font-size:11px; color:var(--text-muted);">Target: ${sourceDef.file} (Lines ${sourceDef.startLine}–${sourceDef.endLine})</span>
        </div>
      `;
    }
  }

  renderLines(data) {
    const lines = data.lines || [];
    let html = '<div class="code-container">';
    lines.forEach(item => {
      const escaped = this.escapeHtml(item.content);
      html += `
        <div class="code-line">
          <div class="code-line-num">${item.lineNumber}</div>
          <div class="code-line-text">${escaped || '&nbsp;'}</div>
        </div>
      `;
    });
    html += '</div>';

    html += `
      <div style="margin-top:16px; display:flex; justify-content:space-between; align-items:center;">
        <span style="color:var(--text-dim); font-size:11px;">Git Verified Anchor | Total Lines: ${data.totalLines || 'N/A'}</span>
        <button class="src-tag" onclick="navigator.clipboard.writeText(window.location.href); alert('Permalink copied to clipboard!');">
          Copy Link
        </button>
      </div>
    `;

    this.contentEl.innerHTML = html;
  }

  escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

window.SourceDrawer = SourceDrawer;
