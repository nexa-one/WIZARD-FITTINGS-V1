/**
 * ThemeManager – handles theme selection, persistence (localStorage), and
 * live switching for the WIZARD FITTINGS isometric engine.
 */
export class ThemeManager {
  /**
   * @param {object} themingConfig  – config.theming section
   */
  constructor(themingConfig) {
    this.cfg          = themingConfig;
    this._currentKey  = this._loadPersistedTheme() || themingConfig.default_theme;
    this._listeners   = [];
  }

  // ── getters ───────────────────────────────────────────────────────────────

  get currentKey()    { return this._currentKey; }
  get currentTheme()  { return this.cfg.available_themes[this._currentKey]; }
  get availableKeys() { return Object.keys(this.cfg.available_themes); }

  // ── switching ─────────────────────────────────────────────────────────────

  /**
   * Switch to a different theme.
   * @param {string} key  – e.g. 'light_technical' | 'dark_professional' | 'blueprint'
   */
  setTheme(key) {
    if (!this.cfg.available_themes[key]) {
      throw new Error(`Unknown theme "${key}". Available: ${this.availableKeys.join(", ")}`);
    }
    this._currentKey = key;
    if (this.cfg.theme_switch.persist) {
      try {
        localStorage.setItem(this.cfg.theme_switch.storage_key, key);
      } catch (_) { /* localStorage unavailable */ }
    }
    this._notifyListeners(key);
  }

  // ── persistence ───────────────────────────────────────────────────────────

  _loadPersistedTheme() {
    if (!this.cfg.theme_switch.persist) return null;
    try {
      return localStorage.getItem(this.cfg.theme_switch.storage_key) || null;
    } catch (_) { return null; }
  }

  // ── listeners ─────────────────────────────────────────────────────────────

  /** Register a callback that fires whenever the theme changes. */
  onChange(fn) { this._listeners.push(fn); }

  _notifyListeners(key) {
    this._listeners.forEach(fn => fn(key, this.currentTheme));
  }

  // ── UI helper ─────────────────────────────────────────────────────────────

  /**
   * Populate a <select> element with the available themes.
   * @param {HTMLSelectElement} selectEl
   */
  populateSelect(selectEl) {
    selectEl.innerHTML = "";
    this.availableKeys.forEach(key => {
      const opt   = document.createElement("option");
      opt.value   = key;
      opt.textContent = key.replace(/_/g, " ").toUpperCase();
      if (key === this._currentKey) opt.selected = true;
      selectEl.appendChild(opt);
    });
    selectEl.addEventListener("change", () => this.setTheme(selectEl.value));
  }
}
