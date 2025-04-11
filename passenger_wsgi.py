import os
import sys

from dotenv import load_dotenv
load_dotenv()

# Путь к виртуальному окружению
VENV_PATH = os.path.join(os.getcwd(), 'venv', 'lib', 'python3.9', 'site-packages')

# Путь к проекту
PROJECT_PATH = os.getcwd()

# Добавляем пути в системные пути
sys.path.insert(0, VENV_PATH)
sys.path.insert(0, PROJECT_PATH)

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Poliklinika.settings')

# Импорт и получение application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 