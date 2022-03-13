#!/bin/bash

gnome-terminal -- /bin/bash -c 'redis-server'
gnome-terminal -- /bin/bash -c 'source venv/bin/activate; celery -A update_ticks_using_celery worker --loglevel=info'
gnome-terminal -- /bin/bash -c 'source venv/bin/activate; python3 main_.py'