Deployment checklist and quick steps

1) Environment
- Copy `.env.example` to `.env` and fill values (SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS, email settings).

2) Install requirements
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Migrate & collectstatic
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

4) Run checks & tests
```bash
python manage.py check
python manage.py test
```

5) Run with Docker (local)
```bash
docker-compose build
docker-compose up
```

6) Deploy to a host (example: DigitalOcean/Heroku)
- For Heroku: `heroku buildpacks:set heroku/python` then `git push heroku main` with `Procfile` present.
- For Docker: push image to registry and deploy using your provider.

7) Security
- Set `DEBUG=False` in production.
- Configure HTTPS (TLS) and secure headers.

Notes
- `yearscore/settings_prod.py` is a suggested production settings file; set `DJANGO_SETTINGS_MODULE=yearscore.settings_prod` in your production environment.
- If you use Postgres, ensure `psycopg2-binary` is installed (already in `requirements.txt`).
