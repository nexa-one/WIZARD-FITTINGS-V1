/**
 * FittingGeometry – generates 3-D wireframe geometry for HVAC/SMACNA fittings.
 *
 * Each generator returns:
 * {
 *   vertices  : [[x,y,z], ...]          – in mm, world space (Z-up, X-right, Y-forward)
 *   edges     : [{v1, v2, type}, ...]   – type: 'visible' | 'hidden' | 'silhouette'
 *   faces     : [{indices, faceType}, ...]  – faceType: 'top'|'front'|'right'|'left'|'back'|'bottom'
 *   dimensions: [{type, p1, p2, label, value, unit, axis?}, ...]
 * }
 *
 * Coordinate conventions:
 *   X – width direction (right)
 *   Y – depth direction (into page / forward)
 *   Z – height direction (up)
 */

// ─── helpers ─────────────────────────────────────────────────────────────────

function edge(v1, v2, type = "visible") { return { v1, v2, type }; }
function face(indices, faceType)        { return { indices, faceType }; }

function linDim(p1, p2, label, value, unit = "mm", axis) {
  return { type: "linear", p1, p2, label, value, unit, axis };
}
function angDim(center, p1, p2, label, value) {
  return { type: "angular", center, p1, p2, label, value, unit: "°" };
}

// ─── individual generators ───────────────────────────────────────────────────

/** 90° Rectangular Elbow – L-shaped prism */
function elbow90(dims) {
  const W  = dims.width            || 300;
  const H  = dims.height           || 200;
  const CR = dims.centerline_radius || dims.depth || W;

  // The elbow body forms an L in the XY plane.
  // Bottom ring (z=0) – 6 vertices tracing the L outer+inner outline:
  //   v0=(0,0)  v1=(W,0)  v2=(W,CR)  v3=(CR,CR)  v4=(CR,W)  v5=(0,W)
  // Top ring  (z=H) – v6…v11
  const bot = [
    [0,  0,  0],   // v0  inlet front-left
    [W,  0,  0],   // v1  inlet front-right
    [W,  CR, 0],   // v2  inner-corner right
    [CR, CR, 0],   // v3  inner-corner pivot
    [CR, W,  0],   // v4  outlet back-right
    [0,  W,  0],   // v5  outlet back-left
  ];
  const top = bot.map(([x, y]) => [x, y, H]);
  const vertices = [...bot, ...top];

  // bottom edges – all hidden (face is downward)
  const botE = [
    edge(0,1,"hidden"), edge(1,2,"hidden"), edge(2,3,"hidden"),
    edge(3,4,"hidden"), edge(4,5,"hidden"), edge(5,0,"hidden"),
  ];
  // top edges – all visible (face is upward, toward camera)
  const topE = [
    edge(6,7,"visible"), edge(7,8,"visible"), edge(8,9,"visible"),
    edge(9,10,"visible"), edge(10,11,"visible"), edge(11,6,"visible"),
  ];
  // vertical edges
  const vertE = [
    edge(0,6,"silhouette"), // far-left outer
    edge(1,7,"silhouette"), // front-right outer
    edge(2,8,"visible"),    // inner corner right
    edge(3,9,"visible"),    // inner corner pivot (may be occluded – still visible in sketch)
    edge(4,10,"visible"),   // outlet corner
    edge(5,11,"hidden"),    // back-left outer
  ];

  const faces = [
    face([6,7,8,9,10,11], "top"),
    face([0,1,7,6],         "front"),   // inlet face, faces -Y
    face([1,2,8,7],         "right"),   // right outer, faces +X
    face([2,3,9,8],         "back"),    // inner corner back
    face([3,4,10,9],        "left"),    // inner corner left
    face([4,5,11,10],       "back"),    // outlet outer
    face([5,0,6,11],        "left"),    // left outer, faces -X
    face([0,1,2,3,4,5],     "bottom"),
  ];

  const dimensions = [
    linDim([0,0,0], [W,0,0],  "W", W,              "mm", "x"),
    linDim([0,0,0], [0,0,H],  "H", H,              "mm", "z"),
    linDim([0,0,0], [0,W,0],  "D", W,              "mm", "y"),
    linDim([0,CR,0],[0,W,0],  "R", CR,             "mm", "y"),
  ];

  return { vertices, edges: [...botE, ...topE, ...vertE], faces, dimensions };
}

