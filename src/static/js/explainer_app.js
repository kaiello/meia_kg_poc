/**
 * Archify Explainer Application Coordinator
 * State machine, URL hash router, and user interaction manager.
 */

class ExplainerApp {
  constructor() {
    this.panels = [];
    this.currentPanel = null;
    this.currentStepIdx = 0;
    this.controller = null;
    this.drawer = null;

    this.init();
  }

  async init() {
    // 1. Initialize Components
    const viewport = document.getElementById('svgViewport');
    this.controller = new DiagramController(viewport);

    const drawerEl = document.getElementById('sourceDrawer');
    this.drawer = new SourceDrawer(drawerEl);

    // 2. Fetch or load Panels
    if (window.ARCHIFY_PANELS && window.ARCHIFY_PANELS.length > 0) {
      this.panels = window.ARCHIFY_PANELS;
    } else {
      try {
        const resp = await fetch('/api/explainer/data');
        const data = await resp.json();
        this.panels = data.panels || [];
      } catch (e) {
        console.error('Failed to load panel data from API, using fallback', e);
      }
    }

    // 3. Bind Global Actions
    this.bindGlobalEvents();
    this.bindKeyboardShortcuts();

    // 4. Initial Hash Routing
    window.addEventListener('hashchange', () => this.handleHashChange());
    this.handleHashChange();
  }

  bindGlobalEvents() {
    // Theme toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => this.cycleTheme());
    }

    // Fullscreen / Presentation Mode
    const fsBtn = document.getElementById('fullscreenBtn');
    if (fsBtn) {
      fsBtn.addEventListener('click', () => this.togglePresentationMode());
    }

    // Guide Modal
    const guideBtn = document.getElementById('guideBtn');
    const guideModal = document.getElementById('guideModal');
    const closeGuideBtn = document.getElementById('closeGuideBtn');
    if (guideBtn && guideModal) {
      guideBtn.addEventListener('click', () => guideModal.classList.add('is-open'));
    }
    if (closeGuideBtn && guideModal) {
      closeGuideBtn.addEventListener('click', () => guideModal.classList.remove('is-open'));
    }

    // Canvas Buttons
    document.getElementById('zoomInBtn')?.addEventListener('click', () => this.controller.zoom(1.2));
    document.getElementById('zoomOutBtn')?.addEventListener('click', () => this.controller.zoom(0.8));
    document.getElementById('zoomResetBtn')?.addEventListener('click', () => this.controller.resetZoom());

    // Reach Controls
    document.getElementById('reachDownstreamBtn')?.addEventListener('click', () => this.controller.highlightReach('downstream'));
    document.getElementById('reachUpstreamBtn')?.addEventListener('click', () => this.controller.highlightReach('upstream'));
    document.getElementById('reachResetBtn')?.addEventListener('click', () => {
      const step = this.currentPanel?.steps?.[this.currentStepIdx];
      if (step) {
        this.controller.highlightStep(step.activeNodes, step.activeEdges);
      } else {
        this.controller.highlightStep([], []);
      }
    });

