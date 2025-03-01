import os
import Celery

# Définir le module Django pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siade25.settings')

app = Celery('siade25')

# Charger la configuration de Celery depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover des tâches dans les applications Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')