/** 45° Rectangular Elbow */
function elbow45(dims) {
  const W = dims.width  || 300;
  const H = dims.height || 200;
  const D = dims.depth  || dims.centerline_radius || W;

  // Approximate as a skewed prism. Front face at y=0, back face shifted +X by D*tan(45°)=D
  // Bottom ring: 4-corner trapezoid
  const vertices = [
    [0, 0,   0], // v0 inlet bottom-left
    [W, 0,   0], // v1 inlet bottom-right
    [W, D,   0], // v2 outlet bottom-right
    [0, D,   0], // v3 outlet bottom-left (shifted by D in both X and Y for 45°)
    [0, 0,   H], // v4 inlet top-left
    [W, 0,   H], // v5 inlet top-right
    [W+D, D, H], // v6 outlet top-right (45° bend offset in X)
    [D,  D,  H], // v7 outlet top-left
  ];

  const edges = [
    // inlet face
    edge(0,1,"visible"), edge(1,5,"visible"), edge(5,4,"visible"), edge(4,0,"visible"),
    // outlet face
    edge(3,2,"hidden"),  edge(2,6,"visible"), edge(6,7,"visible"), edge(7,3,"visible"),
    // body edges
    edge(0,3,"hidden"),  edge(1,2,"visible"), edge(4,7,"visible"), edge(5,6,"visible"),
  ];

  const faces = [
    face([4,5,6,7], "top"),
    face([0,1,5,4], "front"),
    face([1,2,6,5], "right"),
    face([3,2,6,7], "back"),
    face([0,3,7,4], "left"),
    face([0,1,2,3], "bottom"),
  ];

  const dimensions = [
    linDim([0,0,0], [W,0,0],  "W",  W,  "mm", "x"),
    linDim([0,0,0], [0,0,H],  "H",  H,  "mm", "z"),
    angDim([0,D,0],  [0,0,0], [D,D,0], "∠", 45),
  ];

  return { vertices, edges, faces, dimensions };
}

/** Rectangular Tee – T-junction (branch off centre of duct) */
function tee(dims) {
  const W  = dims.width         || 300;
  const H  = dims.height        || 200;
  const D  = dims.depth         || 300;
  const BW = dims.branch_width  || W / 2;
  const BD = dims.branch_depth  || 150;

  // Main duct: x=[0,W], y=[0,D], z=[0,H]   (12 edges of box)
  // Branch duct: x=[(W-BW)/2, (W+BW)/2], y=[-BD,0], z=[0,H]
  const bx0 = (W - BW) / 2;
  const bx1 = (W + BW) / 2;

  const vertices = [
    // Main duct bottom (z=0) v0-v3
    [0, 0, 0], [W, 0, 0], [W, D, 0], [0, D, 0],
    // Main duct top (z=H) v4-v7
    [0, 0, H], [W, 0, H], [W, D, H], [0, D, H],
    // Branch bottom (z=0) v8-v11
    [bx0, -BD, 0], [bx1, -BD, 0], [bx1, 0, 0], [bx0, 0, 0],
    // Branch top (z=H) v12-v15
    [bx0, -BD, H], [bx1, -BD, H], [bx1, 0, H], [bx0, 0, H],
  ];

  const edges = [
    // Main duct bottom (hidden)
    edge(0,1,"hidden"), edge(1,2,"hidden"), edge(2,3,"hidden"), edge(3,0,"hidden"),
    // Main duct top (visible)
    edge(4,5,"visible"), edge(5,6,"visible"), edge(6,7,"visible"), edge(7,4,"visible"),
    // Main duct verticals
    edge(0,4,"silhouette"), edge(1,5,"silhouette"), edge(2,6,"visible"), edge(3,7,"hidden"),
    // Branch bottom (hidden)
    edge(8,9,"hidden"), edge(9,10,"hidden"), edge(10,11,"hidden"), edge(11,8,"hidden"),
    // Branch top (visible)
    edge(12,13,"visible"), edge(13,14,"visible"), edge(14,15,"visible"), edge(15,12,"visible"),
    // Branch verticals
    edge(8,12,"silhouette"), edge(9,13,"silhouette"), edge(10,14,"visible"), edge(11,15,"visible"),
  ];

  const faces = [
    face([4,5,6,7],   "top"),
    face([0,1,5,4],   "front"),
    face([1,2,6,5],   "right"),
    face([12,13,14,15],"top"),
    face([8,9,13,12], "front"),
    face([9,10,14,13],"right"),
  ];

  const dimensions = [
    linDim([0,0,0], [W,0,0], "W",  W,  "mm", "x"),
    linDim([0,0,0], [0,0,H], "H",  H,  "mm", "z"),
    linDim([0,0,0], [0,D,0], "D",  D,  "mm", "y"),
    linDim([bx0,0,0],[bx1,0,0],"BW",BW,"mm","x"),
  ];

  return { vertices, edges, faces, dimensions };
}

