/**
 * Archify Diagram Controller
 * Manages SVG pan/zoom, step-lighting, node focus, and reach traversal.
 */

class DiagramController {
  constructor(viewportEl) {
    this.viewport = viewportEl;
    this.currentSvg = null;
    this.scale = 1;
    this.panX = 0;
    this.panY = 0;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    this.focusedNodeId = null;

    this.initPanZoom();
  }

  setSvg(svgElement) {
    this.currentSvg = svgElement;
    this.resetZoom();
    this.bindNodeEvents();
  }

  initPanZoom() {
    this.viewport.addEventListener('mousedown', (e) => {
      if (e.target.closest('.node') || e.target.closest('button')) return;
      this.isDragging = true;
      this.startX = e.clientX - this.panX;
      this.startY = e.clientY - this.panY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      this.panX = e.clientX - this.startX;
      this.panY = e.clientY - this.startY;
      this.applyTransform();
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    this.viewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.zoom(zoomFactor);
    }, { passive: false });
  }

  zoom(factor) {
    const newScale = this.scale * factor;
    if (newScale >= 0.4 && newScale <= 3.0) {
      this.scale = newScale;
      this.applyTransform();
    }
  }

  resetZoom() {
    this.scale = 1;
    this.panX = 0;
    this.panY = 0;
    this.applyTransform();
  }

  applyTransform() {
    if (!this.currentSvg) return;
    this.currentSvg.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.scale})`;
  }

  bindNodeEvents() {
    if (!this.currentSvg) return;
    const nodes = this.currentSvg.querySelectorAll('.node');
    nodes.forEach(node => {
      node.addEventListener('click', (e) => {
        e.stopPropagation();
        const nodeId = node.id || node.getAttribute('data-node-id');
        this.onNodeClick(nodeId);
      });
    });
  }

  onNodeClick(nodeId) {
    this.focusedNodeId = nodeId;
    window.dispatchEvent(new CustomEvent('archify:node-selected', { detail: { nodeId } }));
  }

  highlightStep(activeNodeIds = [], activeEdgeIds = []) {
    if (!this.currentSvg) return;

    const allNodes = this.currentSvg.querySelectorAll('.node');
    const allEdges = this.currentSvg.querySelectorAll('.edge');

    if (activeNodeIds.length === 0 && activeEdgeIds.length === 0) {
      // Clear lighting
      allNodes.forEach(n => n.classList.remove('is-active', 'is-dimmed'));
      allEdges.forEach(e => e.classList.remove('is-active', 'is-dimmed'));
      return;
    }

    allNodes.forEach(node => {
      const id = node.id || node.getAttribute('data-node-id');
      if (activeNodeIds.includes(id)) {
        node.classList.add('is-active');
        node.classList.remove('is-dimmed');
      } else {
        node.classList.remove('is-active');
        node.classList.add('is-dimmed');
      }
    });

    allEdges.forEach(edge => {
      const id = edge.id;
      if (activeEdgeIds.includes(id)) {
        edge.classList.add('is-active');
        edge.classList.remove('is-dimmed');
      } else {
        edge.classList.remove('is-active');
        edge.classList.add('is-dimmed');
      }
    });
  }

  highlightReach(direction = 'downstream') {
    if (!this.currentSvg || !this.focusedNodeId) return;

    const allNodes = this.currentSvg.querySelectorAll('.node');
    const allEdges = this.currentSvg.querySelectorAll('.edge');

    allNodes.forEach(n => n.classList.add('is-dimmed'));
    allEdges.forEach(e => e.classList.add('is-dimmed'));

    const focusedEl = this.currentSvg.getElementById(this.focusedNodeId);
    if (focusedEl) {
      focusedEl.classList.remove('is-dimmed');
      focusedEl.classList.add('is-active');
    }

    // Trace connected edges
    allEdges.forEach(edge => {
      const from = edge.getAttribute('data-from');
      const to = edge.getAttribute('data-to');
      if (direction === 'downstream' && from === this.focusedNodeId) {
        edge.classList.remove('is-dimmed');
        edge.classList.add('is-active');
        const targetNode = this.currentSvg.getElementById(to);
        if (targetNode) {
          targetNode.classList.remove('is-dimmed');
          targetNode.classList.add('reach-target');
        }
      } else if (direction === 'upstream' && to === this.focusedNodeId) {
        edge.classList.remove('is-dimmed');
        edge.classList.add('is-active');
        const sourceNode = this.currentSvg.getElementById(from);
        if (sourceNode) {
          sourceNode.classList.remove('is-dimmed');
          sourceNode.classList.add('reach-source');
        }
      }
    });
  }
}

window.DiagramController = DiagramController;
