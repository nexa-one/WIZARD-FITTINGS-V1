/**
 * ExportManager – handles export of the current sketch to PDF, PNG, STL and STEP.
 *
 * Dependencies:
 *   PDF  → jsPDF  (CDN: https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js)
 *   STL  → custom binary writer (no external dep)
 *   PNG  → native Canvas.toDataURL / toBlob
 *   STEP → stub (requires backend with OpenCASCADE)
 */
export class ExportManager {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {object}            exportConfig  – config.export section
   */
  constructor(canvas, exportConfig) {
    this.canvas = canvas;
    this.cfg    = exportConfig;
  }

  // ── PNG ───────────────────────────────────────────────────────────────────

  /**
   * Export the current canvas as a PNG file.
   * @param {string} [filename='fitting-sketch.png']
   * @param {object} [opts]
   * @param {boolean} [opts.transparent=false]  – preserve alpha channel
   */
  exportPNG(filename = "fitting-sketch.png", { transparent = false } = {}) {
    const cfg   = this.cfg.formats.png;
    if (!cfg.enabled) throw new Error("PNG export is disabled");

    const dataURL = this.canvas.toDataURL("image/png");
    this._downloadDataURL(dataURL, filename);
  }

  // ── PDF (via jsPDF) ───────────────────────────────────────────────────────

  /**
   * Export the current canvas view as a PDF page.
   * Requires jsPDF to be loaded (window.jspdf or import).
   *
   * @param {string} [filename='fitting-sketch.pdf']
   * @param {object} [opts]
   * @param {string} [opts.pageSize='A4']
   * @param {string} [opts.orientation='landscape']
   */
  exportPDF(filename = "fitting-sketch.pdf", { pageSize = "A4", orientation = "landscape" } = {}) {
    const cfg = this.cfg.formats.pdf;
    if (!cfg.enabled) throw new Error("PDF export is disabled");

    const jsPDF = (typeof window !== "undefined" && window.jspdf)
      ? window.jspdf.jsPDF
      : null;

    if (!jsPDF) {
      // Fallback: open canvas data URL in new tab and let user print to PDF
      console.warn("[ExportManager] jsPDF not loaded – opening PNG for manual PDF print.");
      const dataURL = this.canvas.toDataURL("image/png");
      const win = window.open();
      if (win) {
        win.document.write(
          `<style>body{margin:0}img{width:100%;height:auto}</style>` +
          `<img src="${dataURL}">`
        );
        win.document.title = filename;
      }
      return;
    }

    const doc = new jsPDF({ orientation, unit: "mm", format: pageSize.toLowerCase() });
    const pgW = doc.internal.pageSize.getWidth();
    const pgH = doc.internal.pageSize.getHeight();

    const imgData = this.canvas.toDataURL("image/png");
    doc.addImage(imgData, "PNG", 5, 5, pgW - 10, pgH - 10);
    doc.save(filename);
  }

  // ── STL (binary) ─────────────────────────────────────────────────────────

  /**
   * Export the fitting geometry as a binary STL file.
   * @param {object} geometry  – output of FittingGeometry.generateGeometry()
   * @param {string} [filename='fitting.stl']
   */
  exportSTL(geometry, filename = "fitting.stl") {
    const cfg = this.cfg.formats.stl;
    if (!cfg.enabled) throw new Error("STL export is disabled");

    const triangles = this._triangulateGeometry(geometry);
    const buffer    = this._writeBinarySTL(triangles);
    this._downloadBuffer(buffer, filename, "model/stl");
  }

  /** Build triangle list from face vertex indices and projected 3-D vertices. */
  _triangulateGeometry(geometry) {
    const verts = geometry.vertices;
    const tris  = [];

    for (const face of geometry.faces) {
      const idx = face.indices;
      // Fan triangulation from first vertex
      for (let i = 1; i < idx.length - 1; i++) {
        const v0 = verts[idx[0]];
        const v1 = verts[idx[i]];
        const v2 = verts[idx[i + 1]];
        const n  = this._computeNormal(v0, v1, v2);
        tris.push({ n, v0, v1, v2 });
      }
    }
    return tris;
  }

  _computeNormal(v0, v1, v2) {
    const ax = v1[0] - v0[0], ay = v1[1] - v0[1], az = v1[2] - v0[2];
    const bx = v2[0] - v0[0], by = v2[1] - v0[1], bz = v2[2] - v0[2];
    const nx = ay * bz - az * by;
    const ny = az * bx - ax * bz;
    const nz = ax * by - ay * bx;
    const len = Math.sqrt(nx*nx + ny*ny + nz*nz) || 1;
    return [nx/len, ny/len, nz/len];
  }

  _writeBinarySTL(triangles) {
    // Binary STL: 80-byte header + 4-byte count + N × 50-byte triangle records
    const byteLen = 80 + 4 + triangles.length * 50;
    const buf     = new ArrayBuffer(byteLen);
    const view    = new DataView(buf);
    const LE      = true; // little-endian

    // Header (ASCII, 80 bytes)
    const header  = "WIZARD_FITTINGS_ISOMETRIC_ENGINE STL export";
    for (let i = 0; i < 80; i++) {
      view.setUint8(i, i < header.length ? header.charCodeAt(i) : 0);
    }
    view.setUint32(80, triangles.length, LE);

    let offset = 84;
    for (const { n, v0, v1, v2 } of triangles) {
      const write3 = (arr) => {
        view.setFloat32(offset,     arr[0], LE); offset += 4;
        view.setFloat32(offset,     arr[1], LE); offset += 4;
        view.setFloat32(offset,     arr[2], LE); offset += 4;
      };
      write3(n);  write3(v0); write3(v1); write3(v2);
      view.setUint16(offset, 0, LE); offset += 2; // attribute byte count
    }

    return buf;
  }

  // ── STEP stub ─────────────────────────────────────────────────────────────

  /**
   * Export stub for STEP format. Falls back to STL.
   * Full STEP generation requires a backend with OpenCASCADE.
   * @param {object} geometry
   * @param {string} [filename='fitting.step']
   */
  exportSTEP(geometry, filename = "fitting.step") {
    const cfg = this.cfg.formats.step;
    if (!cfg.enabled) throw new Error("STEP export is disabled");

    console.warn(
      "[ExportManager] STEP export requires a backend with OpenCASCADE. " +
      "Falling back to STL as per config."
    );
    const stlFile = filename.replace(/\.step$/i, ".stl");
    this.exportSTL(geometry, stlFile);
  }

  // ── helpers ───────────────────────────────────────────────────────────────

  // Fix 1: append/remove anchor to DOM so Firefox triggers the download.
  _downloadDataURL(dataURL, filename) {
    const a    = document.createElement("a");
    a.href     = dataURL;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  _downloadBuffer(buffer, filename, mimeType) {
    const blob = new Blob([buffer], { type: mimeType });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
}