/** Rectangular Reducer – transition between two cross-section sizes */
function reducer(dims) {
  const W1 = dims.inlet_width   || dims.width  || 300;
  const H1 = dims.inlet_height  || dims.height || 200;
  const W2 = dims.outlet_width  || W1 * 0.6;
  const H2 = dims.outlet_height || H1 * 0.6;
  const D  = dims.depth         || 300;

  // Centred transition – inlet at y=0, outlet at y=D
  const dx = (W1 - W2) / 2;
  const dz = (H1 - H2) / 2;

  const vertices = [
    // Inlet face (y=0)
    [0,  0, 0],  [W1, 0, 0],  [W1, 0, H1],  [0,  0, H1],  // v0-v3
    // Outlet face (y=D), centred
    [dx, D, dz], [dx+W2, D, dz], [dx+W2, D, dz+H2], [dx, D, dz+H2], // v4-v7
  ];

  const edges = [
    // Inlet face
    edge(0,1,"visible"), edge(1,2,"visible"), edge(2,3,"visible"), edge(3,0,"visible"),
    // Outlet face
    edge(4,5,"visible"), edge(5,6,"visible"), edge(6,7,"visible"), edge(7,4,"visible"),
    // Connecting (transition) edges
    edge(0,4,"hidden"),    edge(1,5,"visible"), edge(2,6,"visible"), edge(3,7,"visible"),
  ];

  const faces = [
    face([3,2,6,7], "top"),
    face([0,1,5,4], "front"),
    face([1,2,6,5], "right"),
    face([0,3,7,4], "left"),
    face([0,1,2,3], "bottom"),
    face([4,5,6,7], "back"),
  ];

  const dimensions = [
    linDim([0,0,0],  [W1,0,0],  "W IN",  W1, "mm", "x"),
    linDim([0,0,H1], [0,0,0],   "H IN",  H1, "mm", "z"),
    linDim([dx,D,dz],[dx+W2,D,dz],"W OUT",W2,"mm","x"),
    linDim([0,0,0],  [0,D,0],   "D",     D,  "mm", "y"),
  ];

  return { vertices, edges, faces, dimensions };
}

