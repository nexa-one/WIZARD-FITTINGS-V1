/**
 * WIZARD_FITTINGS_ISOMETRIC_ENGINE – Default Configuration
 * Version 1.0.0
 */

export const ENGINE_NAME    = "WIZARD_FITTINGS_ISOMETRIC_ENGINE";
export const ENGINE_VERSION = "1.0.0";

export const DEFAULT_CONFIG = {
  output_mode: {
    default: "sketch_isometric",
    available_modes: ["sketch_isometric", "3d_visual"],

    sketch_isometric: {
      background: "#FFFFFF",
      grid: {
        visible: true,
        color: "#E8E8E8",
        type: "isometric",
        angle_deg: 30,
        line_width: 0.4,
      },
      object_lines: {
        visible_edges: { color: "#111111", width: 1.8, style: "solid" },
        hidden_edges:  { color: "#AAAAAA", width: 0.6, style: "dashed", dash: [4, 3] },
        silhouette:    { color: "#000000", width: 2.4, style: "solid" },
      },
      dimension_lines: {
        color: "#1A56DB",
        text_color: "#1A56DB",
        font: "Courier New, monospace",
        font_size_px: 10,
        font_weight: "bold",
        arrow_style: "filled_triangle",
        arrow_length_px: 6,
        extension_line_color: "#4B7BE8",
        extension_line_width: 0.6,
        offset_px: 20,
        show: [
          "width", "height", "depth", "angles",
          "inlet_diameter", "outlet_diameter", "centerline_radius",
        ],
      },
      face_shading: {
        enabled: true,
        top_face:   "#F9F9F9",
        left_face:  "#ECECEC",
        right_face: "#E0E0E0",
      },
      title_block: {
        position: "bottom_right",
        border: { color: "#111111", width: 1 },
        font: "Courier New, monospace",
        fields: ["fitting_name", "scale", "view_type", "date", "revision"],
      },
    },

    "3d_visual": {
      renderer: "WebGL",
      background: "#1A1A2E",
      material: "matte_neutral",
      colors: {
        body:    "#B0B8C1",
        flange:  "#8A9BB0",
        opening: "#6C7A89",
      },
      lighting: {
        ambient_intensity: 0.5,
        directional: [
          { direction: [1, 2, 1],   intensity: 0.8, color: "#FFFFFF" },
          { direction: [-1, 0, -1], intensity: 0.3, color: "#AACCFF" },
        ],
      },
      environment: "studio_neutral",
    },

    mode_switch: {
      ui_control: "toggle_button",
      label_sketch: "SKETCH",
      label_3d: "3D VIEW",
      transition_ms: 300,
    },
  },

  dimensions: {
    units: "mm",
    decimal_places: 1,
    show_all_by_default: true,
    fields: {
      width:             { label: "W",     color: "#1A56DB" },
      height:            { label: "H",     color: "#1A56DB" },
      depth:             { label: "D",     color: "#1A56DB" },
      inlet_diameter:    { label: "Ø IN",  color: "#1565C0" },
      outlet_diameter:   { label: "Ø OUT", color: "#1565C0" },
      angle:             { label: "∠",     color: "#0D47A1" },
      centerline_radius: { label: "R",     color: "#0D47A1" },
      wall_thickness:    { label: "T",     color: "#5C6BC0" },
    },
  },

  annotations_panel: {
    position: "bottom_left",
    style: {
      background: "transparent",
      border: "1px solid #333",
      font: "Courier New, monospace",
      font_size: 9,
      text_color: "#222222",
      label_color: "#555555",
    },
    fields: [
      { key: "requested_by", label: "REQUESTED BY", type: "string",   required: true  },
      { key: "prepared_by",  label: "PREPARED BY",  type: "string",   required: true  },
      { key: "created_at",   label: "DATE",          type: "date",     required: true, format: "YYYY-MM-DD" },
      {
        key: "urgency", label: "URGENCY", type: "enum", required: true,
        options: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        colors: { LOW: "#4CAF50", MEDIUM: "#FF9800", HIGH: "#F44336", CRITICAL: "#B71C1C" },
      },
      { key: "work_order",   label: "WORK ORDER", type: "string",   required: false },
      { key: "project_name", label: "PROJECT",    type: "string",   required: false },
      { key: "notes",        label: "NOTES",      type: "textarea", required: false },
    ],
  },

  coordinate_cube: {
    enabled: true,
    style: "fusion360",
    position: "top_right",
    size_px: 80,
    axes: {
      x: { label: "X", color: "#E53935" },
      y: { label: "Y", color: "#43A047" },
      z: { label: "Z", color: "#1E88E5" },
    },
    clickable: true,
    snap_to_views: ["FRONT", "BACK", "LEFT", "RIGHT", "TOP", "BOTTOM", "ISO"],
  },

  viewport_controls: {
    zoom: {
      enabled: true,
      min_scale: 0.3,
      max_scale: 4.0,
      step: 0.1,
      controls: ["scroll_wheel", "pinch_gesture", "+/- buttons"],
    },
    pan: {
      enabled: true,
      controls: ["middle_click_drag", "space+drag"],
    },
    rotate: {
      enabled: true,
      mode: "isometric_snap",
      snap_angles: [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
      controls: ["right_click_drag"],
    },
  },

  export: {
    formats: {
      pdf: {
        enabled: true,
        page_sizes: ["A4", "A3", "Letter"],
        orientation: ["portrait", "landscape"],
        dpi: 300,
        include_title_block: true,
        include_annotations: true,
        color_mode: ["color", "grayscale", "black_and_white"],
        library: "jspdf",
      },
      stl: {
        enabled: true,
        type: "binary",
        units: "mm",
        precision: 0.01,
        note: "Generated from the fitting's parametric geometry",
        library: "three.js STLExporter",
      },
      step: {
        enabled: true,
        standard: "ISO-10303-21",
        note: "Requires backend with OpenCASCADE or equivalent",
        fallback: "stl",
      },
      png: {
        enabled: true,
        resolution: "2x",
        background: "white",
        transparent_option: true,
      },
    },
    ui: {
      export_button: "bottom_toolbar",
      format_selector: "dropdown",
    },
  },

  module_integration: {
    ai_module: {
      flow: "user_input → AI_extraction → JSON_fitting → sketch_render",
      input_types: ["text_description", "image_upload", "pdf_spec"],
      output: "fitting_json",
      auto_render: true,
      fields_extracted: ["type", "dimensions", "angles", "material", "standard"],
    },
    parametric_module: {
      flow: "manual_inputs → parameter_change → live_sketch_update",
      update_mode: "real_time",
      debounce_ms: 150,
      inputs: ["width", "height", "depth", "angle", "inlet_d", "outlet_d", "radius"],
    },
    wizard_module: {
      flow: "step_selection → fitting_choice → sketch_per_step",
      sketch_preview: "inline_per_step",
      final_view: "full_sketch_with_all_dims",
    },
  },

  theming: {
    default_theme: "light_technical",
    available_themes: {
      light_technical: {
        background:    "#FFFFFF",
        lines:         "#111111",
        dimensions:    "#1A56DB",
        annotations:   "#222222",
        grid:          "#E8E8E8",
        ui_background: "#F5F5F5",
        ui_text:       "#111111",
        accent:        "#1A56DB",
        face_top:      "#F9F9F9",
        face_left:     "#ECECEC",
        face_right:    "#E0E0E0",
      },
      dark_professional: {
        background:    "#12161C",
        lines:         "#E0E0E0",
        dimensions:    "#4FC3F7",
        annotations:   "#B0BEC5",
        grid:          "#1E2530",
        ui_background: "#0D1117",
        ui_text:       "#E0E0E0",
        accent:        "#4FC3F7",
        face_top:      "#1E2530",
        face_left:     "#191F28",
        face_right:    "#141A22",
      },
      blueprint: {
        background:    "#0A2463",
        lines:         "#FFFFFF",
        dimensions:    "#90CAF9",
        annotations:   "#BBDEFB",
        grid:          "#0D2E7A",
        ui_background: "#071A4F",
        ui_text:       "#E3F2FD",
        accent:        "#64B5F6",
        face_top:      "#0D2E7A",
        face_left:     "#0A2463",
        face_right:    "#071A4F",
      },
    },
    theme_switch: {
      ui_control: "dropdown",
      persist: true,
      storage_key: "wizard_sketch_theme",
    },
  },

  fitting_schema: {
    description: "Standard JSON schema for any generated fitting",
    example: {
      id: "ELBOW-90-300x200",
      type: "elbow_90",
      name: "90° Elbow SMACNA",
      standard: "SMACNA HVAC Duct Construction Standards 3rd Ed.",
      material: "Galvanized Steel 26ga",
      dimensions: {
        width: 300, height: 200, depth: 300,
        inlet_width: 300, inlet_height: 200,
        outlet_width: 300, outlet_height: 200,
        angle_deg: 90,
        centerline_radius: 150,
        wall_thickness: 0.55,
      },
      metadata: {
        requested_by: "John Smith",
        prepared_by: "Wizard Fittings AI",
        created_at: "2026-03-05T00:00:00Z",
        urgency: "HIGH",
        work_order: "WO-2026-0312",
        project_name: "HVAC Tower A - Level 3",
        revision: "Rev A",
        notes: "Throat radius per SMACNA Table 4-2. Verify gauge with contractor.",
      },
      render_options: {
        mode: "sketch_isometric",
        theme: "light_technical",
        show_dims: true,
        show_hidden: true,
        show_grid: true,
      },
    },
  },
};
