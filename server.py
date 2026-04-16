"""
server.py
Serves static Compass newsletter HTML editions.
Deployed as a standalone Railway service from the compassIssues repo.
"""

import os
import re
import calendar
from collections import defaultdict
from flask import Flask, send_from_directory, render_template_string, redirect, abort

app = Flask(__name__)

ISSUES_DIR = os.path.join(os.path.dirname(__file__), "compass_issues")

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

LOGO_URL = "/static/Compass800.png"

@app.route("/")
def index():
    """Archive index — grouped by year and month, with calendar dropdowns."""
    if not os.path.exists(ISSUES_DIR):
        editions = {}
    else:
        files = sorted([
            f for f in os.listdir(ISSUES_DIR)
            if f.startswith("compass_") and f.endswith(".html")
            and "teaser" not in f and "snippet" not in f
        ], reverse=True)

        editions = defaultdict(lambda: defaultdict(dict))
        for f in files:
            date_str = f.replace("compass_", "").replace(".html", "")
            try:
                year, month, day = date_str.split("-")
                editions[int(year)][int(month)][int(day)] = date_str
            except ValueError:
                continue

        editions = {
            y: dict(sorted(editions[y].items(), reverse=True))
            for y in sorted(editions.keys(), reverse=True)
        }

    has_editions = any(editions.get(y) for y in editions)

    # Build calendar data per year/month
    cal_data = {}
    for year, months in editions.items():
        cal_data[year] = {}
        for month_num, days_dict in months.items():
            c = calendar.monthcalendar(year, month_num)
            cal_data[year][month_num] = {
                "weeks": c,
                "has_edition": set(days_dict.keys()),
                "date_map": days_dict,
            }

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
      width: 160px;
      height: auto;
      background: #F7F5F0;
      mix-blend-mode: multiply;
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

    /* ── CONTENT ── */
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
      color: #111111;
      line-height: 1;
      margin-bottom: 28px;
      border-bottom: 1px solid #E0DDD6;
      padding-bottom: 16px;
    }

    /* ── MONTH BUTTONS ── */
    .months-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 24px;
    }
    .month-btn {
      font-family: 'DM Mono', monospace;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #1B3A6B;
      background: none;
      border: 1px solid #1B3A6B;
      padding: 8px 20px;
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
    }
    .month-btn:hover, .month-btn.active {
      background: #1B3A6B;
      color: #fff;
    }

    /* ── CALENDAR ── */
    .calendar-container {
      display: none;
      margin-bottom: 8px;
    }
    .calendar-container.open { display: block; }

    .calendar-wrap {
      background: #fff;
      border: 1px solid #E0DDD6;
      padding: 20px 24px 16px;
      display: inline-block;
    }
    .cal-header {
      font-family: 'DM Mono', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #6B6860;
      margin-bottom: 14px;
    }
    .cal-grid {
      border-collapse: collapse;
    }
    .cal-grid th {
      font-family: 'DM Mono', monospace;
      font-size: 9px;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: #9B9890;
      padding: 0 0 8px;
      text-align: center;
      font-weight: 400;
      width: 36px;
    }
    .cal-grid td {
      text-align: center;
      padding: 2px;
    }
    .cal-day {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      font-size: 13px;
      font-weight: 500;
      border-radius: 2px;
    }
    .cal-day.no-edition {
      color: #C8C5BE;
    }
    a.cal-day.has-edition {
      color: #1B3A6B;
      font-weight: 600;
      text-decoration: none;
      transition: background 0.12s;
    }
    a.cal-day.has-edition:hover {
      background: #E8EDF5;
    }

    .empty-msg {
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

    @media (max-width: 600px) {
      .content { padding: 32px 20px; }
      .header { padding: 36px 20px 32px; }
      .logo-img { width: 120px; }
    }
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="header">
    <div class="header-inner">
      <img src="{{ logo_url }}" alt="Compass" class="logo-img">
      <div class="brand-tagline">Sports Analytics · MLB Edition</div>
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

        <!-- Month buttons -->
        <div class="months-row">
          {% for month_num in months.keys() %}
          <button class="month-btn" onclick="toggleCal('cal-{{ year }}-{{ month_num }}', this)">
            {{ month_names[month_num] }}
          </button>
          {% endfor %}
        </div>

        <!-- Calendar panels -->
        {% for month_num, month_info in cal_data[year].items() %}
        <div class="calendar-container" id="cal-{{ year }}-{{ month_num }}">
          <div class="calendar-wrap">
            <div class="cal-header">{{ month_names[month_num] }} {{ year }}</div>
            <table class="cal-grid">
              <thead>
                <tr>
                  <th>Su</th><th>Mo</th><th>Tu</th><th>We</th><th>Th</th><th>Fr</th><th>Sa</th>
                </tr>
              </thead>
              <tbody>
                {% for week in month_info.weeks %}
                <tr>
                  {% for day in week %}
                  <td>
                    {% if day == 0 %}
                      <span class="cal-day no-edition">&nbsp;</span>
                    {% elif day in month_info.has_edition %}
                      <a class="cal-day has-edition"
                         href="/{{ month_info.date_map[day] }}"
                         target="_blank" rel="noopener">{{ day }}</a>
                    {% else %}
                      <span class="cal-day no-edition">{{ day }}</span>
                    {% endif %}
                  </td>
                  {% endfor %}
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
        {% endfor %}

      </div>
      {% endfor %}
    {% else %}
      <p class="empty-msg">No editions published yet.</p>
    {% endif %}
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <a href="https://mlb.up.railway.app/" class="footer-btn" target="_blank" rel="noopener">
      Compass: MLB Stats Tracker →
    </a>
  </div>

  <script>
    function toggleCal(id, btn) {
      // Close any other open calendar and deactivate its button
      document.querySelectorAll('.calendar-container.open').forEach(el => {
        if (el.id !== id) el.classList.remove('open');
      });
      document.querySelectorAll('.month-btn.active').forEach(el => {
        if (el !== btn) el.classList.remove('active');
      });
      // Toggle this one
      document.getElementById(id).classList.toggle('open');
      btn.classList.toggle('active');
    }

    // Auto-open the most recent month on load
    const firstBtn = document.querySelector('.month-btn');
    const firstCal = document.querySelector('.calendar-container');
    if (firstBtn && firstCal) {
      firstBtn.classList.add('active');
      firstCal.classList.add('open');
    }
  </script>

</body>
</html>
    """, editions=editions, has_editions=has_editions, month_names=MONTH_NAMES,
         cal_data=cal_data, logo_url=LOGO_URL)


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