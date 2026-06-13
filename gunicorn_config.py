import multiprocessing

bind = "0.0.0.0:10000"

workers = 2

worker_class = "sync"

timeout = 120

loglevel = "info"
accesslog = "-"
errorlog = "-"

max_requests = 1000
max_requests_jitter = 50

preload_app = True
