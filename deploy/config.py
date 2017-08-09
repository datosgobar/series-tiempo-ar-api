proc_name = "django_application"
workers = 9 
max_requests = 0
timeout = 30

raw_env = [
            'DJANGO_SETTINGS_MODULE=conf.settings.local'
            ]
