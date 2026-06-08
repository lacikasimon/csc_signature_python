DEMO_HTML = """
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSC PDF Signer & Stamper Demo</title>
  <style>
    :root {
      color-scheme: light;
      --app-bg: #eef3f8;
      --surface: #ffffff;
      --surface-soft: #f7fafc;
      --ink: #102033;
      --muted: #637083;
      --line: #d5dee8;
      --line-strong: #bac8d6;
      --teal: #0b3b82;
      --teal-dark: #082b63;
      --teal-soft: #eaf1ff;
      --green: #1f9d55;
      --blue: #2563eb;
      --danger: #b42318;
      --document-shadow: 0 12px 28px rgba(15, 23, 42, 0.16);
      --shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
      --shadow-soft: 0 1px 2px rgba(15, 23, 42, 0.08);
    }

    * { box-sizing: border-box; }

    html,
    body {
      height: 100%;
    }

    body {
      margin: 0;
      background: var(--app-bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      letter-spacing: 0;
    }

    button,
    input,
    select,
    textarea {
      font: inherit;
    }

    button,
    label[for="pdfFile"],
    a {
      -webkit-tap-highlight-color: transparent;
    }

    .app {
      height: 100vh;
      display: grid;
      grid-template-rows: 64px minmax(0, 1fr) 30px;
      padding: 4px;
      gap: 4px;
    }

    .topbar {
      min-width: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 0 22px;
      color: var(--teal-dark);
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 250, 255, 0.98)),
        #ffffff;
      border: 1px solid #dbe4f0;
      border-radius: 6px;
      box-shadow: var(--shadow);
    }

    .brand {
      min-width: 0;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-mark {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      color: #fff;
      border: 2px solid #dbe8ff;
      border-radius: 999px;
      background:
        radial-gradient(circle at center, #1b5fb5 0 44%, #0b3b82 45% 100%);
      box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.35);
    }

    .brand-mark svg {
      width: 24px;
      height: 24px;
      stroke: currentColor;
    }

    .brand-title {
      display: flex;
      align-items: center;
      gap: 9px;
      min-width: 0;
      margin-bottom: 2px;
    }

    .brand-title h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.1;
      white-space: nowrap;
    }

    .demo-badge {
      border: 1px solid rgba(255, 255, 255, 0.7);
      border-radius: 4px;
      padding: 2px 8px;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0;
      color: var(--teal-dark);
      border-color: #a9b9d2;
    }

    .brand-subtitle {
      margin: 0;
      color: #415878;
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .topbar-actions {
      display: flex;
      align-items: center;
      gap: 14px;
      flex: 0 0 auto;
    }

    .secure-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      color: #087443;
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }

    .toolbar-button,
    .icon-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 34px;
      border: 1px solid var(--line-strong);
      border-radius: 6px;
      color: var(--ink);
      background: #fff;
      cursor: pointer;
      box-shadow: var(--shadow-soft);
    }

    .settings-button {
      min-height: 38px;
      padding: 0 14px;
      border-color: #cad5e5;
      color: var(--teal-dark);
      background: #fff;
    }

    .language-select {
      min-height: 38px;
      min-width: 128px;
      border: 1px solid #cad5e5;
      border-radius: 6px;
      padding: 0 38px 0 14px;
      color: var(--teal-dark);
      background: #fff;
      font-weight: 800;
      box-shadow: var(--shadow-soft);
    }

    .workspace {
      min-height: 0;
      display: grid;
      grid-template-columns: minmax(360px, 424px) minmax(0, 1fr);
      gap: 8px;
    }

    .sidebar,
    .main-panel,
    .footer {
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid var(--line);
      border-radius: 6px;
      box-shadow: var(--shadow-soft);
    }

    .sidebar {
      min-height: 0;
      overflow: auto;
      padding: 12px 16px 0;
    }

    .step {
      padding: 10px 0 12px;
      border-bottom: 1px solid #e8edf3;
    }

    .step:last-of-type {
      border-bottom: 0;
    }

    .step-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }

    .step-title {
      margin: 0;
      font-size: 15px;
      line-height: 1.2;
      font-weight: 800;
      color: #17324a;
    }

    .upload-zone {
      min-height: 104px;
      display: grid;
      place-items: center;
      gap: 8px;
      padding: 16px;
      border: 1px dashed #b8c7d5;
      border-radius: 6px;
      background: linear-gradient(180deg, #fbfdff, #f5f8fb);
      color: var(--teal);
      text-align: center;
      cursor: pointer;
    }

    .upload-zone strong {
      display: block;
      color: #27364a;
      margin-top: 4px;
    }

    .file-button {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 16px;
      border-radius: 5px;
      color: #fff;
      background: var(--teal-dark);
      font-weight: 800;
      box-shadow: var(--shadow-soft);
    }

    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    .file-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 10px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }

    .file-row.hidden {
      display: none;
    }

    .pdf-chip {
      width: 28px;
      height: 34px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid #ef4444;
      border-radius: 4px;
      color: #ef4444;
      font-size: 10px;
      font-weight: 900;
    }

    .file-meta {
      min-width: 0;
      flex: 1 1 auto;
    }

    .file-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 800;
      color: #1d3146;
    }

    .file-size {
      margin-top: 2px;
      color: var(--muted);
      font-size: 12px;
    }

    .ok-dot {
      width: 17px;
      height: 17px;
      display: inline-grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid #20b15a;
      border-radius: 999px;
      color: #20b15a;
      font-size: 12px;
      font-weight: 900;
    }

    .sidebar-layer.hidden {
      display: none;
    }

    .detail-nav {
      display: grid;
      grid-template-columns: 36px minmax(0, 1fr);
      align-items: center;
      gap: 10px;
    }

    .back-button {
      width: 34px;
      height: 34px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line-strong);
      border-radius: 5px;
      color: var(--teal-dark);
      background: #fff;
      cursor: pointer;
      box-shadow: var(--shadow-soft);
    }

    .detail-title {
      min-width: 0;
      display: grid;
      gap: 2px;
    }

    .detail-title h2 {
      margin: 0;
      overflow: hidden;
      color: #17324a;
      font-size: 15px;
      line-height: 1.15;
      font-weight: 900;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .detail-title span {
      overflow: hidden;
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .mode-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 8px;
    }

    .mode-button {
      min-height: 50px;
      display: inline-flex;
      align-items: center;
      justify-content: flex-start;
      gap: 10px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: #fff;
      color: #526172;
      font-weight: 800;
      cursor: pointer;
      text-align: left;
    }

    .mode-button svg {
      width: 18px;
      height: 18px;
    }

    .mode-copy {
      min-width: 0;
      display: grid;
      gap: 2px;
    }

    .mode-copy strong {
      overflow: hidden;
      color: #1e3147;
      font-size: 12px;
      line-height: 1.1;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .mode-copy span {
      overflow: hidden;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.15;
      font-weight: 700;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .mode-button.active {
      color: #fff;
      border-color: var(--teal);
      background: linear-gradient(180deg, #0f4c9a, #0a3475);
      box-shadow: 0 8px 18px rgba(11, 59, 130, 0.20);
    }

    .mode-button.active .mode-copy strong,
    .mode-button.active .mode-copy span {
      color: #fff;
    }

    .switch {
      position: relative;
      display: inline-flex;
      width: 28px;
      height: 16px;
      flex: 0 0 auto;
    }

    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .slider {
      position: absolute;
      inset: 0;
      border-radius: 999px;
      background: #cfd8e3;
      cursor: pointer;
      transition: background 0.16s ease;
    }

    .slider::after {
      content: "";
      position: absolute;
      width: 12px;
      height: 12px;
      left: 2px;
      top: 2px;
      border-radius: 999px;
      background: #fff;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.28);
      transition: transform 0.16s ease;
    }

    .switch input:checked + .slider {
      background: var(--teal);
    }

    .switch input:checked + .slider::after {
      transform: translateX(12px);
    }

    .section-body.collapsed {
      display: none;
    }

    .function-section-hidden {
      display: none;
    }

    .function-section .step-header .switch {
      display: none;
    }

    .field {
      min-width: 0;
      margin-bottom: 8px;
    }

    .field label,
    .field-label {
      display: block;
      margin-bottom: 5px;
      color: #34495f;
      font-size: 11px;
      font-weight: 800;
    }

    .control-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 10px;
    }

    .triple-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px 10px;
    }

    .input-wrap {
      display: flex;
      align-items: stretch;
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: #fff;
      overflow: hidden;
    }

    input,
    textarea {
      width: 100%;
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 7px 8px;
      color: var(--ink);
      background: #fff;
      outline-color: rgba(11, 59, 130, 0.25);
    }

    .input-wrap input {
      border: 0;
      border-radius: 0;
    }

    textarea {
      min-height: 48px;
      resize: vertical;
    }

    .unit {
      min-width: 42px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 8px;
      color: var(--muted);
      border-left: 1px solid #eef2f6;
      background: #f8fafc;
      font-size: 12px;
    }

    input[type="range"] {
      padding: 0;
      accent-color: var(--teal);
    }

    .range-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 44px;
      align-items: center;
      gap: 8px;
      min-height: 31px;
    }

    .range-value {
      color: var(--muted);
      font-size: 12px;
      text-align: right;
    }

    .color-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 2px;
    }

    .color-control {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 33px;
      padding: 5px 7px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: #fff;
    }

    .color-control input {
      width: 36px;
      height: 24px;
      padding: 0;
      border: 0;
      background: transparent;
      cursor: pointer;
    }

    .radio-row {
      display: flex;
      align-items: center;
      gap: 12px;
      min-height: 30px;
      flex-wrap: wrap;
    }

    .radio-row label {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: #526172;
      font-size: 12px;
      font-weight: 800;
    }

    .radio-row input {
      width: 14px;
      height: 14px;
      margin: 0;
      accent-color: var(--blue);
    }

    .signature-box-fields.hidden,
    .seal-box-fields.hidden {
      display: none;
    }

    .token-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 34px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: #fff;
      overflow: hidden;
    }

    .token-row input {
      border: 0;
      border-radius: 0;
    }

    .token-row button {
      border: 0;
      border-left: 1px solid #eef2f6;
      color: #526172;
      background: #fff;
      cursor: pointer;
    }

    .placeholder-actions {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 8px;
      margin-bottom: 10px;
    }

    .mini-action {
      min-height: 32px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      border: 1px solid #cbd7e6;
      border-radius: 5px;
      color: var(--teal-dark);
      background: #fff;
      font-size: 12px;
      font-weight: 900;
      cursor: pointer;
      box-shadow: var(--shadow-soft);
    }

    .mini-action.danger {
      color: var(--danger);
    }

    .mini-action:disabled {
      cursor: not-allowed;
      opacity: 0.48;
    }

    .placeholder-list {
      display: grid;
      gap: 6px;
      margin-bottom: 10px;
    }

    .placeholder-item {
      min-height: 34px;
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      padding: 7px 8px;
      border: 1px solid var(--line);
      border-radius: 5px;
      color: #415878;
      background: #fff;
      cursor: pointer;
      text-align: left;
    }

    .placeholder-item.active {
      border-color: #4f46e5;
      color: #1e1b4b;
      background: #eef2ff;
    }

    .placeholder-index {
      width: 22px;
      height: 22px;
      display: inline-grid;
      place-items: center;
      border-radius: 999px;
      color: #fff;
      background: #4f46e5;
      font-size: 11px;
      font-weight: 900;
    }

    .placeholder-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 12px;
      font-weight: 900;
    }

    .placeholder-page {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
    }

    .sidebar-actions {
      position: sticky;
      bottom: 0;
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 8px;
      padding: 10px 0 12px;
      background: linear-gradient(rgba(255, 255, 255, 0), #fff 22%);
    }

    .sidebar-actions.hidden {
      display: none;
    }

    .primary-action,
    .download-action {
      min-height: 40px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      border: 0;
      border-radius: 5px;
      color: #fff;
      font-weight: 900;
      text-decoration: none;
      cursor: pointer;
      box-shadow: var(--shadow-soft);
    }

    .primary-action {
      background: linear-gradient(180deg, #0f4c9a, #0a3475);
    }

    .primary-action:disabled {
      opacity: 0.65;
      cursor: wait;
    }

    .download-action {
      background: #8faed6;
    }

    .download-action[aria-disabled="true"] {
      pointer-events: none;
      opacity: 0.56;
    }

    .icon-button[aria-disabled="true"] {
      pointer-events: none;
      opacity: 0.52;
    }

    .main-panel {
      min-width: 0;
      min-height: 0;
      display: grid;
      grid-template-rows: 44px 48px minmax(0, 1fr) 58px;
      overflow: hidden;
    }

    .status-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 0 40px;
      border-bottom: 1px solid #e8edf3;
      background: #fff;
    }

    .status-left {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .status-label {
      color: #1e2f43;
      font-weight: 900;
    }

    .status-message {
      color: var(--green);
      font-weight: 800;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .status-message.error {
      color: var(--danger);
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 0 38px 0 12px;
      border-bottom: 1px solid #e8edf3;
      background: linear-gradient(180deg, #fbfdff, #f4f8fb);
    }

    .preview-tabs {
      display: inline-flex;
      align-self: stretch;
      gap: 8px;
    }

    .preview-tabs button {
      min-width: 134px;
      border: 0;
      border-bottom: 3px solid transparent;
      color: #486176;
      background: transparent;
      font-weight: 900;
      cursor: pointer;
    }

    .preview-tabs button.active {
      color: var(--teal-dark);
      border-color: var(--teal);
      background: #fff;
    }

    .viewer-tools {
      display: flex;
      align-items: center;
      gap: 10px;
      color: #526172;
    }

    .page-input {
      width: 44px;
      height: 30px;
      padding: 0 8px;
      text-align: center;
    }

    .zoom-group {
      display: inline-grid;
      grid-template-columns: 30px 60px 30px;
      height: 30px;
      border: 1px solid var(--line);
      border-radius: 5px;
      overflow: hidden;
      background: #fff;
    }

    .zoom-group button,
    .zoom-group span {
      border: 0;
      background: #fff;
      display: inline-grid;
      place-items: center;
      color: #526172;
    }

    .zoom-group button {
      cursor: pointer;
      font-size: 18px;
    }

    .zoom-group span {
      border-left: 1px solid #eef2f6;
      border-right: 1px solid #eef2f6;
      font-size: 12px;
      font-weight: 800;
    }

    .icon-button {
      width: 34px;
      height: 30px;
      padding: 0;
    }

    .viewer {
      position: relative;
      min-width: 0;
      min-height: 0;
      overflow: auto;
      background:
        radial-gradient(circle at center, rgba(11, 59, 130, 0.08), transparent 46%),
        linear-gradient(180deg, #eef3fa, #e7edf5);
      padding: 14px 18px 10px;
    }

    .frame-shell {
      min-height: 100%;
      display: grid;
      place-items: start center;
    }

    .placement-editor {
      width: min(100%, 720px);
      min-height: 100%;
      display: grid;
      place-items: start center;
    }

    .placement-editor.hidden {
      display: none;
    }

    .placement-canvas {
      position: relative;
      display: inline-block;
      max-width: 100%;
      max-height: calc(100vh - 226px);
      background: #fff;
      border: 1px solid #d4dce6;
      box-shadow: var(--document-shadow);
      user-select: none;
      touch-action: none;
    }

    .placement-canvas img {
      display: block;
      width: auto;
      max-width: 100%;
      max-height: calc(100vh - 226px);
      height: auto;
      pointer-events: none;
    }

    .placement-box {
      position: absolute;
      display: grid;
      place-items: center;
      min-width: 28px;
      min-height: 20px;
      border: 2px solid var(--teal);
      border-radius: 5px;
      color: var(--teal);
      background: rgba(255, 255, 255, 0.88);
      font-size: clamp(10px, 1.1vw, 15px);
      font-weight: 900;
      line-height: 1.15;
      text-align: center;
      cursor: move;
      text-transform: uppercase;
      touch-action: none;
      user-select: none;
      will-change: left, top, width, height;
      box-shadow: 0 4px 12px rgba(11, 59, 130, 0.18);
    }

    .placement-box.signature {
      border-color: var(--blue);
      color: var(--blue);
      background: rgba(255, 255, 255, 0.86);
      align-content: center;
      justify-items: center;
      gap: 2px;
      padding: 6px 8px;
      text-transform: none;
    }

    .placement-box.seal {
      border-color: #118a56;
      color: #0e7148;
      background: rgba(238, 252, 246, 0.9);
      align-content: center;
      justify-items: center;
      gap: 2px;
      padding: 6px 8px;
      text-transform: uppercase;
    }

    .placeholder-layer {
      position: absolute;
      inset: 0;
      pointer-events: none;
    }

    .placeholder-layer .placement-box {
      pointer-events: auto;
    }

    .placement-box.placeholder {
      border-color: #4f46e5;
      color: #3730a3;
      background: rgba(238, 242, 255, 0.9);
      align-content: center;
      justify-items: center;
      gap: 2px;
      padding: 6px 8px;
      text-transform: none;
    }

    .placement-box.placeholder.active {
      border-color: #1d4ed8;
      color: #1d4ed8;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.16), 0 4px 12px rgba(11, 59, 130, 0.18);
    }

    .placeholder-caption {
      font-size: 10px;
      font-weight: 900;
      color: #1f3150;
      text-align: center;
    }

    .seal-mark {
      width: 30px;
      height: 30px;
      display: inline-grid;
      place-items: center;
      border: 2px solid currentColor;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 900;
      line-height: 1;
    }

    .seal-caption {
      font-size: 9px;
      font-weight: 900;
      color: #174333;
      text-align: center;
      text-transform: none;
    }

    .sig-script {
      font-family: "Segoe Script", "Brush Script MT", cursive;
      font-size: clamp(14px, 2vw, 22px);
      line-height: 1;
      color: #1d63d6;
    }

    .sig-caption {
      font-size: 9px;
      font-weight: 800;
      color: #1f3150;
      text-align: center;
    }

    .placement-box.hidden {
      display: none;
    }

    .resize-handle {
      position: absolute;
      right: -6px;
      bottom: -6px;
      width: 12px;
      height: 12px;
      border: 2px solid #fff;
      border-radius: 999px;
      background: currentColor;
      cursor: nwse-resize;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.28);
    }

    .placement-hint {
      width: min(100%, 720px);
      margin: 8px 0 0;
      color: #526172;
      font-size: 12px;
      font-weight: 700;
      text-align: center;
    }

    iframe {
      width: min(100%, 720px);
      height: calc(100vh - 226px);
      min-height: 520px;
      border: 1px solid #d4dce6;
      background: #fff;
      box-shadow: var(--document-shadow);
    }

    iframe.hidden {
      display: none;
    }

    .empty-state {
      width: min(100%, 720px);
      min-height: 520px;
      display: grid;
      place-items: center;
      border: 1px solid #d4dce6;
      background: #f8fafc;
      color: #6d7887;
      font-weight: 900;
      box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10);
    }

    .empty-state.hidden {
      display: none;
    }

    .result-actions {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto auto;
      align-items: center;
      gap: 12px;
      padding: 8px 22px;
      border-top: 1px solid #dfe7f0;
      background: #fff;
    }

    .result-status {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      color: #516176;
    }

    .result-status strong {
      display: block;
      color: #16345c;
      font-size: 12px;
      line-height: 1.15;
    }

    .result-status span:last-child {
      display: block;
      overflow: hidden;
      color: #66758a;
      font-size: 11px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .result-status.error strong,
    .result-status.error span:last-child {
      color: var(--danger);
    }

    .result-button {
      min-height: 34px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 0 18px;
      border: 1px solid #cbd7e6;
      border-radius: 5px;
      color: var(--teal-dark);
      background: #fff;
      font-size: 12px;
      font-weight: 900;
      text-decoration: none;
      cursor: pointer;
      box-shadow: var(--shadow-soft);
    }

    .result-button.primary {
      min-width: 190px;
      color: #fff;
      border-color: var(--teal);
      background: linear-gradient(180deg, #0f4c9a, #0a3475);
    }

    .result-button[aria-disabled="true"] {
      pointer-events: none;
      opacity: 0.55;
    }

    .log-panel {
      position: absolute;
      top: 102px;
      right: 26px;
      width: min(360px, calc(100% - 52px));
      z-index: 10;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .log-panel.hidden {
      display: none;
    }

    .log-panel header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 12px;
      border-bottom: 1px solid #e8edf3;
      font-weight: 900;
    }

    .log-panel button {
      border: 0;
      background: transparent;
      cursor: pointer;
      color: #526172;
    }

    .log-list {
      max-height: 240px;
      overflow: auto;
      margin: 0;
      padding: 10px 12px 12px 28px;
      color: #43566c;
      font-size: 12px;
    }

    .footer {
      min-width: 0;
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      align-items: center;
      gap: 10px;
      padding: 0 20px;
      color: #768397;
      font-size: 11px;
    }

    .footer span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    svg {
      width: 16px;
      height: 16px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
      flex: 0 0 auto;
    }

    @media (max-width: 1050px) {
      .app {
        height: auto;
        min-height: 100vh;
        grid-template-rows: auto auto auto;
      }

      .topbar {
        flex-wrap: wrap;
        min-height: 64px;
        padding: 12px 16px;
      }

      .workspace {
        grid-template-columns: 1fr;
      }

      .sidebar {
        max-height: none;
      }

      .main-panel {
        min-height: 680px;
      }

      .placement-canvas,
      .placement-canvas img {
        max-height: none;
      }
    }

    @media (max-width: 680px) {
      .topbar-actions,
      .secure-pill,
      .viewer-tools {
        display: none;
      }

      .brand-title h1 {
        font-size: 18px;
        white-space: normal;
      }

      .brand-title {
        flex-wrap: wrap;
      }

      .demo-badge {
        display: none;
      }

      .brand-subtitle {
        white-space: normal;
      }

      .mode-grid,
      .control-grid,
      .triple-grid,
      .color-grid,
      .footer {
        grid-template-columns: 1fr;
      }

      .status-bar,
      .toolbar {
        padding-left: 14px;
        padding-right: 14px;
      }

      .preview-tabs {
        width: 100%;
      }

      .preview-tabs button {
        min-width: 0;
        flex: 1 1 auto;
      }

      .viewer {
        padding: 8px;
      }

      .result-actions {
        grid-template-columns: 1fr;
        align-items: stretch;
      }

      iframe,
      .placement-editor,
      .empty-state {
        min-height: 520px;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M8 10h8"></path>
            <path d="M9 10v6"></path>
            <path d="M12 10v6"></path>
            <path d="M15 10v6"></path>
            <path d="M7 16h10"></path>
            <path d="m12 5 6 4H6Z"></path>
          </svg>
        </div>
        <div>
          <div class="brand-title">
            <h1>CSC PDF SIGNER &amp; STAMPER DEMO</h1>
            <span class="demo-badge">DEMO</span>
          </div>
          <p class="brand-subtitle">
            Semnarea și ștampilarea documentelor prin serviciul CSC
          </p>
        </div>
      </div>
      <div class="topbar-actions">
        <span class="secure-pill">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 3 20 6v6c0 5-3.4 8-8 9-4.6-1-8-4-8-9V6l8-3Z"></path>
            <path d="m9 12 2 2 4-5"></path>
          </svg>
          Conexiune securizată
        </span>
        <button class="toolbar-button settings-button" type="button">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M9.5 9a2.5 2.5 0 0 1 4.8.9c0 1.9-2.3 2.2-2.3 4"></path>
            <path d="M12 17h.01"></path>
          </svg>
          Ajutor
        </button>
        <select class="language-select" aria-label="Limba interfeței">
          <option selected>Română</option>
        </select>
      </div>
    </header>

    <div class="workspace">
      <aside class="sidebar">
        <section class="step">
          <div class="step-header">
            <h2 class="step-title">1. ÎNCĂRCARE PDF</h2>
          </div>
          <input id="pdfFile" class="visually-hidden" name="pdf" type="file" accept="application/pdf">
          <label class="upload-zone" for="pdfFile">
            <svg viewBox="0 0 24 24" aria-hidden="true" style="width:42px;height:42px">
              <path d="M16 16 12 12 8 16"></path>
              <path d="M12 12v9"></path>
              <path d="M20.4 18.4A5 5 0 0 0 18 9h-1.3A8 8 0 1 0 4 16.3"></path>
            </svg>
            <strong>Trageți și plasați fișierul PDF aici</strong>
            <span>sau</span>
            <span class="file-button">Alege fișier</span>
          </label>
          <div id="selectedFileRow" class="file-row hidden">
            <div class="pdf-chip">PDF</div>
            <div class="file-meta">
              <div id="selectedFileName" class="file-name">-</div>
              <div id="selectedFileSize" class="file-size">-</div>
            </div>
            <span class="ok-dot">✓</span>
          </div>
        </section>

        <div id="functionMenuLayer" class="sidebar-layer">
          <section class="step">
            <div class="step-header">
              <h2 class="step-title">2. FUNCȚII</h2>
            </div>
            <div class="mode-grid" role="tablist" aria-label="Mod de operare">
              <button class="mode-button" type="button" data-mode="sign" aria-pressed="false">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 20h9"></path>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"></path>
                </svg>
                <span class="mode-copy">
                  <strong>Semnare</strong>
                  <span>O singură semnătură CSC</span>
                </span>
              </button>
              <button class="mode-button" type="button" data-mode="stamp" aria-pressed="false">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M7 21h10"></path>
                  <path d="M9 17h6"></path>
                  <path d="M12 3v8"></path>
                  <path d="M8 11h8l1 6H7Z"></path>
                </svg>
                <span class="mode-copy">
                  <strong>Ștampilă</strong>
                  <span>Marcaj vizibil pe document</span>
                </span>
              </button>
              <button class="mode-button active" type="button" data-mode="both" aria-pressed="true">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 20h9"></path>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"></path>
                  <path d="M4 7h7"></path>
                </svg>
                <span class="mode-copy">
                  <strong>Semnare + Ștampilă</strong>
                  <span>Semnare CSC cu ștampilă</span>
                </span>
              </button>
              <button class="mode-button" type="button" data-mode="placeholders" aria-pressed="false">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"></path>
                  <path d="M14 2v6h6"></path>
                  <path d="M8 14h8"></path>
                  <path d="M8 18h5"></path>
                </svg>
                <span class="mode-copy">
                  <strong>Semnături multiple</strong>
                  <span>Poziții pentru mai mulți semnatari</span>
                </span>
              </button>
              <button class="mode-button" type="button" data-mode="seal" aria-pressed="false">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 3 20 6v6c0 5-3.4 8-8 9-4.6-1-8-4-8-9V6l8-3Z"></path>
                  <path d="M9 12h6"></path>
                  <path d="M12 9v6"></path>
                </svg>
                <span class="mode-copy">
                  <strong>Sigiliu electronic</strong>
                  <span>Sigiliu instituțional CSC</span>
                </span>
              </button>
            </div>
          </section>
        </div>

        <div id="functionDetailLayer" class="sidebar-layer hidden">
          <section class="step">
            <div class="detail-nav">
              <button id="backToFunctionList" class="back-button" type="button" aria-label="Înapoi la lista funcțiilor">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="m15 18-6-6 6-6"></path>
                </svg>
              </button>
              <div class="detail-title">
                <h2 id="detailTitle">Funcție</h2>
                <span id="detailSubtitle">Configurați opțiunile funcției selectate</span>
              </div>
            </div>
          </section>

        <section id="stampSection" class="step function-section">
          <div class="step-header">
            <h2 class="step-title">SETĂRI ȘTAMPILĂ</h2>
            <label class="switch" aria-label="Setări ștampilă">
              <input id="stampToggle" type="checkbox" checked>
              <span class="slider"></span>
            </label>
          </div>
          <div id="stampPanel" class="section-body">
            <div class="control-grid">
              <div class="field">
                <label for="stampText">Text ștampilă</label>
                <input id="stampText" type="text" value="APROBAT">
              </div>
              <div class="field">
                <label for="stampPage">Pagina</label>
                <div class="input-wrap">
                  <input id="stampPage" type="number" min="1" value="1">
                  <span class="unit">/ <span class="page-count">1</span></span>
                </div>
              </div>
              <div class="field">
                <label for="stampX">Poziție X</label>
                <div class="input-wrap">
                  <input id="stampX" type="number" min="0" value="120">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="stampY">Poziție Y</label>
                <div class="input-wrap">
                  <input id="stampY" type="number" min="0" value="180">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="stampWidth">Lățime</label>
                <div class="input-wrap">
                  <input id="stampWidth" type="number" min="1" value="60">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="stampHeight">Înălțime</label>
                <div class="input-wrap">
                  <input id="stampHeight" type="number" min="1" value="30">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="stampFont">Dimensiune font</label>
                <div class="input-wrap">
                  <input id="stampFont" type="number" min="1" max="72" value="14">
                  <span class="unit">pt</span>
                </div>
              </div>
              <div class="field">
                <label for="stampOpacity">Transparență fundal</label>
                <div class="range-row">
                  <input id="stampOpacity" type="range" min="0" max="1" step="0.05" value="0.30">
                  <span id="stampOpacityValue" class="range-value">30%</span>
                </div>
              </div>
              <div class="field">
                <label for="stampBorder">Grosime chenar</label>
                <div class="range-row">
                  <input id="stampBorder" type="range" min="0" max="20" step="0.5" value="1.5">
                  <span id="stampBorderValue" class="range-value">1.5 pt</span>
                </div>
              </div>
            </div>
            <div class="color-grid">
              <div>
                <span class="field-label">Culoare text</span>
                <label class="color-control" for="stampTextColor">
                  <input id="stampTextColor" type="color" value="#0b3b82">
                  <span>#0b3b82</span>
                </label>
              </div>
              <div>
                <span class="field-label">Culoare chenar</span>
                <label class="color-control" for="stampBorderColor">
                  <input id="stampBorderColor" type="color" value="#0b3b82">
                  <span>#0b3b82</span>
                </label>
              </div>
            </div>
          </div>
        </section>

        <section id="signatureSection" class="step function-section">
          <div class="step-header">
            <h2 class="step-title">SETĂRI SEMNĂTURĂ</h2>
            <label class="switch" aria-label="Setări semnătură">
              <input id="signatureToggle" type="checkbox" checked>
              <span class="slider"></span>
            </label>
          </div>
          <div id="signaturePanel" class="section-body">
            <div class="field">
              <label for="fieldName">Nume câmp</label>
              <input id="fieldName" type="text" value="Director Juridic">
            </div>
            <div class="field">
              <label for="reason">Motiv</label>
              <input id="reason" type="text" value="Aprobare contract">
            </div>
            <div class="field">
              <label for="location">Locație</label>
              <input id="location" type="text" value="București, România">
            </div>
            <div class="field">
              <span class="field-label">Tip semnătură</span>
              <div class="radio-row">
                <label>
                  <input id="visibleSignature" type="radio" name="signatureVisibility" value="visible" checked>
                  Semnătură vizibilă
                </label>
                <label>
                  <input id="invisibleSignature" type="radio" name="signatureVisibility" value="invisible">
                  Semnătură invizibilă
                </label>
              </div>
            </div>
            <div id="signatureBoxFields" class="signature-box-fields">
              <div class="triple-grid">
                <div class="field">
                  <label for="sigPage">Pagina</label>
                  <div class="input-wrap">
                    <input id="sigPage" type="number" min="1" value="1">
                    <span class="unit">/ <span class="page-count">1</span></span>
                  </div>
                </div>
                <div class="field">
                  <label for="sigX">Poziție X</label>
                  <div class="input-wrap">
                    <input id="sigX" type="number" min="0" value="120">
                    <span class="unit">mm</span>
                  </div>
                </div>
                <div class="field">
                  <label for="sigY">Poziție Y</label>
                  <div class="input-wrap">
                    <input id="sigY" type="number" min="0" value="240">
                    <span class="unit">mm</span>
                  </div>
                </div>
                <div class="field">
                  <label for="sigWidth">Lățime</label>
                  <div class="input-wrap">
                    <input id="sigWidth" type="number" min="1" value="80">
                    <span class="unit">mm</span>
                  </div>
                </div>
                <div class="field">
                  <label for="sigHeight">Înălțime</label>
                  <div class="input-wrap">
                    <input id="sigHeight" type="number" min="1" value="25">
                    <span class="unit">mm</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="field">
              <label for="token">Token CSC OAuth <span style="font-weight:600;color:#748096">(opțional)</span></label>
              <div class="token-row">
                <input id="token" type="password" autocomplete="off">
                <button id="tokenVisibility" type="button" aria-label="Afișare token">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>

        <section id="placeholdersSection" class="step function-section">
          <div class="step-header">
            <h2 class="step-title">SEMNĂTURI MULTIPLE</h2>
            <label class="switch" aria-label="Poziții pentru semnături multiple">
              <input id="placeholdersToggle" type="checkbox">
              <span class="slider"></span>
            </label>
          </div>
          <div id="placeholdersPanel" class="section-body collapsed">
            <div class="placeholder-actions">
              <button id="addPlaceholderButton" class="mini-action" type="button">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 5v14"></path>
                  <path d="M5 12h14"></path>
                </svg>
                Adaugă poziție
              </button>
              <button id="removePlaceholderButton" class="mini-action danger" type="button">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 6h18"></path>
                  <path d="M8 6V4h8v2"></path>
                  <path d="M19 6l-1 14H6L5 6"></path>
                </svg>
                Șterge poziția
              </button>
            </div>
            <div id="placeholderList" class="placeholder-list" aria-label="Poziții de semnătură"></div>
            <div class="field">
              <label class="radio-row">
                <input id="signFirstPlaceholder" type="checkbox">
                Semnează prima poziție acum
              </label>
            </div>
            <div id="signFirstPanel" class="section-body collapsed">
              <div class="field">
                <label for="placeholderSignReason">Motiv semnare</label>
                <input id="placeholderSignReason" type="text" value="Semnare prima poziție">
              </div>
              <div class="field">
                <label for="placeholderSignLocation">Locație</label>
                <input id="placeholderSignLocation" type="text" value="București, România">
              </div>
              <div class="field">
                <label for="placeholderToken">Token CSC OAuth <span style="font-weight:600;color:#748096">(opțional)</span></label>
                <div class="token-row">
                  <input id="placeholderToken" type="password" autocomplete="off">
                  <button id="placeholderTokenVisibility" type="button" aria-label="Afișare token semnare prima poziție">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            <div class="field">
              <label for="placeholderFieldName">Nume câmp</label>
              <input id="placeholderFieldName" type="text" value="Signature1">
            </div>
            <div class="triple-grid">
              <div class="field">
                <label for="placeholderPage">Pagina</label>
                <div class="input-wrap">
                  <input id="placeholderPage" type="number" min="1" value="1">
                  <span class="unit">/ <span class="page-count">1</span></span>
                </div>
              </div>
              <div class="field">
                <label for="placeholderX">Poziție X</label>
                <div class="input-wrap">
                  <input id="placeholderX" type="number" min="0" value="120">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="placeholderY">Poziție Y</label>
                <div class="input-wrap">
                  <input id="placeholderY" type="number" min="0" value="240">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="placeholderWidth">Lățime</label>
                <div class="input-wrap">
                  <input id="placeholderWidth" type="number" min="1" value="80">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div class="field">
                <label for="placeholderHeight">Înălțime</label>
                <div class="input-wrap">
                  <input id="placeholderHeight" type="number" min="1" value="25">
                  <span class="unit">mm</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="sealSection" class="step function-section">
          <div class="step-header">
            <h2 class="step-title">SIGILIU ELECTRONIC</h2>
            <label class="switch" aria-label="Setări sigiliu electronic">
              <input id="sealToggle" type="checkbox">
              <span class="slider"></span>
            </label>
          </div>
          <div id="sealPanel" class="section-body collapsed">
            <div class="field">
              <label for="sealFieldName">Nume câmp sigiliu</label>
              <input id="sealFieldName" type="text" value="SigiliuElectronic1">
            </div>
            <div class="field">
              <label for="sealReason">Motiv</label>
              <input id="sealReason" type="text" value="Sigiliu electronic instituțional">
            </div>
            <div class="field">
              <label for="sealLocation">Locație</label>
              <input id="sealLocation" type="text" value="București, România">
            </div>
            <div class="field">
              <span class="field-label">Tip sigiliu</span>
              <div class="radio-row">
                <label>
                  <input id="visibleSeal" type="radio" name="sealVisibility" value="visible" checked>
                  Sigiliu vizibil
                </label>
                <label>
                  <input id="invisibleSeal" type="radio" name="sealVisibility" value="invisible">
                  Sigiliu invizibil
                </label>
              </div>
            </div>
            <div id="sealBoxFields" class="seal-box-fields">
              <div class="triple-grid">
                <div class="field">
                  <label for="sealPage">Pagina</label>
                  <div class="input-wrap">
                    <input id="sealPage" type="number" min="1" value="1">
                    <span class="unit">/ <span class="page-count">1</span></span>
                  </div>
                </div>
                <div class="field">
                  <label for="sealX">Poziție X</label>
                  <div class="input-wrap">
                    <input id="sealX" type="number" min="0" value="135">
                    <span class="unit">mm</span>
                  </div>
                </div>
                <div class="field">
                  <label for="sealY">Poziție Y</label>
                  <div class="input-wrap">
                    <input id="sealY" type="number" min="0" value="165">
                    <span class="unit">mm</span>
                  </div>
                </div>
                <div class="field">
                  <label for="sealWidth">Lățime</label>
                  <div class="input-wrap">
                    <input id="sealWidth" type="number" min="1" value="58">
                    <span class="unit">mm</span>
                  </div>
                </div>
                <div class="field">
                  <label for="sealHeight">Înălțime</label>
                  <div class="input-wrap">
                    <input id="sealHeight" type="number" min="1" value="32">
                    <span class="unit">mm</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="field">
              <label for="sealToken">Token CSC sigiliu <span style="font-weight:600;color:#748096">(opțional)</span></label>
              <div class="token-row">
                <input id="sealToken" type="password" autocomplete="off">
                <button id="sealTokenVisibility" type="button" aria-label="Afișare token sigiliu">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>
        </div>

        <div id="sidebarActions" class="sidebar-actions hidden">
          <button id="runButton" class="primary-action" type="button">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8 5v14l11-7Z"></path>
            </svg>
            <span id="runLabel">Rulează semnarea / ștampilarea</span>
          </button>
          <a id="downloadLink" class="download-action" aria-disabled="true">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3v12"></path>
              <path d="m7 10 5 5 5-5"></path>
              <path d="M5 21h14"></path>
            </svg>
            Descarcă rezultatul
          </a>
        </div>
      </aside>

      <main class="main-panel">
        <section class="status-bar">
          <div class="status-left">
            <span class="status-label">Status:</span>
            <span class="ok-dot">✓</span>
            <span id="status" class="status-message">Gata pentru utilizare</span>
          </div>
          <button id="clearButton" class="toolbar-button" type="button">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M3 6h18"></path>
              <path d="M8 6V4h8v2"></path>
              <path d="M19 6l-1 14H6L5 6"></path>
              <path d="M10 11v5"></path>
              <path d="M14 11v5"></path>
            </svg>
            Șterge tot
          </button>
        </section>

        <section class="toolbar">
          <div class="preview-tabs" role="tablist" aria-label="Previzualizare">
            <button type="button" data-preview="input" class="active">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"></path>
                <path d="M14 2v6h6"></path>
              </svg>
              PDF original
            </button>
            <button type="button" data-preview="output">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m20 6-11 11-5-5"></path>
              </svg>
              PDF rezultat
            </button>
          </div>
          <div class="viewer-tools">
            <input id="pageNumber" class="page-input" type="number" min="1" value="1" aria-label="Numărul paginii">
            <span>/ <span class="page-count">1</span></span>
            <div class="zoom-group" aria-label="Zoom">
              <button id="zoomOut" type="button">−</button>
              <span id="zoomLevel">100%</span>
              <button id="zoomIn" type="button">+</button>
            </div>
            <button id="refreshPreview" class="icon-button" type="button" aria-label="Resetează previzualizarea">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M21 12a9 9 0 0 1-15 6.7"></path>
                <path d="M3 12a9 9 0 0 1 15-6.7"></path>
                <path d="M21 4v6h-6"></path>
                <path d="M3 20v-6h6"></path>
              </svg>
            </button>
            <a id="downloadToolbarLink" class="icon-button" aria-disabled="true" aria-label="Descărcare">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3v12"></path>
                <path d="m7 10 5 5 5-5"></path>
                <path d="M5 21h14"></path>
              </svg>
            </a>
          </div>
        </section>

        <section class="viewer">
          <div class="frame-shell">
            <div id="placementEditor" class="placement-editor hidden">
              <div id="placementCanvas" class="placement-canvas">
                <img id="pageImage" alt="Previzualizare pagină PDF">
                <div id="stampBox" class="placement-box" data-placement="stamp">
                  <span id="stampBoxLabel">APROBAT</span>
                  <span class="resize-handle" data-placement="stamp" data-action="resize"></span>
                </div>
                <div id="signatureBox" class="placement-box signature" data-placement="signature">
                  <span class="sig-script">Semnătură</span>
                  <span class="sig-caption">Director Juridic<br>București, România</span>
                  <span class="resize-handle" data-placement="signature" data-action="resize"></span>
                </div>
                <div id="sealBox" class="placement-box seal hidden" data-placement="seal">
                  <span class="seal-mark">SE</span>
                  <span class="seal-caption">Sigiliu electronic<br>Instituție publică</span>
                  <span class="resize-handle" data-placement="seal" data-action="resize"></span>
                </div>
                <div id="placeholderLayer" class="placeholder-layer"></div>
              </div>
              <p class="placement-hint">
                Trageți casetele pe document sau redimensionați-le din colț.
              </p>
            </div>
            <iframe id="outputFrame" title="PDF rezultat" class="hidden"></iframe>
            <div id="emptyState" class="empty-state">Nu a fost selectat niciun PDF</div>
          </div>
          <aside id="logPanel" class="log-panel hidden">
            <header>
              <span>Jurnal procesare</span>
              <button id="logClose" type="button" aria-label="Închide jurnalul">×</button>
            </header>
            <ol id="logList" class="log-list">
              <li>Gata pentru utilizare</li>
            </ol>
          </aside>
        </section>

        <section class="result-actions">
          <div id="resultStatus" class="result-status">
            <span class="ok-dot">✓</span>
            <div>
              <strong id="resultStatusTitle">Pregătit pentru poziționare</strong>
              <span id="resultStatusText">Încărcați un PDF pentru previzualizare vizuală.</span>
            </div>
          </div>
          <button id="resetPreviewButton" class="result-button" type="button">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M21 12a9 9 0 0 1-15 6.7"></path>
              <path d="M3 12a9 9 0 0 1 15-6.7"></path>
              <path d="M21 4v6h-6"></path>
              <path d="M3 20v-6h6"></path>
            </svg>
            Resetează previzualizarea
          </button>
          <a id="downloadResultLink" class="result-button primary" aria-disabled="true">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3v12"></path>
              <path d="m7 10 5 5 5-5"></path>
              <path d="M5 21h14"></path>
            </svg>
            Descarcă rezultatul
          </a>
        </section>
      </main>
    </div>

    <footer class="footer">
      <span>© 2024 Autoritatea pentru Digitalizarea României</span>
      <span>Conexiune securizată (TLS 1.3)</span>
      <span>Politica de confidențialitate</span>
      <span>Termeni și condiții</span>
      <span>Versiune: 1.0.0 &nbsp; DEMO</span>
    </footer>
  </div>

  <script>
    const state = {
      mode: "both",
      sidebarLayer: "menu",
      activePreview: "input",
      inputUrl: null,
      pageImageUrl: null,
      outputUrl: null,
      outputName: "rezultat-semnat.pdf",
      pageCount: 1,
      pageWidth: 0,
      pageHeight: 0,
      renderSeq: 0,
      drag: null,
      zoom: 100,
      placeholders: [
        {
          id: 1,
          fieldName: "Signature1",
          page: 1,
          x: 120,
          y: 240,
          width: 80,
          height: 25
        }
      ],
      activePlaceholderId: 1,
      nextPlaceholderId: 2
    };

    const $ = (id) => document.getElementById(id);
    const PT_PER_MM = 72 / 25.4;
    const modeButtons = [...document.querySelectorAll("[data-mode]")];
    const previewButtons = [...document.querySelectorAll("[data-preview]")];
    const modeDetails = {
      sign: {
        title: "Semnare",
        subtitle: "Configurați semnătura CSC pentru document."
      },
      stamp: {
        title: "Ștampilă",
        subtitle: "Configurați marcajul vizibil aplicat pe PDF."
      },
      both: {
        title: "Semnare + Ștampilă",
        subtitle: "Configurați semnătura CSC și ștampila."
      },
      placeholders: {
        title: "Semnături multiple",
        subtitle: "Pregătiți pozițiile pentru mai mulți semnatari."
      },
      seal: {
        title: "Sigiliu electronic",
        subtitle: "Configurați sigiliul electronic instituțional."
      }
    };

    function numberValue(id) {
      return Number($(id).value);
    }

    function pageIndex(id) {
      return Math.max(0, numberValue(id) - 1);
    }

    function mmToPt(value) {
      return value * PT_PER_MM;
    }

    function ptToMm(value) {
      return value / PT_PER_MM;
    }

    function roundMm(value) {
      return Math.round(value * 10) / 10;
    }

    function roundPt(value) {
      return Math.round(value);
    }

    function setStatus(message, isError = false) {
      const status = $("status");
      status.textContent = message;
      status.classList.toggle("error", isError);
      $("resultStatus").classList.toggle("error", isError);
      const item = document.createElement("li");
      item.textContent = message;
      $("logList").prepend(item);
    }

    function setResultStatus(title, text, isError = false) {
      $("resultStatusTitle").textContent = title;
      $("resultStatusText").textContent = text;
      $("resultStatus").classList.toggle("error", isError);
    }

    function formatSize(bytes) {
      if (bytes < 1024) {
        return `${bytes} B`;
      }
      if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
      }
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    function actionLabelForMode(mode) {
      if (mode === "stamp") {
        return "Rulează ștampilarea";
      }
      if (mode === "sign") {
        return "Rulează semnarea";
      }
      if (mode === "seal") {
        return "Aplică sigiliul electronic";
      }
      if (mode === "placeholders") {
        return $("signFirstPlaceholder")?.checked
          ? "Generează și semnează prima poziție"
          : "Generează pozițiile de semnătură";
      }
      return "Rulează semnarea / ștampilarea";
    }

    function updateDetailHeader() {
      const detail = modeDetails[state.mode] || modeDetails.both;
      $("detailTitle").textContent = detail.title;
      $("detailSubtitle").textContent = detail.subtitle;
    }

    function showFunctionMenu() {
      state.sidebarLayer = "menu";
      $("functionMenuLayer").classList.remove("hidden");
      $("functionDetailLayer").classList.add("hidden");
      $("sidebarActions").classList.add("hidden");
      updatePlacementBoxes();
    }

    function showFunctionDetail() {
      state.sidebarLayer = "detail";
      $("functionMenuLayer").classList.add("hidden");
      $("functionDetailLayer").classList.remove("hidden");
      $("sidebarActions").classList.remove("hidden");
      updateDetailHeader();
      updatePlacementBoxes();
    }

    function setMode(mode) {
      state.mode = mode;
      modeButtons.forEach((button) => {
        const active = button.dataset.mode === mode;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });

      const signing = mode === "sign" || mode === "both";
      const stamp = mode === "stamp" || mode === "both";
      const seal = mode === "seal";
      const placeholders = mode === "placeholders";
      $("signatureToggle").checked = signing;
      $("stampToggle").checked = stamp;
      $("sealToggle").checked = seal;
      $("placeholdersToggle").checked = placeholders;
      $("signaturePanel").classList.toggle("collapsed", !signing);
      $("stampPanel").classList.toggle("collapsed", !stamp);
      $("sealPanel").classList.toggle("collapsed", !seal);
      $("placeholdersPanel").classList.toggle("collapsed", !placeholders);
      $("signatureSection").classList.toggle("function-section-hidden", !signing);
      $("stampSection").classList.toggle("function-section-hidden", !stamp);
      $("sealSection").classList.toggle("function-section-hidden", !seal);
      $("placeholdersSection").classList.toggle("function-section-hidden", !placeholders);
      updateDetailHeader();
      $("runLabel").textContent = actionLabelForMode(mode);
      updatePlacementBoxes();
    }

    function syncModeFromToggles() {
      const stamp = $("stampToggle").checked;
      const signing = $("signatureToggle").checked;
      const seal = $("sealToggle").checked;
      const placeholders = $("placeholdersToggle").checked;
      if (seal) {
        setMode("seal");
        return;
      }
      if (placeholders) {
        setMode("placeholders");
        return;
      }
      if (stamp && signing) {
        setMode("both");
      } else if (stamp) {
        setMode("stamp");
      } else {
        setMode("sign");
      }
    }

    function setPreview(preview) {
      state.activePreview = preview;
      previewButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.preview === preview);
      });
      $("placementEditor").classList.toggle("hidden", preview !== "input" || !state.pageImageUrl);
      $("outputFrame").classList.toggle("hidden", preview !== "output" || !state.outputUrl);
      $("emptyState").classList.toggle(
        "hidden",
        (preview === "input" && state.pageImageUrl) || (preview === "output" && state.outputUrl)
      );
    }

    function updateSignatureVisibility() {
      $("signatureBoxFields").classList.toggle("hidden", !$("visibleSignature").checked);
      updatePlacementBoxes();
    }

    function updateSealVisibility() {
      $("sealBoxFields").classList.toggle("hidden", !$("visibleSeal").checked);
      updatePlacementBoxes();
    }

    function updateSignFirstVisibility() {
      $("signFirstPanel").classList.toggle("collapsed", !$("signFirstPlaceholder").checked);
      if (state.mode === "placeholders") {
        $("runLabel").textContent = actionLabelForMode("placeholders");
      }
    }

    function updateRangeLabels() {
      $("stampOpacityValue").textContent = `${Math.round(numberValue("stampOpacity") * 100)}%`;
      $("stampBorderValue").textContent = `${numberValue("stampBorder")} pt`;
    }

    function updateColorLabel(input) {
      input.parentElement.querySelector("span").textContent = input.value;
      updatePlacementBoxes();
    }

    function setPageCount(pageCount) {
      state.pageCount = Math.max(1, pageCount || 1);
      document.querySelectorAll(".page-count").forEach((node) => {
        node.textContent = state.pageCount;
      });
      for (const id of ["pageNumber", "stampPage", "sigPage", "sealPage", "placeholderPage"]) {
        $(id).max = String(state.pageCount);
        if (numberValue(id) > state.pageCount) {
          $(id).value = state.pageCount;
        }
      }
      state.placeholders.forEach((placeholder) => {
        placeholder.page = clamp(placeholder.page, 1, state.pageCount);
      });
      syncPlaceholderFieldsFromActive();
      renderPlaceholderList();
    }

    function currentPageIndex() {
      return pageIndex("pageNumber");
    }

    function placeholderKind(id) {
      return `placeholder:${id}`;
    }

    function isPlaceholderKind(kind) {
      return kind.startsWith("placeholder:");
    }

    function placeholderIdFromKind(kind) {
      return Number(kind.split(":")[1]);
    }

    function placeholderById(id) {
      return state.placeholders.find((placeholder) => placeholder.id === id) || null;
    }

    function activePlaceholder() {
      return placeholderById(state.activePlaceholderId) || state.placeholders[0];
    }

    function uniquePlaceholderName(startAt = state.placeholders.length + 1) {
      const existing = new Set(state.placeholders.map((placeholder) => placeholder.fieldName));
      let index = startAt;
      let candidate = `Signature${index}`;
      while (existing.has(candidate)) {
        index += 1;
        candidate = `Signature${index}`;
      }
      return candidate;
    }

    function syncPlaceholderFieldsFromActive() {
      const placeholder = activePlaceholder();
      if (!placeholder) {
        return;
      }
      $("placeholderFieldName").value = placeholder.fieldName;
      $("placeholderPage").value = placeholder.page;
      $("placeholderX").value = placeholder.x;
      $("placeholderY").value = placeholder.y;
      $("placeholderWidth").value = placeholder.width;
      $("placeholderHeight").value = placeholder.height;
    }

    function syncActivePlaceholderFromFields({ updatePage = false } = {}) {
      const placeholder = activePlaceholder();
      if (!placeholder) {
        return;
      }
      placeholder.fieldName = $("placeholderFieldName").value || uniquePlaceholderName();
      placeholder.page = clamp(numberValue("placeholderPage") || 1, 1, state.pageCount);
      placeholder.x = Math.max(0, numberValue("placeholderX") || 0);
      placeholder.y = Math.max(0, numberValue("placeholderY") || 0);
      placeholder.width = Math.max(1, numberValue("placeholderWidth") || 1);
      placeholder.height = Math.max(1, numberValue("placeholderHeight") || 1);
      renderPlaceholderList();
      updatePlacementBoxes();
      if (updatePage && state.mode === "placeholders") {
        $("pageNumber").value = placeholder.page;
        renderPagePreview();
      }
    }

    function renderPlaceholderList() {
      const list = $("placeholderList");
      list.replaceChildren();
      state.placeholders.forEach((placeholder, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "placeholder-item";
        button.classList.toggle("active", placeholder.id === state.activePlaceholderId);
        button.dataset.placeholderId = String(placeholder.id);

        const badge = document.createElement("span");
        badge.className = "placeholder-index";
        badge.textContent = String(index + 1);

        const name = document.createElement("span");
        name.className = "placeholder-name";
        name.textContent = placeholder.fieldName || `Signature${index + 1}`;

        const page = document.createElement("span");
        page.className = "placeholder-page";
        page.textContent = `Pag. ${placeholder.page}`;

        button.replaceChildren(badge, name, page);
        button.addEventListener("click", () => selectPlaceholder(placeholder.id));
        list.append(button);
      });
      $("removePlaceholderButton").disabled = state.placeholders.length <= 1;
    }

    function selectPlaceholder(id, { updateBoxes = true } = {}) {
      if (!placeholderById(id)) {
        return;
      }
      state.activePlaceholderId = id;
      syncPlaceholderFieldsFromActive();
      renderPlaceholderList();
      if (updateBoxes) {
        updatePlacementBoxes();
      } else {
        document.querySelectorAll(".placement-box.placeholder").forEach((box) => {
          box.classList.toggle("active", Number(box.dataset.placeholderId) === id);
        });
      }
    }

    function addPlaceholder() {
      const id = state.nextPlaceholderId;
      state.nextPlaceholderId += 1;
      const page = clamp(numberValue("pageNumber") || 1, 1, state.pageCount);
      const offset = (state.placeholders.length % 4) * 12;
      state.placeholders.push({
        id,
        fieldName: uniquePlaceholderName(),
        page,
        x: 120,
        y: Math.max(20, 240 - offset),
        width: 80,
        height: 25
      });
      selectPlaceholder(id);
      setMode("placeholders");
    }

    function removeActivePlaceholder() {
      if (state.placeholders.length <= 1) {
        return;
      }
      const index = state.placeholders.findIndex(
        (placeholder) => placeholder.id === state.activePlaceholderId
      );
      state.placeholders = state.placeholders.filter(
        (placeholder) => placeholder.id !== state.activePlaceholderId
      );
      const nextIndex = clamp(index, 0, state.placeholders.length - 1);
      state.activePlaceholderId = state.placeholders[nextIndex].id;
      syncPlaceholderFieldsFromActive();
      renderPlaceholderList();
      updatePlacementBoxes();
    }

    async function renderPagePreview() {
      let file;
      try {
        file = selectedFile();
      } catch (error) {
        setPreview("input");
        return;
      }

      const seq = ++state.renderSeq;
      const form = new FormData();
      form.append("pdf", file, file.name || "input.pdf");
      form.append("page", String(currentPageIndex()));
      setStatus("Se generează previzualizarea paginii...");

      try {
        const response = await fetch("/v1/pdf/page-image", {
          method: "POST",
          body: form
        });
        if (!response.ok) {
          const payload = await response.json().catch(() => null);
          const detail = payload && payload.detail ? JSON.stringify(payload.detail) : response.statusText;
          throw new Error(detail);
        }
        if (seq !== state.renderSeq) {
          return;
        }

        const blob = await response.blob();
        if (state.pageImageUrl) {
          URL.revokeObjectURL(state.pageImageUrl);
        }
        state.pageImageUrl = URL.createObjectURL(blob);
        state.pageWidth = Number(response.headers.get("X-PDF-Page-Width"));
        state.pageHeight = Number(response.headers.get("X-PDF-Page-Height"));
        setPageCount(Number(response.headers.get("X-PDF-Page-Count")));

        const image = $("pageImage");
        image.onload = () => {
          updatePlacementBoxes();
          setPreview("input");
        };
        image.src = state.pageImageUrl;
        setStatus("Previzualizarea este gata.");
        setResultStatus("Previzualizare activă", "Poziționați ștampila și semnătura direct pe document.");
      } catch (error) {
        setStatus(error.message || String(error), true);
        setResultStatus("Eroare previzualizare", error.message || String(error), true);
      }
    }

    function placementMetrics() {
      const image = $("pageImage");
      if (!state.pageWidth || !state.pageHeight || !image.complete) {
        return null;
      }
      const rect = image.getBoundingClientRect();
      if (!rect.width || !rect.height) {
        return null;
      }
      return {
        width: rect.width,
        height: rect.height
      };
    }

    function placementValues(kind) {
      if (isPlaceholderKind(kind)) {
        const placeholder = placeholderById(placeholderIdFromKind(kind));
        if (!placeholder) {
          return null;
        }
        return {
          page: placeholder.page - 1,
          x: mmToPt(placeholder.x),
          y: mmToPt(placeholder.y),
          width: mmToPt(placeholder.width),
          height: mmToPt(placeholder.height)
        };
      }
      if (kind === "stamp") {
        return {
          page: pageIndex("stampPage"),
          x: mmToPt(numberValue("stampX")),
          y: mmToPt(numberValue("stampY")),
          width: mmToPt(numberValue("stampWidth")),
          height: mmToPt(numberValue("stampHeight"))
        };
      }
      if (kind === "seal") {
        return {
          page: pageIndex("sealPage"),
          x: mmToPt(numberValue("sealX")),
          y: mmToPt(numberValue("sealY")),
          width: mmToPt(numberValue("sealWidth")),
          height: mmToPt(numberValue("sealHeight"))
        };
      }
      return {
        page: pageIndex("sigPage"),
        x: mmToPt(numberValue("sigX")),
        y: mmToPt(numberValue("sigY")),
        width: mmToPt(numberValue("sigWidth")),
        height: mmToPt(numberValue("sigHeight"))
      };
    }

    function isPlacementVisible(kind) {
      if (state.sidebarLayer !== "detail") {
        return false;
      }
      const values = placementValues(kind);
      if (!state.pageImageUrl || !values || values.page !== currentPageIndex()) {
        return false;
      }
      if (isPlaceholderKind(kind)) {
        return state.mode === "placeholders" && $("placeholdersToggle").checked;
      }
      if (kind === "stamp") {
        return state.mode !== "sign" && $("stampToggle").checked;
      }
      if (kind === "seal") {
        return state.mode === "seal" && $("sealToggle").checked && $("visibleSeal").checked;
      }
      return state.mode !== "stamp" && $("signatureToggle").checked && $("visibleSignature").checked;
    }

    function placementBoxFor(kind) {
      if (isPlaceholderKind(kind)) {
        return document.querySelector(
          `.placement-box.placeholder[data-placeholder-id="${placeholderIdFromKind(kind)}"]`
        );
      }
      if (kind === "stamp") {
        return $("stampBox");
      }
      if (kind === "seal") {
        return $("sealBox");
      }
      return $("signatureBox");
    }

    function renderPlaceholderBoxes(metrics) {
      const layer = $("placeholderLayer");
      layer.replaceChildren();
      if (!metrics || state.mode !== "placeholders" || !state.pageImageUrl) {
        return;
      }

      state.placeholders.forEach((placeholder, index) => {
        const kind = placeholderKind(placeholder.id);
        if (!isPlacementVisible(kind)) {
          return;
        }
        const box = document.createElement("div");
        box.className = "placement-box placeholder";
        box.classList.toggle("active", placeholder.id === state.activePlaceholderId);
        box.dataset.placeholderId = String(placeholder.id);
        box.dataset.placement = kind;

        const script = document.createElement("span");
        script.className = "sig-script";
        script.textContent = `Semnătură ${index + 1}`;

        const caption = document.createElement("span");
        caption.className = "placeholder-caption";
        caption.textContent = placeholder.fieldName || `Signature${index + 1}`;

        const handle = document.createElement("span");
        handle.className = "resize-handle";
        handle.dataset.action = "resize";
        handle.dataset.placement = kind;

        box.replaceChildren(script, caption, handle);
        applyBoxStyle(box, placementValues(kind), metrics);
        box.addEventListener("pointerdown", (event) => {
          selectPlaceholder(placeholder.id, { updateBoxes: false });
          startPlacementDrag(
            event,
            kind,
            event.target.dataset.action === "resize" ? "resize" : "move"
          );
        });
        layer.append(box);
      });
    }

    function applyBoxStyle(box, values, metrics) {
      const left = (values.x / state.pageWidth) * metrics.width;
      const width = (values.width / state.pageWidth) * metrics.width;
      const height = (values.height / state.pageHeight) * metrics.height;
      const top = ((state.pageHeight - values.y - values.height) / state.pageHeight) * metrics.height;
      box.style.left = `${Math.max(0, left)}px`;
      box.style.top = `${Math.max(0, top)}px`;
      box.style.width = `${Math.max(20, width)}px`;
      box.style.height = `${Math.max(18, height)}px`;
    }

    function updatePlacementBoxes() {
      const metrics = placementMetrics();
      for (const kind of ["stamp", "signature", "seal"]) {
        const box = placementBoxFor(kind);
        const visible = metrics && isPlacementVisible(kind);
        box.classList.toggle("hidden", !visible);
        if (!visible) {
          continue;
        }
        applyBoxStyle(box, placementValues(kind), metrics);
      }
      $("stampBoxLabel").textContent = $("stampText").value || "APROBAT";
      $("stampBox").style.color = $("stampTextColor").value;
      $("stampBox").style.borderColor = $("stampBorderColor").value;
      $("stampBox").style.background = `rgba(255, 255, 255, ${0.68 + numberValue("stampOpacity") * 0.26})`;
      const caption = $("signatureBox").querySelector(".sig-caption");
      caption.replaceChildren(
        document.createTextNode($("fieldName").value || "Director Juridic"),
        document.createElement("br"),
        document.createTextNode($("location").value || "București, România")
      );
      const sealCaption = $("sealBox").querySelector(".seal-caption");
      sealCaption.replaceChildren(
        document.createTextNode($("sealFieldName").value || "SigiliuElectronic1"),
        document.createElement("br"),
        document.createTextNode($("sealLocation").value || "București, România")
      );
      renderPlaceholderBoxes(metrics);
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function applyPlacementToFields(kind, rect, metrics) {
      const x = (rect.left / metrics.width) * state.pageWidth;
      const width = (rect.width / metrics.width) * state.pageWidth;
      const height = (rect.height / metrics.height) * state.pageHeight;
      const y = state.pageHeight - ((rect.top + rect.height) / metrics.height) * state.pageHeight;

      if (isPlaceholderKind(kind)) {
        const placeholder = placeholderById(placeholderIdFromKind(kind));
        if (!placeholder) {
          return;
        }
        placeholder.page = numberValue("pageNumber");
        placeholder.x = roundMm(ptToMm(x));
        placeholder.y = roundMm(ptToMm(y));
        placeholder.width = roundMm(ptToMm(width));
        placeholder.height = roundMm(ptToMm(height));
        if (placeholder.id === state.activePlaceholderId) {
          syncPlaceholderFieldsFromActive();
        }
        renderPlaceholderList();
      } else if (kind === "stamp") {
        $("stampPage").value = numberValue("pageNumber");
        $("stampX").value = roundMm(ptToMm(x));
        $("stampY").value = roundMm(ptToMm(y));
        $("stampWidth").value = roundMm(ptToMm(width));
        $("stampHeight").value = roundMm(ptToMm(height));
      } else if (kind === "seal") {
        $("sealPage").value = numberValue("pageNumber");
        $("sealX").value = roundMm(ptToMm(x));
        $("sealY").value = roundMm(ptToMm(y));
        $("sealWidth").value = roundMm(ptToMm(width));
        $("sealHeight").value = roundMm(ptToMm(height));
      } else {
        $("sigPage").value = numberValue("pageNumber");
        $("sigX").value = roundMm(ptToMm(x));
        $("sigY").value = roundMm(ptToMm(y));
        $("sigWidth").value = roundMm(ptToMm(width));
        $("sigHeight").value = roundMm(ptToMm(height));
      }
    }

    function startPlacementDrag(event, kind, action) {
      const metrics = placementMetrics();
      if (!metrics || !isPlacementVisible(kind)) {
        return;
      }
      event.preventDefault();
      const box = placementBoxFor(kind);
      if (!box) {
        return;
      }
      const boxRect = box.getBoundingClientRect();
      const imageRect = $("pageImage").getBoundingClientRect();
      state.drag = {
        kind,
        action,
        metrics,
        pointerId: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        left: boxRect.left - imageRect.left,
        top: boxRect.top - imageRect.top,
        width: boxRect.width,
        height: boxRect.height,
        next: null,
        frame: null
      };
      box.setPointerCapture(event.pointerId);
    }

    function movePlacement(event) {
      if (!state.drag) {
        return;
      }
      const drag = state.drag;
      const box = placementBoxFor(drag.kind);
      if (!box) {
        return;
      }
      const dx = event.clientX - drag.startX;
      const dy = event.clientY - drag.startY;
      const minWidth = drag.kind === "stamp" ? 36 : 56;
      const minHeight = drag.kind === "stamp" ? 22 : 34;
      let next = {
        left: drag.left,
        top: drag.top,
        width: drag.width,
        height: drag.height
      };

      if (drag.action === "resize") {
        next.width = clamp(drag.width + dx, minWidth, drag.metrics.width - drag.left);
        next.height = clamp(drag.height + dy, minHeight, drag.metrics.height - drag.top);
      } else {
        next.left = clamp(drag.left + dx, 0, drag.metrics.width - drag.width);
        next.top = clamp(drag.top + dy, 0, drag.metrics.height - drag.height);
      }

      drag.next = next;
      if (drag.frame !== null) {
        return;
      }
      drag.frame = requestAnimationFrame(() => {
        drag.frame = null;
        const current = drag.next || next;
        box.style.left = `${current.left}px`;
        box.style.top = `${current.top}px`;
        box.style.width = `${current.width}px`;
        box.style.height = `${current.height}px`;
      });
    }

    function endPlacementDrag(event) {
      if (!state.drag) {
        return;
      }
      const drag = state.drag;
      const box = placementBoxFor(drag.kind);
      const finalRect = drag.next || {
        left: drag.left,
        top: drag.top,
        width: drag.width,
        height: drag.height
      };
      if (drag.frame !== null) {
        cancelAnimationFrame(drag.frame);
      }
      if (box) {
        box.style.left = `${finalRect.left}px`;
        box.style.top = `${finalRect.top}px`;
        box.style.width = `${finalRect.width}px`;
        box.style.height = `${finalRect.height}px`;
        if (event && typeof box.releasePointerCapture === "function") {
          try {
            box.releasePointerCapture(drag.pointerId);
          } catch (error) {
            // The pointer may already be released by the browser.
          }
        }
      }
      applyPlacementToFields(drag.kind, finalRect, drag.metrics);
      state.drag = null;
      updatePlacementBoxes();
    }

    function stampMetadata() {
      return {
        text: $("stampText").value,
        page: pageIndex("stampPage"),
        x: roundPt(mmToPt(numberValue("stampX"))),
        y: roundPt(mmToPt(numberValue("stampY"))),
        width: roundPt(mmToPt(numberValue("stampWidth"))),
        height: roundPt(mmToPt(numberValue("stampHeight"))),
        font_size: numberValue("stampFont"),
        background_opacity: numberValue("stampOpacity"),
        border_width: numberValue("stampBorder"),
        text_color: $("stampTextColor").value,
        border_color: $("stampBorderColor").value
      };
    }

    function signingMetadata() {
      const metadata = {
        field_name: $("fieldName").value,
        reason: $("reason").value || null,
        location: $("location").value || null,
        signature_box: null,
        stamp: state.mode === "both" ? stampMetadata() : null
      };

      if ($("visibleSignature").checked) {
        const x = mmToPt(numberValue("sigX"));
        const y = mmToPt(numberValue("sigY"));
        const width = mmToPt(numberValue("sigWidth"));
        const height = mmToPt(numberValue("sigHeight"));
        metadata.signature_box = {
          page: pageIndex("sigPage"),
          x1: roundPt(x),
          y1: roundPt(y),
          x2: roundPt(x + width),
          y2: roundPt(y + height)
        };
      }
      return metadata;
    }

    function sealMetadata() {
      const metadata = {
        field_name: $("sealFieldName").value,
        reason: $("sealReason").value || null,
        location: $("sealLocation").value || null,
        signature_box: null
      };

      if ($("visibleSeal").checked) {
        const x = mmToPt(numberValue("sealX"));
        const y = mmToPt(numberValue("sealY"));
        const width = mmToPt(numberValue("sealWidth"));
        const height = mmToPt(numberValue("sealHeight"));
        metadata.signature_box = {
          page: pageIndex("sealPage"),
          x1: roundPt(x),
          y1: roundPt(y),
          x2: roundPt(x + width),
          y2: roundPt(y + height)
        };
      }
      return metadata;
    }

    function signaturePlaceholdersMetadata() {
      return {
        empty_field_appearance: true,
        sign_first: $("signFirstPlaceholder").checked,
        sign_reason: $("placeholderSignReason").value || null,
        sign_location: $("placeholderSignLocation").value || null,
        placeholders: state.placeholders.map((placeholder) => {
          const x = mmToPt(placeholder.x);
          const y = mmToPt(placeholder.y);
          const width = mmToPt(placeholder.width);
          const height = mmToPt(placeholder.height);
          return {
            field_name: placeholder.fieldName,
            box: {
              page: Math.max(0, placeholder.page - 1),
              x1: roundPt(x),
              y1: roundPt(y),
              x2: roundPt(x + width),
              y2: roundPt(y + height)
            }
          };
        })
      };
    }

    function selectedFile() {
      const file = $("pdfFile").files[0];
      if (!file) {
        throw new Error("Selectați un fișier PDF.");
      }
      return file;
    }

    function setDownload(url, fileName) {
      for (const id of ["downloadLink", "downloadToolbarLink", "downloadResultLink"]) {
        const link = $(id);
        link.href = url;
        link.download = fileName;
        link.setAttribute("aria-disabled", "false");
      }
    }

    async function run() {
      const button = $("runButton");
      button.disabled = true;
      setStatus("Se procesează documentul...");
      try {
        const file = selectedFile();
        const form = new FormData();
        form.append("pdf", file, file.name || "input.pdf");

        let endpoint = "/v1/sign/pdf";
        if (state.mode === "stamp") {
          endpoint = "/v1/stamp/pdf";
          form.append("metadata", JSON.stringify(stampMetadata()));
          state.outputName = "rezultat-stampilat.pdf";
        } else if (state.mode === "seal") {
          endpoint = "/v1/seal/pdf";
          form.append("metadata", JSON.stringify(sealMetadata()));
          state.outputName = "rezultat-sigilat.pdf";
        } else if (state.mode === "placeholders") {
          endpoint = "/v1/signature-placeholders/pdf";
          form.append("metadata", JSON.stringify(signaturePlaceholdersMetadata()));
          state.outputName = $("signFirstPlaceholder").checked
            ? "pozitii-semnaturi-prima-semnata.pdf"
            : "pozitii-semnaturi.pdf";
        } else {
          form.append("metadata", JSON.stringify(signingMetadata()));
          state.outputName = "rezultat-semnat.pdf";
        }

        const headers = {};
        const token = $("token").value.trim();
        const sealToken = $("sealToken").value.trim();
        const placeholderToken = $("placeholderToken").value.trim();
        if (state.mode === "seal" && sealToken) {
          headers["X-CSC-Seal-OAuth-Token"] = sealToken;
        } else if (state.mode === "placeholders" && $("signFirstPlaceholder").checked && placeholderToken) {
          headers["X-CSC-OAuth-Token"] = placeholderToken;
        } else if (token) {
          headers["X-CSC-OAuth-Token"] = token;
        }

        const response = await fetch(endpoint, {
          method: "POST",
          body: form,
          headers
        });

        if (!response.ok) {
          const payload = await response.json().catch(() => null);
          const detail = payload && payload.detail ? JSON.stringify(payload.detail) : response.statusText;
          throw new Error(detail);
        }

        const blob = await response.blob();
        if (state.outputUrl) {
          URL.revokeObjectURL(state.outputUrl);
        }
        state.outputUrl = URL.createObjectURL(blob);
        $("outputFrame").src = state.outputUrl;
        setDownload(state.outputUrl, state.outputName);
        let successText = "Documentul a fost semnat și ștampilat cu succes.";
        if (state.mode === "seal") {
          successText = "Documentul a fost sigilat electronic cu succes.";
        } else if (state.mode === "placeholders") {
          successText = $("signFirstPlaceholder").checked
            ? "Pozițiile au fost adăugate, iar prima poziție a fost semnată."
            : "Pozițiile pentru semnături multiple au fost adăugate în PDF.";
        }
        setStatus(successText);
        setResultStatus("Succes", successText);
        setPreview("output");
      } catch (error) {
        setStatus(error.message || String(error), true);
        setResultStatus("Eroare", error.message || String(error), true);
      } finally {
        button.disabled = false;
      }
    }

    $("pdfFile").addEventListener("change", () => {
      const file = $("pdfFile").files[0];
      if (!file) {
        return;
      }
      if (state.inputUrl) {
        URL.revokeObjectURL(state.inputUrl);
      }
      state.inputUrl = URL.createObjectURL(file);
      $("selectedFileName").textContent = file.name || "input.pdf";
      $("selectedFileSize").textContent = `${formatSize(file.size)} · PDF`;
      $("selectedFileRow").classList.remove("hidden");
      setStatus(file.name || "PDF selectat");
      $("pageNumber").value = "1";
      renderPagePreview();
    });

    $("visibleSignature").addEventListener("change", updateSignatureVisibility);
    $("invisibleSignature").addEventListener("change", updateSignatureVisibility);
    $("visibleSeal").addEventListener("change", updateSealVisibility);
    $("invisibleSeal").addEventListener("change", updateSealVisibility);
    $("stampToggle").addEventListener("change", syncModeFromToggles);
    $("signatureToggle").addEventListener("change", syncModeFromToggles);
    $("sealToggle").addEventListener("change", syncModeFromToggles);
    $("placeholdersToggle").addEventListener("change", syncModeFromToggles);
    $("signFirstPlaceholder").addEventListener("change", updateSignFirstVisibility);
    $("addPlaceholderButton").addEventListener("click", addPlaceholder);
    $("removePlaceholderButton").addEventListener("click", removeActivePlaceholder);
    $("stampOpacity").addEventListener("input", updateRangeLabels);
    $("stampBorder").addEventListener("input", updateRangeLabels);
    $("stampTextColor").addEventListener("input", (event) => updateColorLabel(event.target));
    $("stampBorderColor").addEventListener("input", (event) => updateColorLabel(event.target));
    $("stampText").addEventListener("input", updatePlacementBoxes);
    $("fieldName").addEventListener("input", updatePlacementBoxes);
    $("location").addEventListener("input", updatePlacementBoxes);
    $("sealFieldName").addEventListener("input", updatePlacementBoxes);
    $("sealLocation").addEventListener("input", updatePlacementBoxes);
    $("placeholderFieldName").addEventListener("input", () => syncActivePlaceholderFromFields());
    for (const id of [
      "stampX",
      "stampY",
      "stampWidth",
      "stampHeight",
      "sigX",
      "sigY",
      "sigWidth",
      "sigHeight",
      "sealX",
      "sealY",
      "sealWidth",
      "sealHeight"
    ]) {
      $(id).addEventListener("input", updatePlacementBoxes);
    }
    for (const id of [
      "placeholderX",
      "placeholderY",
      "placeholderWidth",
      "placeholderHeight"
    ]) {
      $(id).addEventListener("input", () => syncActivePlaceholderFromFields());
    }
    $("pageNumber").addEventListener("change", renderPagePreview);
    $("stampPage").addEventListener("change", () => {
      if (state.mode !== "sign") {
        $("pageNumber").value = $("stampPage").value;
        renderPagePreview();
      }
    });
    $("sigPage").addEventListener("change", () => {
      if (state.mode !== "stamp") {
        $("pageNumber").value = $("sigPage").value;
        renderPagePreview();
      }
    });
    $("sealPage").addEventListener("change", () => {
      if (state.mode === "seal") {
        $("pageNumber").value = $("sealPage").value;
        renderPagePreview();
      }
    });
    $("placeholderPage").addEventListener("change", () => {
      syncActivePlaceholderFromFields({ updatePage: true });
    });
    $("stampBox").addEventListener("pointerdown", (event) => {
      startPlacementDrag(
        event,
        "stamp",
        event.target.dataset.action === "resize" ? "resize" : "move"
      );
    });
    $("signatureBox").addEventListener("pointerdown", (event) => {
      startPlacementDrag(
        event,
        "signature",
        event.target.dataset.action === "resize" ? "resize" : "move"
      );
    });
    $("sealBox").addEventListener("pointerdown", (event) => {
      startPlacementDrag(
        event,
        "seal",
        event.target.dataset.action === "resize" ? "resize" : "move"
      );
    });
    window.addEventListener("pointermove", movePlacement);
    window.addEventListener("pointerup", endPlacementDrag);
    window.addEventListener("pointercancel", endPlacementDrag);
    $("runButton").addEventListener("click", run);
    $("backToFunctionList").addEventListener("click", showFunctionMenu);
    $("refreshPreview").addEventListener("click", renderPagePreview);
    $("resetPreviewButton").addEventListener("click", renderPagePreview);
    $("clearButton").addEventListener("click", () => {
      $("pdfFile").value = "";
      if (state.inputUrl) {
        URL.revokeObjectURL(state.inputUrl);
      }
      if (state.pageImageUrl) {
        URL.revokeObjectURL(state.pageImageUrl);
      }
      if (state.outputUrl) {
        URL.revokeObjectURL(state.outputUrl);
      }
      state.inputUrl = null;
      state.pageImageUrl = null;
      state.outputUrl = null;
      $("pageImage").removeAttribute("src");
      $("outputFrame").removeAttribute("src");
      $("selectedFileRow").classList.add("hidden");
      setPageCount(1);
      for (const id of ["downloadLink", "downloadToolbarLink", "downloadResultLink"]) {
        const link = $(id);
        link.removeAttribute("href");
        link.removeAttribute("download");
        link.setAttribute("aria-disabled", "true");
      }
      setStatus("Gata pentru utilizare");
      setResultStatus("Pregătit pentru poziționare", "Încărcați un PDF pentru previzualizare vizuală.");
      setPreview("input");
    });
    $("logClose").addEventListener("click", () => $("logPanel").classList.add("hidden"));
    $("tokenVisibility").addEventListener("click", () => {
      $("token").type = $("token").type === "password" ? "text" : "password";
    });
    $("sealTokenVisibility").addEventListener("click", () => {
      $("sealToken").type = $("sealToken").type === "password" ? "text" : "password";
    });
    $("placeholderTokenVisibility").addEventListener("click", () => {
      $("placeholderToken").type = $("placeholderToken").type === "password" ? "text" : "password";
    });
    $("zoomOut").addEventListener("click", () => {
      state.zoom = Math.max(60, state.zoom - 10);
      $("zoomLevel").textContent = `${state.zoom}%`;
    });
    $("zoomIn").addEventListener("click", () => {
      state.zoom = Math.min(160, state.zoom + 10);
      $("zoomLevel").textContent = `${state.zoom}%`;
    });

    modeButtons.forEach((button) => {
      button.addEventListener("click", () => {
        setMode(button.dataset.mode);
        showFunctionDetail();
      });
    });
    previewButtons.forEach((button) => {
      button.addEventListener("click", () => setPreview(button.dataset.preview));
    });

    updateRangeLabels();
    updateSignatureVisibility();
    updateSealVisibility();
    updateSignFirstVisibility();
    syncPlaceholderFieldsFromActive();
    renderPlaceholderList();
    setMode("both");
    showFunctionMenu();
    setPreview("input");
  </script>
</body>
</html>
"""
