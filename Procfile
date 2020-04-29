web: FILL_DB=True inv unicorn
release: ./manage.py migrate --noinput && inv install-s3-policy && pip install scout-apm
