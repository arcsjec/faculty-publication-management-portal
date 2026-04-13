# Faculty Publication Portal

Comprehensive Flask-based portal for managing faculty publications, incentive workflows, review pipelines, circulars, notifications, and role-based approvals.

## Highlights

- Multi-role dashboards (admin, HOD, dean, principal, vice principal, etc.)
- Publication CRUD and review/edit workflows
- Incentive and support application flows
- Citation update scheduler and automation scripts
- Deployment scripts for Ubuntu + Nginx + Gunicorn

## Core Files

- `app.py`: main Flask app
- `models.py`: database models
- `forms.py`: WTForms definitions
- `config.py`: environment-based config
- `deployment/`: production deployment scripts and guides

## Quick Setup

1. Create virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Configure `.env` from `.env.example`.
4. Run:
   `python app.py`

## Deployment
Use `deployment/` scripts and guides:

- `deployment/readme.md.md`
- `deployment/DEPLOYMENT_GUIDE.md`
- `deployment/quickstart.md`

## Security Notes

- Keep `.env` private.
- Do not commit production database files.
- Restrict uploaded file exposure and validate file types.

## License
MIT License. See `LICENSE`.