/** Parallel Offset */
function offset(dims) {
  const W  = dims.width  || 300;
  const H  = dims.height || 200;
  const D  = dims.depth  || 400;
  const OX = dims.offset_x || W / 2;   // lateral offset
  const OZ = dims.offset_z || 0;

  const vertices = [
    // Inlet face
    [0, 0, 0], [W, 0, 0], [W, 0, H], [0, 0, H],          // v0-v3
    // Mid-section bottom
    [OX, D/2, OZ], [OX+W, D/2, OZ], [OX+W, D/2, H+OZ], [OX, D/2, H+OZ], // v4-v7
    // Outlet face
    [OX, D, OZ], [OX+W, D, OZ], [OX+W, D, H+OZ], [OX, D, H+OZ],  // v8-v11
  ];

  const edges = [
    // Inlet
    edge(0,1,"visible"), edge(1,2,"visible"), edge(2,3,"visible"), edge(3,0,"visible"),
    // Transition 1
    edge(0,4,"hidden"), edge(1,5,"visible"), edge(2,6,"visible"), edge(3,7,"visible"),
    // Mid-section outline
    edge(4,5,"visible"), edge(5,6,"visible"), edge(6,7,"visible"), edge(7,4,"visible"),
    // Transition 2
    edge(4,8,"hidden"), edge(5,9,"visible"), edge(6,10,"visible"), edge(7,11,"visible"),
    // Outlet
    edge(8,9,"visible"), edge(9,10,"visible"), edge(10,11,"visible"), edge(11,8,"visible"),
  ];

  const faces = [
    face([0,1,2,3],   "front"),
    face([8,9,10,11], "back"),
    face([3,2,6,7],   "top"),
    face([7,6,10,11], "top"),
  ];

  const dimensions = [
    linDim([0,0,0],  [W,0,0],  "W",  W,  "mm", "x"),
    linDim([0,0,0],  [0,0,H],  "H",  H,  "mm", "z"),
    linDim([0,0,0],  [0,D,0],  "D",  D,  "mm", "y"),
    linDim([0,0,H],  [OX,D/2,H+OZ], "OX", OX, "mm", "x"),
  ];

  return { vertices, edges, faces, dimensions };
}

/** End Cap */
function cap(dims) {
  const W = dims.width  || 300;
  const H = dims.height || 200;
  const D = 60;  // cap depth, small fixed or from dims

  const vertices = [
    [0, 0, 0], [W, 0, 0], [W, 0, H], [0, 0, H], // v0-v3 inlet face
    [0, D, 0], [W, D, 0], [W, D, H], [0, D, H], // v4-v7 back face (closed)
  ];

  const edges = [
    edge(0,1,"visible"), edge(1,2,"visible"), edge(2,3,"visible"), edge(3,0,"visible"),
    edge(4,5,"hidden"),  edge(5,6,"visible"), edge(6,7,"visible"), edge(7,4,"visible"),
    edge(0,4,"hidden"), edge(1,5,"visible"), edge(2,6,"visible"), edge(3,7,"visible"),
  ];

  const faces = [
    face([0,1,2,3], "front"),
    face([4,5,6,7], "back"),
    face([3,2,6,7], "top"),
    face([1,2,6,5], "right"),
    face([0,3,7,4], "left"),
    face([0,1,5,4], "bottom"),
  ];

  const dimensions = [
    linDim([0,0,0], [W,0,0], "W", W,  "mm", "x"),
    linDim([0,0,0], [0,0,H], "H", H,  "mm", "z"),
    linDim([0,0,0], [0,D,0], "D", D,  "mm", "y"),
  ];

  return { vertices, edges, faces, dimensions };
}

