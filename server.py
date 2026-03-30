"""
server.py
Serves static Compass newsletter HTML editions.
Deployed as a standalone Railway service from the compassIssues repo.
"""

import os
import re
from collections import defaultdict
from flask import Flask, send_from_directory, render_template_string, redirect, abort

app = Flask(__name__)

ISSUES_DIR = os.path.join(os.path.dirname(__file__), "compass_issues")

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


@app.route("/")
def index():
    """Archive index — grouped by year and month."""
    if not os.path.exists(ISSUES_DIR):
        editions = {}
    else:
        files = sorted([
            f for f in os.listdir(ISSUES_DIR)
            if f.startswith("compass_") and f.endswith(".html")
            and "teaser" not in f and "snippet" not in f
        ], reverse=True)

        # Group by year → month
        editions = defaultdict(lambda: defaultdict(list))
        for f in files:
            date_str = f.replace("compass_", "").replace(".html", "")
            try:
                year, month, day = date_str.split("-")
                editions[int(year)][int(month)].append({
                    "date": date_str,
                    "day": int(day),
                    "label": f"{MONTH_NAMES[int(month)]} {int(day)}",
                })
            except ValueError:
                continue

        # Sort years descending, months descending within year
        editions = {
            y: dict(sorted(editions[y].items(), reverse=True))
            for y in sorted(editions.keys(), reverse=True)
        }

    has_editions = any(editions.get(y) for y in editions)

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Compass — Archive</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'DM Sans',sans-serif; background:#F7F5F0; color:#111; min-height:100vh; }

    /* ── HEADER ── */
    .header {
      padding: 52px 40px 44px;
      text-align: center;
      background: #F7F5F0;
      border-bottom: 1px solid #E0DDD6;
    }
    .header-inner {
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }
    .brand-name {
      font-family: 'Playfair Display', serif;
      font-size: 40px;
      font-weight: 600;
      color: #111111;
      letter-spacing: -0.5px;
      line-height: 1;
    }
    .brand-tagline {
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #6B6860;
    }
    .latest-btn {
      display: inline-block;
      background: #1B3A6B;
      color: #fff;
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 12px 28px;
      text-decoration: none;
      margin-top: 8px;
    }
    .latest-btn:hover { background: #162f58; }

    /* ── ARCHIVE GRID ── */
    .content {
      max-width: 900px;
      margin: 0 auto;
      padding: 52px 40px;
    }
    .year-block { margin-bottom: 52px; }
    .year-heading {
      font-family: 'Playfair Display', serif;
      font-size: 52px;
      font-weight: 600;
      color: #E0DDD6;
      line-height: 1;
      margin-bottom: 28px;
      border-bottom: 1px solid #E0DDD6;
      padding-bottom: 16px;
    }
    .months-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 32px 40px;
    }
    .month-block {}
    .month-name {
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #6B6860;
      margin-bottom: 10px;
    }
    .edition-link {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: #1B3A6B;
      text-decoration: none;
      padding: 4px 0;
      border-bottom: 1px solid transparent;
      transition: border-color 0.15s;
    }
    .edition-link:hover { border-bottom-color: #1B3A6B; }
    .empty {
      color: #6B6860;
      font-style: italic;
      font-size: 14px;
      margin-top: 20px;
    }

    /* ── FOOTER ── */
    .footer {
      background: #111111;
      padding: 20px 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
    }
    .footer-name {
      font-family: 'Playfair Display', serif;
      font-size: 16px;
      font-weight: 600;
      color: #fff;
    }
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="header">
    <div class="header-inner">
      <svg width="40" height="40" viewBox="0 0 36 36" fill="none">
        <circle cx="18" cy="18" r="17" stroke="#1B3A6B" stroke-width="1.5"/>
        <circle cx="18" cy="18" r="3" fill="#1B3A6B"/>
        <path d="M18 4 L20.5 16 L18 15 L15.5 16 Z" fill="#1B3A6B"/>
        <path d="M18 32 L20.5 20 L18 21 L15.5 20 Z" fill="#E0DDD6"/>
        <line x1="32" y1="18" x2="29" y2="18" stroke="#1B3A6B" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="4" y1="18" x2="7" y2="18" stroke="#1B3A6B" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <div class="brand-name">Compass</div>
      <div class="brand-tagline">Sports intelligence · MLB edition</div>
      {% if has_editions %}
      <a href="/latest" class="latest-btn" target="_blank" rel="noopener">Latest Edition →</a>
      {% endif %}
    </div>
  </div>

  <!-- ARCHIVE -->
  <div class="content">
    {% if has_editions %}
      {% for year, months in editions.items() %}
      <div class="year-block">
        <div class="year-heading">{{ year }}</div>
        <div class="months-grid">
          {% for month_num, issues in months.items() %}
          <div class="month-block">
            <div class="month-name">{{ month_names[month_num] }}</div>
            {% for issue in issues %}
            <a class="edition-link" href="/{{ issue.date }}" target="_blank" rel="noopener">
              {{ issue.label }}
            </a>
            {% endfor %}
          </div>
          {% endfor %}
        </div>
      </div>
      {% endfor %}
    {% else %}
      <p class="empty">No editions published yet.</p>
    {% endif %}
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <svg width="18" height="18" viewBox="0 0 36 36" fill="none">
      <circle cx="18" cy="18" r="17" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
      <circle cx="18" cy="18" r="3" fill="rgba(255,255,255,0.8)"/>
      <path d="M18 4 L20.5 16 L18 15 L15.5 16 Z" fill="white"/>
      <path d="M18 32 L20.5 20 L18 21 L15.5 20 Z" fill="rgba(255,255,255,0.3)"/>
    </svg>
    <span class="footer-name">Compass</span>
  </div>

</body>
</html>
    """, editions=editions, has_editions=has_editions, month_names=MONTH_NAMES)


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