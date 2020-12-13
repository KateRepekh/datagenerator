web: gunicorn datagenerator.wsgi
worker: celery -A datagenerator worker -B -l INFO
