# ARC SJEC - Faculty Publication Portal (Flask)
## Project Documentation

## 1. Abstract
Faculty Publication Portal is a large-scale Flask web application designed to manage publication records, approval workflows, incentives, and communication pipelines across multiple institutional roles. It centralizes publication lifecycle operations and policy-driven decision workflows.

## 2. Objectives
1. Digitize publication submission and tracking.
2. Enable role-based review and approval hierarchy.
3. Manage incentive/support applications with transparency.
4. Support admin-level governance, audit, and user management.
5. Provide deployment-ready structure for institutional hosting.

## 3. System Structure
- App entry: `app.py`
- Configuration: `config.py`, `.env`
- Models and persistence: `models.py`
- Forms and input validation: `forms.py`
- Templates: `templates/`
- Assets: `static/`
- Deployment tooling: `deployment/`

## 4. Functional Areas
- User and role administration.
- Publication submission/edit/review.
- Multi-stage application workflows (journal, conference, incentives).
- Citation and periodic data updates.
- Circulars, FAQ, notifications, feedback channels.

## 5. Validation Status
- `app.py` syntax validation: passed.

## 6. Deployment Readiness
The repository includes dedicated deployment assets (service file, Nginx config, shell scripts) indicating production deployment preparedness on Ubuntu stacks.

## 7. GitHub Hygiene Recommendations
1. Keep `.env` untracked.
2. Exclude runtime DB files and sensitive uploads where required.
3. Prefer sample data fixtures over real institutional data.

## 8. Future Scope
1. Modular blueprint split from monolithic `app.py`.
2. Centralized permission matrix middleware.
3. REST API layer for mobile/admin clients.
4. Enhanced analytics and BI dashboards.
5. Full test suite (unit + integration + UI).

## 9. Conclusion
The portal is a feature-rich, institution-grade Flask platform with broad workflow coverage and deployment support. It is now documented and prepared for GitHub publication with improved repository metadata.
