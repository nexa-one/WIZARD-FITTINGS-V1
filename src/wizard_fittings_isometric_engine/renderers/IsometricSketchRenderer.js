/**
 * IsometricSketchRenderer
 *
 * Canvas 2D renderer that produces a technical-drawing-style isometric sketch:
 *  • White background with light isometric grid
 *  • Black solid/dashed object lines
 *  • Blue dimension lines with filled-triangle arrows
 *  • Face shading (three tones of near-white)
 *  • Annotations panel (bottom-left)
 *  • Title block (bottom-right)
 *
 * Usage:
 *   const r = new IsometricSketchRenderer(canvas, config);
 *   r.render(fittingJSON, geometry);
 */

import { IsometricProjection } from "../geometry/IsometricProjection.js";

export class IsometricSketchRenderer {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {object} config  – merged engine config
   */
  constructor(canvas, config) {
    this.canvas  = canvas;
    this.ctx     = canvas.getContext("2d");
    this.config  = config;

    // viewport state (managed by ViewportController)
    this.scale   = 1.0;   // px / mm  (auto-computed on first render)
    this.panX    = 0;
    this.panY    = 0;
  }

  // ── main entry ─────────────────────────────────────────────────────────────

  /**
   * Full render of a fitting.
   * @param {object} fitting   – fitting JSON (id, type, name, dimensions, metadata, render_options)
   * @param {object} geometry  – output of FittingGeometry.generateGeometry()
   */
  render(fitting, geometry) {
    const ctx    = this.ctx;
    const cfg    = this.config;
    const theme  = this._activeTheme();
    const skCfg  = cfg.output_mode.sketch_isometric;

    ctx.save();
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Background
    ctx.fillStyle = theme.background;
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Auto-scale on first render or if requested
    const proj = this._buildProjection(geometry.vertices);

    // Projected 2-D vertices
    const pts = proj.projectAll(geometry.vertices);

    if (skCfg.grid.visible && fitting.render_options?.show_grid !== false) {
      this._drawGrid(proj, theme);
    }

    if (skCfg.face_shading.enabled) {
      this._drawFaces(geometry.faces, pts, theme);
    }

    if (fitting.render_options?.show_hidden !== false) {
      this._drawEdges(geometry.edges, pts, "hidden",    skCfg.object_lines, theme);
    }
    this._drawEdges(geometry.edges, pts, "visible",   skCfg.object_lines, theme);
    this._drawEdges(geometry.edges, pts, "silhouette", skCfg.object_lines, theme);

    if (fitting.render_options?.show_dims !== false) {
      this._drawDimensions(geometry.dimensions, proj, skCfg.dimension_lines, theme);
    }

    this._drawAnnotationsPanel(fitting, skCfg, theme);
    this._drawTitleBlock(fitting, skCfg, theme);

    ctx.restore();
  }

  // ── projection setup ───────────────────────────────────────────────────────

  _buildProjection(vertices) {
    if (!vertices || vertices.length === 0) {
      return new IsometricProjection({
        scale: 0.5,
        originX: this.canvas.width  / 2,
        originY: this.canvas.height / 2,
      });
    }

    // Compute bounding box of projected vertices using unit scale
    const unitProj = new IsometricProjection({ scale: 1, originX: 0, originY: 0 });
    const unitPts  = unitProj.projectAll(vertices);
    const minX = Math.min(...unitPts.map(p => p.x));
    const maxX = Math.max(...unitPts.map(p => p.x));
    const minY = Math.min(...unitPts.map(p => p.y));
    const maxY = Math.max(...unitPts.map(p => p.y));

    const padH = 160; // px padding for dims
    const padV = 180;
    const drawW = this.canvas.width  - padH;
    const drawH = this.canvas.height - padV;

    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;
    const autoScale = Math.min(drawW / rangeX, drawH / rangeY) * 0.65 * this.scale;

    // Centre in the top half (bottom reserved for panels)
    const cx = this.canvas.width  / 2  + this.panX;
    const cy = (this.canvas.height - 120) / 2 + this.panY;

    const ox = cx - autoScale * (minX + maxX) / 2;
    const oy = cy - autoScale * (minY + maxY) / 2;

    return new IsometricProjection({ scale: autoScale, originX: ox, originY: oy });
  }

  // ── grid ───────────────────────────────────────────────────────────────────

