Deploying to Render (quick guide)

Prereqs
- Push your repo to GitHub (or connect your Git provider to Render).
- Install `render` CLI locally if you want to operate from terminal (optional): https://render.com/docs/cli

Quick steps (recommended)
1) Create Render account and connect your Git repo.
2) In Render dashboard, create a new service and connect it to the `main` branch.
   - Service type: "Web Service"
   - Environment: "Docker"
   - Start command: `gunicorn yearscore.wsgi:application --bind 0.0.0.0:$PORT`
   - Region: choose the nearest region.
   - Or simply let Render read `render.yaml` in the repo to create service and database.

3) Add a managed Postgres (Render can create one automatically from `render.yaml`).
4) Set environment variables/secrets in the Service dashboard (Environment > Environment Variables):
   - `SECRET_KEY` (strong random value)
   - `DEBUG` = `0`
   - `ALLOWED_HOSTS` = `.onrender.com` or your domain
   - `DJANGO_SETTINGS_MODULE` = `yearscore.settings_prod` (optional)
   - `DATABASE_URL` = (if not using the managed DB from `render.yaml`)
   - Email/SMTP credentials if you use email features
   - Any storage credentials (S3) if you plan to serve media from object storage

5) Deploy (Render will build the Docker image and deploy automatically once the service is created).

6) Run migrations and collectstatic (use the Render dashboard shell or CLI):
   - In Render dashboard: open the service, click "Shell" and run:

```
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

7) Media files
- Render instances are ephemeral. Use S3 (or another object store) and configure `django-storages` for `DEFAULT_FILE_STORAGE`.
- Alternatively, use Render Volumes (not ideal for scaling). See Render docs for details.

8) Logs and troubleshooting
```
# View logs in dashboard or CLI
render logs service performance-tracker
```

Tips
- Keep secrets out of `render.yaml`; set them in the dashboard.
- Ensure `requirements.txt` includes `gunicorn` and `psycopg2-binary`.
- If you want a zero-downtime deploy strategy, review Render docs for rollout configuration.

If you want, I can:
- create/adjust `yearscore/settings_prod.py` and sample `.env` entries for Render,
- add S3 integration code for media/static collection,
- or run a local Docker smoke test (`docker build` / `docker run`).

Which of these should I do next?