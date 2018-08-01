import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
loglevel = 'info'
secure_scheme_headers = {
    'HTTP_X_FORWARDED_PROTO': 'https'
}
