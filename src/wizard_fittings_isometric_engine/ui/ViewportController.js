/**
 * ViewportController – attaches mouse / touch event listeners to a canvas and
 * updates the renderer's pan, scale, and rotation state in real time.
 *
 * Supported gestures:
 *   Scroll-wheel / pinch  → zoom
 *   Middle-click drag     → pan
 *   Space + left-drag     → pan
 *   Right-click drag      → isometric-snap rotate
 */
export class ViewportController {
  /**
   * @param {HTMLCanvasElement}        canvas
   * @param {object}                   vpConfig  – config.viewport_controls
   * @param {{ onUpdate: function }}   callbacks
   */
  constructor(canvas, vpConfig, { onUpdate }) {
    this.canvas   = canvas;
    this.cfg      = vpConfig;
    this.onUpdate = onUpdate;

    this._scale      = 1.0;
    this._panX       = 0;
    this._panY       = 0;
    this._rotDeg     = 0;
    this._spaceDown  = false;
    this._mouse      = { x: 0, y: 0, button: -1, down: false };

    this._bindEvents();
  }

  get state() {
    return { scale: this._scale, panX: this._panX, panY: this._panY, rotDeg: this._rotDeg };
  }

  // ── event binding ──────────────────────────────────────────────────────────

  _bindEvents() {
    const el  = this.canvas;
    el.addEventListener("wheel",       this._onWheel.bind(this),     { passive: false });
    el.addEventListener("mousedown",   this._onMouseDown.bind(this));
    el.addEventListener("mousemove",   this._onMouseMove.bind(this));
    el.addEventListener("mouseup",     this._onMouseUp.bind(this));
    el.addEventListener("mouseleave",  this._onMouseUp.bind(this));
    el.addEventListener("contextmenu", e => e.preventDefault());

    // Touch (pinch-to-zoom)
    el.addEventListener("touchstart",  this._onTouchStart.bind(this), { passive: false });
    el.addEventListener("touchmove",   this._onTouchMove.bind(this),  { passive: false });
    el.addEventListener("touchend",    this._onTouchEnd.bind(this));

    // Space key (pan mode)
    window.addEventListener("keydown", e => { if (e.code === "Space") { e.preventDefault(); this._spaceDown = true; }});
    window.addEventListener("keyup",   e => { if (e.code === "Space") this._spaceDown = false; });

    // +/- keys for zoom
    window.addEventListener("keydown", e => {
      const z = this.cfg.zoom;
      if (e.key === "+" || e.key === "=") this._applyZoom(z.step);
      if (e.key === "-")                  this._applyZoom(-z.step);
    });
  }

  // ── wheel ─────────────────────────────────────────────────────────────────

  _onWheel(e) {
    e.preventDefault();
    const step = e.deltaY < 0 ? this.cfg.zoom.step : -this.cfg.zoom.step;
    this._applyZoom(step);
  }

  _applyZoom(delta) {
    const z = this.cfg.zoom;
    this._scale = Math.max(z.min_scale, Math.min(z.max_scale, this._scale + delta));
    this._notify();
  }

  // ── mouse ─────────────────────────────────────────────────────────────────

  _onMouseDown(e) {
    this._mouse.down   = true;
    this._mouse.button = e.button;
    this._mouse.x      = e.clientX;
    this._mouse.y      = e.clientY;
    if (e.button === 2 || e.button === 1) e.preventDefault();
  }

  _onMouseMove(e) {
    if (!this._mouse.down) return;

    const dx = e.clientX - this._mouse.x;
    const dy = e.clientY - this._mouse.y;
    this._mouse.x = e.clientX;
    this._mouse.y = e.clientY;

    const isPan   = this._mouse.button === 1 || this._spaceDown;
    const isRotate = this._mouse.button === 2;

    if (isPan && this.cfg.pan.enabled) {
      this._panX += dx;
      this._panY += dy;
      this._notify();
    } else if (isRotate && this.cfg.rotate.enabled) {
      this._rotDeg += dx * 0.5;
      // Snap to nearest snap angle
      const snaps  = this.cfg.rotate.snap_angles;
      const nearest = snaps.reduce((a, b) =>
        Math.abs(b - ((this._rotDeg % 360) + 360) % 360) <
        Math.abs(a - ((this._rotDeg % 360) + 360) % 360) ? b : a, snaps[0]);
      const diff = Math.abs(nearest - ((this._rotDeg % 360) + 360) % 360);
      if (diff < 5) this._rotDeg = nearest;
      this._notify();
    }
  }

  _onMouseUp() {
    this._mouse.down   = false;
    this._mouse.button = -1;
  }

  // ── touch (pinch) ─────────────────────────────────────────────────────────

  _onTouchStart(e) {
    if (e.touches.length === 2) {
      this._pinchDist = this._getTouchDist(e.touches);
    }
  }

  _onTouchMove(e) {
    e.preventDefault();
    if (e.touches.length === 2) {
      const dist  = this._getTouchDist(e.touches);
      const ratio = dist / (this._pinchDist || dist);
      this._pinchDist = dist;
      const z = this.cfg.zoom;
      this._scale = Math.max(z.min_scale, Math.min(z.max_scale, this._scale * ratio));
      this._notify();
    }
  }

  _onTouchEnd() { this._pinchDist = null; }

  _getTouchDist(touches) {
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  // ── notify ────────────────────────────────────────────────────────────────

  _notify() {
    if (this.onUpdate) this.onUpdate(this.state);
  }

  /** Reset to default view */
  reset() {
    this._scale  = 1.0;
    this._panX   = 0;
    this._panY   = 0;
    this._rotDeg = 0;
    this._notify();
  }
}