/** Y-Wye – symmetrical two-branch split */
function wye(dims) {
  const W  = dims.width        || 300;
  const H  = dims.height       || 200;
  const D  = dims.depth        || 300;
  const BW = dims.branch_width || W * 0.7;
  const angle = dims.angle_deg || 45;
  const spread = D * Math.tan((angle / 2) * Math.PI / 180);

  const vertices = [
    // Inlet face (y=0)
    [0, 0, 0], [W, 0, 0], [W, 0, H], [0, 0, H],  // v0-v3
    // Right branch outlet
    [W/2 + spread, D, 0], [W/2 + spread + BW, D, 0],
    [W/2 + spread + BW, D, H], [W/2 + spread, D, H],  // v4-v7
    // Left branch outlet
    [W/2 - spread - BW, D, 0], [W/2 - spread, D, 0],
    [W/2 - spread, D, H], [W/2 - spread - BW, D, H],  // v8-v11
  ];

  const edges = [
    // Inlet
    edge(0,1,"visible"), edge(1,2,"visible"), edge(2,3,"visible"), edge(3,0,"visible"),
    // Right branch face
    edge(4,5,"visible"), edge(5,6,"visible"), edge(6,7,"visible"), edge(7,4,"visible"),
    // Left branch face
    edge(8,9,"visible"), edge(9,10,"visible"), edge(10,11,"visible"), edge(11,8,"visible"),
    // Body top
    edge(2,7,"visible"), edge(3,11,"visible"),
    // Body sides
    edge(0,8,"hidden"), edge(1,4,"visible"),
  ];

  const faces = [
    face([0,1,2,3],   "front"),
    face([4,5,6,7],   "right"),
    face([8,9,10,11], "left"),
  ];

  const dimensions = [
    linDim([0,0,0], [W,0,0], "W", W,    "mm", "x"),
    linDim([0,0,0], [0,0,H], "H", H,    "mm", "z"),
    linDim([0,0,0], [0,D,0], "D", D,    "mm", "y"),
    angDim([W/2,0,0], [0,0,0], [W/2+spread,D,0], "∠", angle),
  ];

  return { vertices, edges, faces, dimensions };
}

/** Shape Transition – rectangular to round or different shape */
function transition(dims) {
  // Modelled as a pyramid-like frustum with rectangular cross-sections
  const W1 = dims.inlet_width   || dims.width  || 300;
  const H1 = dims.inlet_height  || dims.height || 200;
  const W2 = dims.outlet_width  || 200;
  const H2 = dims.outlet_height || 150;
  const D  = dims.depth         || 250;

  // Centred outlet
  const dx = (W1 - W2) / 2;
  const dz = (H1 - H2) / 2;

  const vertices = [
    [0,  0, 0],  [W1, 0, 0],  [W1, 0, H1],  [0,  0, H1], // inlet  v0-v3
    [dx, D, dz], [dx+W2, D, dz], [dx+W2, D, dz+H2], [dx, D, dz+H2], // outlet v4-v7
  ];

  const edges = [
    edge(0,1,"visible"), edge(1,2,"visible"), edge(2,3,"visible"), edge(3,0,"visible"),
    edge(4,5,"visible"), edge(5,6,"visible"), edge(6,7,"visible"), edge(7,4,"visible"),
    edge(0,4,"hidden"),  edge(1,5,"visible"), edge(2,6,"visible"), edge(3,7,"visible"),
  ];

  const faces = [
    face([3,2,6,7], "top"),
    face([0,1,5,4], "front"),
    face([1,2,6,5], "right"),
  ];

  const dimensions = [
    linDim([0,0,0],    [W1,0,0],    "W IN",  W1, "mm", "x"),
    linDim([0,0,H1],   [0,0,0],     "H IN",  H1, "mm", "z"),
    linDim([dx,D,dz],  [dx+W2,D,dz],"W OUT", W2, "mm", "x"),
    linDim([0,0,0],    [0,D,0],     "D",     D,  "mm", "y"),
  ];

  return { vertices, edges, faces, dimensions };
}

// ─── registry ────────────────────────────────────────────────────────────────

const GENERATORS = {
  elbow_90:   elbow90,
  elbow_45:   elbow45,
  tee:        tee,
  reducer:    reducer,
  offset:     offset,
  cap:        cap,
  wye:        wye,
  transition: transition,
};

// ─── public API ──────────────────────────────────────────────────────────────

/**
 * Generate geometry for a given fitting type and dimensions.
 * @param {string} type    – fitting type key (e.g. 'elbow_90')
 * @param {object} dims    – dimension object from fitting JSON
 * @returns {{ vertices, edges, faces, dimensions }}
 */
export function generateGeometry(type, dims = {}) {
  const gen = GENERATORS[type];
  if (!gen) {
    throw new Error(`Unknown fitting type: "${type}". Valid types: ${Object.keys(GENERATORS).join(", ")}`);
  }
  return gen(dims);
}

export const SUPPORTED_TYPES = Object.keys(GENERATORS);