  _drawGrid(proj, theme) {
    const ctx = this.ctx;
    const cfg = this.config.output_mode.sketch_isometric.grid;
    const W   = this.canvas.width;
    const H   = this.canvas.height;

    ctx.save();
    ctx.strokeStyle = theme.grid;
    ctx.lineWidth   = cfg.line_width;
    ctx.setLineDash([]);

    // Draw isometric grid lines using the projection's axis vectors.
    // We draw a set of lines parallel to each iso axis across the viewport.
    const ax = proj.axisVectors;
    const step = proj.scale * 50; // grid cell every 50 mm in world space

    const drawFamily = (dx, dy) => {
      // Number of lines needed to cover the viewport diagonally
      const n = Math.ceil(Math.max(W, H) * 2.5 / Math.max(Math.abs(dx), Math.abs(dy), 1)) + 2;
      const perpMag = Math.sqrt(dx * dx + dy * dy);
      const perpX   = -dy / perpMag;
      const perpY   =  dx / perpMag;

      for (let i = -n; i <= n; i++) {
        const ox = i * perpX * step;
        const oy = i * perpY * step;
        ctx.beginPath();
        ctx.moveTo(ox - dx * n, oy - dy * n);
        ctx.lineTo(ox + dx * n, oy + dy * n);
        ctx.stroke();
      }
    };

    ctx.save();
    ctx.translate(proj.originX, proj.originY);
    drawFamily(ax.x.dx, ax.x.dy);
    drawFamily(ax.y.dx, ax.y.dy);
    ctx.restore();

    ctx.restore();
  }

  // ── faces (shading) ────────────────────────────────────────────────────────

