/**
 * CoordinateCube – Fusion360-style XYZ orientation cube rendered on a small
 * <canvas> or into a corner of the main canvas.
 *
 * The cube shows the three axis labels (X, Y, Z) coloured red/green/blue and
 * rotates with the current isometric view angle.
 */
export class CoordinateCube {
  /**
   * @param {HTMLCanvasElement} canvas  – dedicated small canvas element
   * @param {object}            config  – engine config (coordinate_cube section)
   */
  constructor(canvas, config) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext("2d");
    this.config = config.coordinate_cube;
    this.size   = this.config.size_px || 80;
    canvas.width  = this.size;
    canvas.height = this.size;
  }

  /**
   * Draw the cube for the given isometric rotation angle (in degrees, 0 = standard ISO).
   * @param {number} [rotDeg=0]  – Y-axis rotation in degrees
   * @param {string} [theme='light_technical']
   */
  draw(rotDeg = 0, theme = "light_technical") {
    const ctx  = this.ctx;
    const s    = this.size;
    const cx   = s / 2;
    const cy   = s / 2;
    const r    = s * 0.28;  // axis arm length
    const rot  = (rotDeg * Math.PI) / 180;

    ctx.clearRect(0, 0, s, s);

    // Background circle
    const bg = theme === "dark_professional" ? "#1A2030"
             : theme === "blueprint"         ? "#0A2463"
             :                                 "#F0F0F0";
    ctx.fillStyle = bg;
    ctx.beginPath();
    ctx.arc(cx, cy, s / 2 - 2, 0, Math.PI * 2);
    ctx.fill();

    // Border
    ctx.strokeStyle = theme === "light_technical" ? "#CCCCCC" : "#444";
    ctx.lineWidth   = 1;
    ctx.stroke();

    // Axis colours from config
    const axCfg = this.config.axes;
    const isoDeg = 30 * Math.PI / 180;

    // Project the three axis tips using current rotation
    const axes = [
      { label: axCfg.x.label, color: axCfg.x.color,
        dx:  Math.cos(rot) * r,         dy: Math.sin(isoDeg) * r },
      { label: axCfg.y.label, color: axCfg.y.color,
        dx: -Math.cos(rot + Math.PI / 3) * r * 0.8,
        dy:  Math.sin(isoDeg) * r },
      { label: axCfg.z.label, color: axCfg.z.color,
        dx:  0,                          dy: -r },
    ];

    axes.forEach(({ label, color, dx, dy }) => {
      // Axis line
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth   = 2;
      ctx.lineCap     = "round";
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + dx, cy + dy);
      ctx.stroke();

      // Arrow tip
      const angle = Math.atan2(dy, dx);
      const tipX  = cx + dx;
      const tipY  = cy + dy;
      const al    = 6;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(tipX, tipY);
      ctx.lineTo(tipX - al * Math.cos(angle - 0.4), tipY - al * Math.sin(angle - 0.4));
      ctx.lineTo(tipX - al * Math.cos(angle + 0.4), tipY - al * Math.sin(angle + 0.4));
      ctx.closePath();
      ctx.fill();

      // Label
      const textColor = theme === "light_technical" ? "#333" : "#EEE";
      ctx.fillStyle   = textColor;
      ctx.font        = "bold 10px Courier New, monospace";
      ctx.textAlign   = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(label, cx + dx * 1.35, cy + dy * 1.35);

      ctx.restore();
    });

    // Centre dot
    ctx.fillStyle = theme === "light_technical" ? "#555" : "#CCC";
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fill();
  }
}
