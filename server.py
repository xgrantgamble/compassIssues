"""
server.py
Serves static Compass newsletter HTML editions.
Deployed as a standalone Railway service from the compass-issues repo.
Completely separate from the compass pipeline repo.
"""

import os
import re
from flask import Flask, send_from_directory, render_template_string, redirect, abort

app = Flask(__name__)

ISSUES_DIR = os.path.join(os.path.dirname(__file__), "compass_issues")


@app.route("/")
def index():
    """Archive index — lists all published editions."""
    if not os.path.exists(ISSUES_DIR):
        issues = []
    else:
        files = sorted([
            f for f in os.listdir(ISSUES_DIR)
            if f.startswith("compass_") and f.endswith(".html")
            and "teaser" not in f and "snippet" not in f
        ], reverse=True)
        issues = [f.replace("compass_", "").replace(".html", "") for f in files]

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Compass — MLB Edition Archive</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'DM Sans',sans-serif; background:#F7F5F0; color:#111; min-height:100vh; }
    .header { background:#1B3A6B; padding:32px 40px; display:flex; align-items:center; gap:14px; }
    .header svg { flex-shrink:0; }
    .header-text h1 { font-family:'Playfair Display',serif; font-size:26px; color:#fff; }
    .header-text p { font-family:'DM Mono',monospace; font-size:10px; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.45); margin-top:4px; }
    .content { max-width:660px; margin:0 auto; padding:40px 20px; }
    .latest-btn { display:inline-block; background:#1B3A6B; color:#fff; font-family:'DM Mono',monospace;
                  font-size:10px; letter-spacing:2px; text-transform:uppercase;
                  padding:12px 24px; text-decoration:none; margin-bottom:32px; }
    .issue { display:flex; justify-content:space-between; align-items:center;
             padding:14px 0; border-bottom:1px solid #E0DDD6; }
    .issue a { color:#1B3A6B; text-decoration:none; font-weight:500; font-size:15px; }
    .issue a:hover { text-decoration:underline; }
    .issue-meta { font-family:'DM Mono',monospace; font-size:11px; color:#6B6860; }
    .empty { color:#6B6860; font-style:italic; margin-top:20px; font-size:14px; }
  </style>
</head>
<body>
  <div class="header">
    <svg width="32" height="32" viewBox="0 0 36 36" fill="none">
      <circle cx="18" cy="18" r="17" stroke="rgba(255,255,255,0.35)" stroke-width="1.5"/>
      <circle cx="18" cy="18" r="3" fill="white"/>
      <path d="M18 4 L20.5 16 L18 15 L15.5 16 Z" fill="white"/>
      <path d="M18 32 L20.5 20 L18 21 L15.5 20 Z" fill="rgba(255,255,255,0.3)"/>
      <line x1="32" y1="18" x2="29" y2="18" stroke="rgba(255,255,255,0.5)" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="4" y1="18" x2="7" y2="18" stroke="rgba(255,255,255,0.5)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <div class="header-text">
      <h1>Compass</h1>
      <p>MLB Edition · Archive</p>
    </div>
  </div>
  <div class="content">
    {% if issues %}
    <a href="/latest" class="latest-btn">Latest Edition →</a>
    {% for d in issues %}
    <div class="issue">
      <a href="/{{ d }}">{{ d }}</a>
      <span class="issue-meta">View →</span>
    </div>
    {% endfor %}
    {% else %}
    <p class="empty">No editions published yet.</p>
    {% endif %}
  </div>
</body>
</html>
    """, issues=issues)


@app.route("/latest")
def latest():
    """Redirect to most recent edition."""
    if not os.path.exists(ISSUES_DIR):
        abort(404)
    files = sorted([
        f for f in os.listdir(ISSUES_DIR)
        if f.startswith("compass_") and f.endswith(".html")
        and "teaser" not in f and "snippet" not in f
    ])
    if not files:
        abort(404)
    date_str = files[-1].replace("compass_", "").replace(".html", "")
    return redirect(f"/{date_str}")


@app.route("/<date_str>")
def serve_edition(date_str):
    """Serve a newsletter edition by date."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        abort(400)
    filename = f"compass_{date_str}.html"
    if not os.path.exists(os.path.join(ISSUES_DIR, filename)):
        return render_template_string("""
<!DOCTYPE html><html><head>
  <title>Compass — Not Found</title>
  <style>body{font-family:sans-serif;text-align:center;padding:60px 20px;color:#333;background:#F7F5F0;}
  h1{font-family:Georgia,serif;font-size:24px;margin-bottom:12px;}p{color:#666;margin-bottom:8px;}a{color:#1B3A6B;}</style>
</head><body>
  <h1>⚾ Compass</h1>
  <p>No edition found for {{ date }}.</p>
  <p><a href="/latest">View latest edition →</a></p>
  <p><a href="/">View all editions →</a></p>
</body></html>
        """, date=date_str), 404
    return send_from_directory(ISSUES_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