  _drawFaces(faces, pts, theme) {
    const ctx = this.ctx;
    const shadeMap = {
      top:    theme.face_top,
      front:  theme.face_right,
      right:  theme.face_right,
      left:   theme.face_left,
      back:   theme.face_left,
      bottom: theme.face_left,
    };

    for (const face of faces) {
      const color = shadeMap[face.faceType] || theme.face_top;
      if (!color) continue;

      ctx.save();
      ctx.fillStyle = color;
      ctx.beginPath();
      face.indices.forEach((vi, i) => {
        const p = pts[vi];
        if (i === 0) ctx.moveTo(p.x, p.y);
        else         ctx.lineTo(p.x, p.y);
      });
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
  }

  // ── edges ──────────────────────────────────────────────────────────────────

  _drawEdges(edges, pts, filterType, lineCfg, theme) {
    const ctx  = this.ctx;
    const spec = lineCfg[
      filterType === "hidden"    ? "hidden_edges"  :
      filterType === "silhouette"? "silhouette"     : "visible_edges"
    ];

    ctx.save();
    ctx.strokeStyle = theme.lines || spec.color;
    if (filterType === "hidden") {
      ctx.strokeStyle = spec.color;
      ctx.setLineDash(spec.dash || [4, 3]);
    } else if (filterType === "silhouette") {
      ctx.setLineDash([]);
    } else {
      ctx.setLineDash([]);
    }
    ctx.lineWidth = spec.width;
    ctx.lineCap   = "round";

    for (const e of edges) {
      if (e.type !== filterType) continue;
      const p1 = pts[e.v1];
      const p2 = pts[e.v2];
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }

    ctx.restore();
  }

  // ── dimensions ─────────────────────────────────────────────────────────────

  _drawDimensions(dimensions, proj, dimCfg, theme) {
    const ctx    = this.ctx;
    const offset = dimCfg.offset_px;
    const color  = theme.dimensions || dimCfg.color;

    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle   = color;
    ctx.font        = `${dimCfg.font_weight} ${dimCfg.font_size_px}px ${dimCfg.font}`;
    ctx.lineWidth   = dimCfg.extension_line_width;
    ctx.setLineDash([]);

    for (const dim of dimensions) {
      if (dim.type === "linear") {
        this._drawLinearDim(dim, proj, offset, color, dimCfg);
      } else if (dim.type === "angular") {
        this._drawAngularDim(dim, proj, offset, color, dimCfg);
      }
    }

    ctx.restore();
  }

  _drawLinearDim(dim, proj, baseOffset, color, dimCfg) {
    const ctx  = this.ctx;
    const p1s  = proj.projectArray(dim.p1);
    const p2s  = proj.projectArray(dim.p2);

    // Determine offset direction (perpendicular to the dimension line in iso space)
    const axis = dim.axis;
    const ax   = proj.axisVectors;
    let perpX, perpY;

    // Perpendicular to dimension axis for offset placement
    if (axis === "x") {
      perpX = -ax.z.dx; perpY = -ax.z.dy - 1;  // offset upward
    } else if (axis === "y") {
      perpX =  ax.z.dx; perpY =  ax.z.dy - 1;
    } else { // z
      perpX = -ax.x.dx - ax.y.dx;
      perpY = -(ax.x.dy + ax.y.dy);
    }
    const perpLen = Math.sqrt(perpX * perpX + perpY * perpY) || 1;
    const pnx     = perpX / perpLen;
    const pny     = perpY / perpLen;

    const off = baseOffset;
    const ep1 = { x: p1s.x + pnx * off, y: p1s.y + pny * off };
    const ep2 = { x: p2s.x + pnx * off, y: p2s.y + pny * off };

    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle   = color;
    ctx.lineWidth   = dimCfg.extension_line_width;

    // Extension lines
    ctx.beginPath();
    ctx.moveTo(p1s.x + pnx * 3, p1s.y + pny * 3);
    ctx.lineTo(ep1.x + pnx * 3, ep1.y + pny * 3);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(p2s.x + pnx * 3, p2s.y + pny * 3);
    ctx.lineTo(ep2.x + pnx * 3, ep2.y + pny * 3);
    ctx.stroke();

    // Dimension line
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(ep1.x, ep1.y);
    ctx.lineTo(ep2.x, ep2.y);
    ctx.stroke();

    // Arrows
    this._drawArrow(ep1.x, ep1.y, ep2.x, ep2.y, dimCfg.arrow_length_px, color);
    this._drawArrow(ep2.x, ep2.y, ep1.x, ep1.y, dimCfg.arrow_length_px, color);

    // Label
    const val   = typeof dim.value === "number" ? dim.value.toFixed(1) : dim.value;
    const label = `${dim.label} ${val} ${dim.unit}`;
    const mx    = (ep1.x + ep2.x) / 2;
    const my    = (ep1.y + ep2.y) / 2;
    ctx.font    = `bold ${dimCfg.font_size_px}px ${dimCfg.font}`;
    ctx.fillStyle   = color;
    ctx.textAlign   = "center";
    ctx.textBaseline = "middle";

    // White halo for readability
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth   = 3;
    ctx.strokeText(label, mx + pnx * 6, my + pny * 6);
    ctx.fillText(label, mx + pnx * 6, my + pny * 6);

    ctx.restore();
  }

  _drawAngularDim(dim, proj, baseOffset, color, dimCfg) {
    const ctx    = this.ctx;
    const center = proj.projectArray(dim.center);
    const ep1    = proj.projectArray(dim.p1);
    const ep2    = proj.projectArray(dim.p2);

    const r = baseOffset + 20;
    const a1 = Math.atan2(ep1.y - center.y, ep1.x - center.x);
    const a2 = Math.atan2(ep2.y - center.y, ep2.x - center.x);

    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle   = color;
    ctx.lineWidth   = 0.8;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(center.x, center.y, r, a1, a2);
    ctx.stroke();

    // Label
    const aMid  = (a1 + a2) / 2;
    const lx    = center.x + (r + 10) * Math.cos(aMid);
    const ly    = center.y + (r + 10) * Math.sin(aMid);
    const label = `${dim.label} ${dim.value}°`;
    ctx.font         = `bold ${dimCfg.font_size_px}px ${dimCfg.font}`;
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";
    ctx.strokeStyle  = "#FFFFFF";
    ctx.lineWidth    = 3;
    ctx.strokeText(label, lx, ly);
    ctx.fillStyle = color;
    ctx.fillText(label, lx, ly);
    ctx.restore();
  }

  _drawArrow(fromX, fromY, toX, toY, size, color) {
    const ctx   = this.ctx;
    const angle = Math.atan2(toY - fromY, toX - fromX);
    const ax    = fromX + Math.cos(angle) * size;
    const ay    = fromY + Math.sin(angle) * size;

    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(ax + Math.cos(angle + 2.5) * size * 0.5,
               ay + Math.sin(angle + 2.5) * size * 0.5);
    ctx.lineTo(ax + Math.cos(angle - 2.5) * size * 0.5,
               ay + Math.sin(angle - 2.5) * size * 0.5);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  // ── annotations panel ──────────────────────────────────────────────────────

  _drawAnnotationsPanel(fitting, skCfg, theme) {
    const ctx  = this.ctx;
    const meta = fitting.metadata || {};
    const cw   = this.canvas.width;
    const ch   = this.canvas.height;

    const panelW = 210;
    const rowH   = 14;
    const rows   = [
      ["REQUESTED BY", meta.requested_by || "—"],
      ["PREPARED BY",  meta.prepared_by  || "—"],
      ["DATE",         (meta.created_at  || "").slice(0, 10) || "—"],
      ["URGENCY",      meta.urgency      || "—"],
      ["WORK ORDER",   meta.work_order   || "—"],
      ["PROJECT",      meta.project_name || "—"],
    ];
    if (meta.notes) rows.push(["NOTES", meta.notes.slice(0, 30)]);

    const panelH = rows.length * rowH + 16;
    const px     = 10;
    const py     = ch - panelH - 10;

    ctx.save();

    // Border
    ctx.strokeStyle = theme.lines || "#333";
    ctx.lineWidth   = 0.7;
    ctx.strokeRect(px, py, panelW, panelH);

    ctx.font         = `9px Courier New, monospace`;
    ctx.textBaseline = "top";

    rows.forEach(([label, value], i) => {
      const y = py + 8 + i * rowH;

      // Label
      ctx.fillStyle = theme.annotations || "#555";
      ctx.fillText(label + ":", px + 6, y);

      // Value
      if (label === "URGENCY") {
        const urgColors = {
          LOW: "#4CAF50", MEDIUM: "#FF9800", HIGH: "#F44336", CRITICAL: "#B71C1C",
        };
        ctx.fillStyle = urgColors[value] || (theme.annotations || "#222");
      } else {
        ctx.fillStyle = theme.annotations || "#222";
      }
      ctx.fillText(value, px + 90, y);
    });

    ctx.restore();
  }

  // ── title block ────────────────────────────────────────────────────────────

  _drawTitleBlock(fitting, skCfg, theme) {
    const ctx  = this.ctx;
    const cw   = this.canvas.width;
    const ch   = this.canvas.height;
    const meta = fitting.metadata || {};

    const blockW = 240;
    const rowH   = 18;
    const rows   = [
      ["FITTING",   fitting.name || fitting.type || "—"],
      ["STANDARD",  fitting.standard || "SMACNA"],
      ["SCALE",     "AUTO"],
      ["VIEW",      "ISOMETRIC"],
      ["DATE",      (meta.created_at || "").slice(0, 10) || "—"],
      ["REVISION",  meta.revision || "Rev A"],
    ];
    const blockH = rows.length * rowH + 16;
    const bx     = cw - blockW - 10;
    const by     = ch - blockH - 10;

    ctx.save();
    ctx.strokeStyle = theme.lines || "#111";
    ctx.lineWidth   = 1;
    ctx.strokeRect(bx, by, blockW, blockH);

    // Header
    ctx.fillStyle   = theme.lines || "#111";
    ctx.fillRect(bx, by, blockW, rowH);
    ctx.fillStyle   = theme.background || "#FFF";
    ctx.font        = `bold 10px Courier New, monospace`;
    ctx.textBaseline = "middle";
    ctx.textAlign    = "center";
    ctx.fillText("WIZARD FITTINGS  ·  TECHNICAL SKETCH", bx + blockW / 2, by + rowH / 2);

    ctx.textAlign = "left";
    rows.forEach(([label, value], i) => {
      const y = by + (i + 1) * rowH + 4;
      ctx.font      = `8px Courier New, monospace`;
      ctx.fillStyle = theme.lines || "#555";
      ctx.fillText(label + ":", bx + 6, y + 4);
      ctx.font      = `bold 9px Courier New, monospace`;
      ctx.fillStyle = theme.annotations || "#111";
      ctx.fillText(value, bx + 80, y + 4);

      // Row separator
      ctx.strokeStyle = theme.grid || "#ccc";
      ctx.lineWidth   = 0.4;
      ctx.beginPath();
      ctx.moveTo(bx, by + (i + 1) * rowH + rowH);
      ctx.lineTo(bx + blockW, by + (i + 1) * rowH + rowH);
      ctx.stroke();
    });

    ctx.restore();
  }

  // ── theme helper ───────────────────────────────────────────────────────────

  _activeTheme() {
    const themes = this.config.theming.available_themes;
    const key    = this._currentThemeKey || this.config.theming.default_theme;
    return themes[key] || themes.light_technical;
  }

  setTheme(themeKey) {
    this._currentThemeKey = themeKey;
  }

  setScale(scale) {
    this.scale = Math.max(0.3, Math.min(4.0, scale));
  }

  setPan(x, y) {
    this.panX = x;
    this.panY = y;
  }
}
