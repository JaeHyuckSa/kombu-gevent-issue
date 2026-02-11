import os
import ssl

SECRET_KEY = "reproduce"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "app"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqps://guest:guest@localhost:5671//")
_ca = os.environ.get("CA_CERT_PATH", "/tls/ca-cert.pem")
CELERY_BROKER_USE_SSL = {"ca_certs": _ca, "cert_reqs": ssl.CERT_REQUIRED} if os.path.exists(_ca) else False
CELERY_TASK_DEFAULT_QUEUE = "gevent"
CELERY_TASK_DEFAULT_EXCHANGE = "celery"
CELERY_TASK_DEFAULT_ROUTING_KEY = "gevent.default"
CELERY_BROKER_HEARTBEAT = 10
CELERY_BROKER_CONNECTION_TIMEOUT = 10
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
