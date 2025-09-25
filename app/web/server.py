from __future__ import annotations

import io
from typing import Any

from flask import Flask, jsonify, request, send_file

from ..core.app import SmartDisplayApp


def create_app() -> Flask:
    flask_app = Flask(__name__)
    app = SmartDisplayApp()

    @flask_app.get("/api/settings")
    def get_settings():
        return jsonify(app.config.settings)

    @flask_app.post("/api/settings")
    def update_settings():
        data: dict[str, Any] = request.get_json(force=True)  # type: ignore[assignment]
        for k, v in data.items():
            app.config.set(k, v)
        app.config.save()
        return jsonify({"ok": True})

    @flask_app.get("/api/preview.png")
    def preview_image():
        mode = (app.config.get("display.mode", "html") or "html").lower()
        if mode == "html":
            image = app.renderer.render_html(app._build_context())
        else:
            image = app.renderer.create_canvas()
            draw = app.renderer.get_draw(image)
            width, height = image.size
            num = max(1, len(app.widgets))
            slot_h = height // num
            y = 0
            for widget in app.widgets:
                region = (0, y, width, y + slot_h)
                widget.draw(draw, region)
                y += slot_h
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")

    @flask_app.get("/")
    def index():
        return (
            """
            <html>
              <head>
                <title>Smart Display</title>
                <style>
                  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }
                  img { width: 480px; height: 800px; border: 1px solid #ccc; display:block; }
                  form { margin-top: 16px; display: grid; grid-template-columns: 160px 1fr; gap: 8px 12px; max-width: 720px; }
                  input, select { padding: 6px 8px; }
                  button { padding: 8px 12px; }
                  label { align-self: center; }
                </style>
              </head>
              <body>
                <h2>Preview</h2>
                <img id="preview" src="/api/preview.png" />
                <h3>Settings</h3>
                <form id="form">
                  <label>Orientation</label>
                  <select name="display.orientation">
                    <option value="portrait">Portrait</option>
                    <option value="landscape">Landscape</option>
                  </select>
                  <label>Mode</label>
                  <select name="display.mode">
                    <option value="html">HTML</option>
                    <option value="pil">PIL</option>
                  </select>
                  <label>Template</label>
                  <input name="display.template" placeholder="display.html" />
                  <label>ICS URL</label>
                  <input name="data.calendar.ics_url" />
                  <label>Lookahead Days</label>
                  <input name="data.calendar.lookahead_days" type="number" />
                  <label>Timezone</label>
                  <input name="data.calendar.timezone" />
                  <label>RSS URL</label>
                  <input name="data.news.rss_url" />
                  <label>Headlines</label>
                  <input name="data.news.limit" type="number" />
                  <label>Market Symbol</label>
                  <input name="data.market.symbol" />
                  <label>Refresh Interval (s)</label>
                  <input name="refresh.interval_seconds" type="number" />
                  <div></div>
                  <div>
                    <button type="submit">Save</button>
                    <button type="button" id="refresh">Render Now</button>
                  </div>
                </form>
                <script>
                  async function load() {
                    const r = await fetch('/api/settings');
                    const s = await r.json();
                    for (const el of document.querySelectorAll('#form [name]')) {
                      const path = el.name.split('.');
                      let node = s;
                      for (const k of path) { if (node && k in node) node = node[k]; else { node = undefined; break; } }
                      if (node !== undefined) el.value = node;
                    }
                    // initial preview cache-bust
                    document.getElementById('preview').src = '/api/preview.png?t=' + Date.now();
                  }
                  async function save(e) {
                    e.preventDefault();
                    const data = {};
                    for (const el of document.querySelectorAll('#form [name]')) {
                      data[el.name] = el.value;
                    }
                    await fetch('/api/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                    document.getElementById('preview').src = '/api/preview.png?t=' + Date.now();
                  }
                  async function refresh() {
                    document.getElementById('preview').src = '/api/preview.png?t=' + Date.now();
                  }
                  load();
                  document.getElementById('form').addEventListener('submit', save);
                  document.getElementById('refresh').addEventListener('click', refresh);
                </script>
              </body>
            </html>
            """
        )

    return flask_app


