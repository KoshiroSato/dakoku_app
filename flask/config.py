wsgi_app = 'app:app'
bind = '0.0.0.0:5000'
workers = 1
timeout = 30
loglevel = 'info'
accesslog = 'output/access.log'
errorlog = 'output/error.log'