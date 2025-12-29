

"""  Project Structure in industry stander"""



auth_project/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── tests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_models.py
│   │   │   │   ├── test_views.py
│   │   │   │   ├── test_serializers.py
│   │   │   │   └── test_tasks.py
│   │   │   ├── urls.py
│   │   │   ├── utils.py
│   │   │   ├── validators.py
│   │   │   └── views.py
│   │   └── core/
│   ├── templates/
│   └── static/
├── nginx/
│   ├── nginx.conf
│   └── nginx.prod.conf
├── scripts/
│   ├── entrypoint.sh
│   ├── start-celery.sh
│   └── start-celery-beat.sh
├── tests/
│   └── conftest.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── Makefile
└── manage.py