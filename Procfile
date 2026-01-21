web: cd EduRise && gunicorn edurise.wsgi --bind 0.0.0.0:$PORT
release: cd EduRise && python manage.py migrate && python manage.py collectstatic --noinput