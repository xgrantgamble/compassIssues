# compass-issues

Static host for Compass MLB newsletter editions.

Deployed as a standalone Railway service. HTML files are pushed here nightly by the `compass` pipeline repo via GitHub Actions.

## Structure

```
compass-issues/
├── server.py           # Flask app — serves editions by date
├── railway.toml        # Railway deploy config
├── requirements.txt
└── compass_issues/     # Newsletter HTML files (auto-populated by pipeline)
    └── compass_YYYY-MM-DD.html
```

## Routes

- `/` — Archive index
- `/latest` — Redirect to most recent edition
- `/{YYYY-MM-DD}` — Serve a specific edition

## Deployment

Railway auto-deploys on push to `main`. The pipeline repo (`compass`) pushes new HTML here after each nightly run.
