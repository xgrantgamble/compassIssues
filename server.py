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
    body { font-family:'DM Sans',sans-serif; background:#F7F5F0; color:#111; min-height:100vh; display:flex; flex-direction:column; }

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
      gap: 16px;
    }
    .logo-img {
      width: 120px;
      height: auto;
      /* Tint black PNG to navy #1B3A6B */
      filter: brightness(0) saturate(100%) invert(18%) sepia(52%) saturate(742%) hue-rotate(185deg) brightness(90%) contrast(95%);
    }
    .brand-tagline {
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #6B6860;
      margin-top: -8px;
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
      margin-top: 4px;
    }
    .latest-btn:hover { background: #162f58; }

    /* ── ARCHIVE GRID ── */
    .content {
      max-width: 960px;
      margin: 0 auto;
      padding: 52px 40px;
      flex: 1;
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

    /* 3 columns fixed */
    .months-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0;
    }

    /* Each month is a collapsible accordion panel */
    .month-block {
      border: 1px solid #E0DDD6;
      border-right: none;
      border-bottom: none;
    }
    .month-block:nth-child(3n) {
      border-right: 1px solid #E0DDD6;
    }
    /* Bottom border on last row */
    .months-grid .month-block:nth-last-child(-n+3) {
      border-bottom: 1px solid #E0DDD6;
    }

    .month-toggle {
      width: 100%;
      background: none;
      border: none;
      cursor: pointer;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      text-align: left;
      background: #F7F5F0;
      transition: background 0.15s;
    }
    .month-toggle:hover { background: #EFECE6; }

    .month-name {
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #6B6860;
    }
    .month-count {
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      color: #9B9890;
      letter-spacing: 1px;
    }
    .month-arrow {
      font-size: 10px;
      color: #9B9890;
      transition: transform 0.2s;
      margin-left: 8px;
      flex-shrink: 0;
    }
    .month-block.open .month-arrow { transform: rotate(180deg); }

    .month-editions {
      display: none;
      padding: 4px 0 12px;
      background: #fff;
      border-top: 1px solid #E0DDD6;
    }
    .month-block.open .month-editions { display: block; }

    .edition-link {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: #1B3A6B;
      text-decoration: none;
      padding: 5px 20px;
      transition: background 0.12s;
    }
    .edition-link:hover { background: #E8EDF5; }

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
    }
    .footer-btn {
      display: inline-block;
      background: #1B3A6B;
      color: #fff;
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 12px 28px;
      text-decoration: none;
    }
    .footer-btn:hover { background: #162f58; }

    /* ── RESPONSIVE ── */
    @media (max-width: 640px) {
      .months-grid { grid-template-columns: 1fr; }
      .month-block { border-right: 1px solid #E0DDD6; border-bottom: none; }
      .month-block:last-child { border-bottom: 1px solid #E0DDD6; }
      .content { padding: 32px 20px; }
      .header { padding: 36px 20px 32px; }
      .logo-img { width: 90px; }
    }
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="header">
    <div class="header-inner">
      <img src="/static/CompassLogoV1.png" alt="Compass" class="logo-img">
      <div class="brand-tagline">Sports Intelligence · MLB Edition</div>
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
          <div class="month-block" id="month-{{ year }}-{{ month_num }}">
            <button class="month-toggle" onclick="toggleMonth('month-{{ year }}-{{ month_num }}')">
              <span class="month-name">{{ month_names[month_num] }}</span>
              <span>
                <span class="month-count">{{ issues|length }} issues</span>
                <span class="month-arrow">▾</span>
              </span>
            </button>
            <div class="month-editions">
              {% for issue in issues %}
              <a class="edition-link" href="/{{ issue.date }}" target="_blank" rel="noopener">
                {{ issue.label }}
              </a>
              {% endfor %}
            </div>
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
    <a href="https://mlb.up.railway.app/" class="footer-btn" target="_blank" rel="noopener">
      Compass: MLB Stats Tracker →
    </a>
  </div>

  <script>
    function toggleMonth(id) {
      const block = document.getElementById(id);
      block.classList.toggle('open');
    }

    // Auto-open the most recent month on load
    const firstBlock = document.querySelector('.month-block');
    if (firstBlock) firstBlock.classList.add('open');
  </script>

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
  <h1>Compass</h1>
  <p>No edition found for {{ date }}.</p>
  <p><a href="/latest">View latest edition →</a></p>
  <p><a href="/">View all editions →</a></p>
</body></html>
        """, date=date_str), 404
    return send_from_directory(ISSUES_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)