    // Node Selected Event
    window.addEventListener('archify:node-selected', (e) => {
      const { nodeId } = e.detail;
      this.updateHash({ focus: nodeId });
    });
  }

  bindKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.key === '?') {
        const modal = document.getElementById('guideModal');
        modal?.classList.toggle('is-open');
      } else if (e.key === 't' || e.key === 'T') {
        this.cycleTheme();
      } else if (e.key === 'f' || e.key === 'F') {
        this.togglePresentationMode();
      } else if (['1', '2', '3', '4', '5'].includes(e.key)) {
        const idx = parseInt(e.key, 10);
        this.switchPanelByIndex(idx);
      } else if (e.key === '+' || e.key === '=') {
        this.controller.zoom(1.15);
      } else if (e.key === '-') {
        this.controller.zoom(0.85);
      } else if (e.key === '0') {
        this.controller.resetZoom();
      }
    });
  }

  cycleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : current === 'light' ? 'high-contrast' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('archify_theme', next);
  }

  togglePresentationMode() {
    document.body.classList.toggle('presentation-mode');
  }

  handleHashChange() {
    const hash = window.location.hash.replace(/^#/, '');
    const params = new URLSearchParams(hash);

    const panelParam = params.get('panel') || '1';
    const stepParam = parseInt(params.get('step') || '1', 10);
    const focusParam = params.get('focus');
    const reachParam = params.get('reach');

    this.switchPanel(panelParam, stepParam, focusParam, reachParam);
  }

  updateHash(changes = {}) {
    const currentParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
    Object.entries(changes).forEach(([k, v]) => {
      if (v === null || v === undefined) {
        currentParams.delete(k);
      } else {
        currentParams.set(k, v);
      }
    });
    window.location.hash = currentParams.toString();
  }

  switchPanelByIndex(idx) {
    const p = this.panels.find(item => item.index === idx);
    if (p) {
      this.updateHash({ panel: p.index, step: 1, focus: null, reach: null });
    }
  }

  switchPanel(panelIdOrIndex, stepNum = 1, focusNode = null, reachMode = null) {
    const panel = this.panels.find(p => p.id === panelIdOrIndex || String(p.index) === String(panelIdOrIndex)) || this.panels[0];
    if (!panel) return;

    this.currentPanel = panel;
    this.currentStepIdx = Math.max(0, stepNum - 1);

    // 1. Update Tabs
    this.renderTabs();

    // 2. Render Left Pane
    this.renderNarrativePane();

    // 3. Load & Render SVG
    this.loadSvg(panel.svgFile).then(() => {
      // Apply step highlight
      const step = panel.steps?.[this.currentStepIdx];
      if (step) {
        this.controller.highlightStep(step.activeNodes, step.activeEdges);
      }
      if (focusNode) {
        this.controller.focusedNodeId = focusNode;
        if (reachMode) {
          this.controller.highlightReach(reachMode);
        }
      }
    });
  }

  renderTabs() {
    const container = document.getElementById('navTabsContainer');
    if (!container) return;

    let html = '';
    this.panels.forEach(p => {
      const activeClass = p.id === this.currentPanel.id ? 'is-active' : '';
      html += `
        <button class="nav-tab-btn ${activeClass}" onclick="app.switchPanelByIndex(${p.index})">
          <span>${p.index}.</span> ${p.shortTitle || p.title}
        </button>
      `;
    });
    container.innerHTML = html;
  }

  renderNarrativePane() {
    const c = this.currentPanel.conclusion || {};
    const conclusionEl = document.getElementById('conclusionCard');
    if (conclusionEl) {
      let metricsHtml = '';
      (c.metrics || []).forEach(m => {
        metricsHtml += `
          <div class="metric-chip">
            <div class="metric-label">${m.label}</div>
            <div class="metric-value">${m.value}</div>
          </div>
        `;
      });

      conclusionEl.innerHTML = `
        <div class="conclusion-badge">ARCHITECTURAL VERDICT &amp; RECEIPTS</div>
        <div class="conclusion-title">${c.headline || this.currentPanel.title}</div>
        <div class="conclusion-summary">${c.summary || ''}</div>
        <div class="conclusion-metrics">${metricsHtml}</div>
      `;
    }

    const stepsListEl = document.getElementById('stepperList');
    if (stepsListEl) {
      let stepsHtml = '';
      (this.currentPanel.steps || []).forEach((s, idx) => {
        const isActive = idx === this.currentStepIdx ? 'is-active' : '';
        let sourcesHtml = '';
        (s.sources || []).forEach(src => {
          sourcesHtml += `
            <button class="src-tag" onclick="app.openSource('${src.id}')" title="${src.label}">
              <span>📄</span> ${src.id}: ${src.file.split('/').pop()}#L${src.startLine}
            </button>
          `;
        });

        stepsHtml += `
          <div class="step-card ${isActive}" onclick="app.selectStep(${idx})" onmouseenter="app.previewStep(${idx})" onmouseleave="app.restoreActiveStep()">
            <div class="step-top">
              <span class="step-badge">${s.badge || 'STEP'}</span>
              <span class="step-number">0${s.step}</span>
            </div>
            <div class="step-title">${s.title}</div>
            <div class="step-narrative">${s.narrative}</div>
            <div class="step-sources">${sourcesHtml}</div>
          </div>
        `;
      });
      stepsListEl.innerHTML = stepsHtml;
    }
  }

  selectStep(idx) {
    this.currentStepIdx = idx;
    this.updateHash({ step: idx + 1, reach: null });
    this.renderNarrativePane();
    const step = this.currentPanel.steps?.[idx];
    if (step) {
      this.controller.highlightStep(step.activeNodes, step.activeEdges);
    }
  }

  previewStep(idx) {
    const step = this.currentPanel.steps?.[idx];
    if (step) {
      this.controller.highlightStep(step.activeNodes, step.activeEdges);
    }
  }

  restoreActiveStep() {
    const step = this.currentPanel.steps?.[this.currentStepIdx];
    if (step) {
      this.controller.highlightStep(step.activeNodes, step.activeEdges);
    }
  }

  openSource(sourceId) {
    let target = null;
    for (const p of this.panels) {
      for (const s of (p.steps || [])) {
        for (const src of (s.sources || [])) {
          if (src.id === sourceId) {
            target = src;
            break;
          }
        }
      }
    }
    if (target) {
      this.drawer.showSource(target);
    }
  }

  async loadSvg(svgFilename) {
    const viewport = document.getElementById('svgViewport');
    if (!viewport) return;

    // Check if SVG is already embedded in document
    const existing = document.getElementById(`inlined-${svgFilename}`);
    if (existing) {
      viewport.innerHTML = '';
      const clone = existing.cloneNode(true);
      clone.style.display = 'block';
      clone.id = 'activeDiagramSvg';
      viewport.appendChild(clone);
      this.controller.setSvg(clone);
      return;
    }

    // Otherwise fetch via HTTP
    try {
      const resp = await fetch(`/static/diagrams/${svgFilename}`);
      const svgText = await resp.text();
      viewport.innerHTML = svgText;
      const svgEl = viewport.querySelector('svg');
      if (svgEl) {
        svgEl.id = 'activeDiagramSvg';
        this.controller.setSvg(svgEl);
      }
    } catch (e) {
      viewport.innerHTML = `<div style="color:var(--accent-rose); padding:20px;">Failed to load diagram: ${svgFilename}</div>`;
    }
  }
}

window.ExplainerApp = ExplainerApp;

// Auto-boot on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new ExplainerApp();
});
