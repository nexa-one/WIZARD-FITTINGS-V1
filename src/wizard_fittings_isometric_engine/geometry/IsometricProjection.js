/**
 * IsometricProjection – converts 3-D world coordinates to 2-D isometric
 * screen coordinates using the standard 30° dimetric projection.
 *
 * Axes (right-hand, Z-up):
 *   +X  → screen right-and-down  (30° below horizontal, rightward)
 *   +Y  → screen left-and-down   (30° below horizontal, leftward)
 *   +Z  → screen up
 */
export class IsometricProjection {
  /**
   * @param {object} opts
   * @param {number} [opts.scale=1]     – mm per pixel scaling factor
   * @param {number} [opts.originX=0]   – canvas X origin of world (0,0,0)
   * @param {number} [opts.originY=0]   – canvas Y origin of world (0,0,0)
   */
  constructor({ scale = 1, originX = 0, originY = 0 } = {}) {
    this.scale   = scale;
    this.originX = originX;
    this.originY = originY;
    this._cos30  = Math.sqrt(3) / 2; // ≈ 0.8660
    this._sin30  = 0.5;
  }

  /**
   * Project a 3-D world point to 2-D canvas coordinates.
   * @param {number} wx  world X (mm)
   * @param {number} wy  world Y (mm)
   * @param {number} wz  world Z (mm)
   * @returns {{ x: number, y: number }}
   */
  project(wx, wy, wz) {
    const s = this.scale;
    return {
      x: this.originX + s * (wx - wy) * this._cos30,
      y: this.originY + s * ((wx + wy) * this._sin30 - wz),
    };
  }

  /**
   * Project an array [wx, wy, wz] to canvas {x, y}.
   * @param {number[]} pt
   * @returns {{ x: number, y: number }}
   */
  projectArray([wx, wy, wz]) {
    return this.project(wx, wy, wz);
  }

  /**
   * Project an entire list of 3-D vertices.
   * @param {number[][]} vertices  – array of [x,y,z]
   * @returns {{ x: number, y: number }[]}
   */
  projectAll(vertices) {
    return vertices.map(v => this.projectArray(v));
  }

  /**
   * Return the 2-D isometric unit vectors for each world axis.
   * Useful for drawing axis indicators and dimension offsets.
   */
  get axisVectors() {
    const s = this.scale;
    return {
      x: { dx:  s * this._cos30, dy:  s * this._sin30 },
      y: { dx: -s * this._cos30, dy:  s * this._sin30 },
      z: { dx:  0,               dy: -s               },
    };
  }

  /**
   * Clone with a different scale while keeping the same origin.
   * @param {number} newScale
   * @returns {IsometricProjection}
   */
  withScale(newScale) {
    return new IsometricProjection({
      scale:   newScale,
      originX: this.originX,
      originY: this.originY,
    });
  }

  /**
   * Clone with a different origin.
   * @param {number} ox
   * @param {number} oy
   * @returns {IsometricProjection}
   */
  withOrigin(ox, oy) {
    return new IsometricProjection({
      scale:   this.scale,
      originX: ox,
      originY: oy,
    });
  }
}
