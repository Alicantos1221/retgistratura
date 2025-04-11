import multiprocessing

# Количество воркеров
workers = multiprocessing.cpu_count() * 2 + 1

# Таймаут в секундах
timeout = 120

# Максимальное количество запросов на воркер
max_requests = 1000

# Максимальное количество запросов на воркер перед перезапуском
max_requests_jitter = 50

# Количество потоков на воркер
threads = 2

# Логирование
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Перезапуск воркеров при изменении кода
reload = False

# Предварительная загрузка приложения
preload_app = True 