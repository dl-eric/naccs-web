FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 443

COPY ./app /app
COPY custom.conf /etc/nginx/conf.d/
COPY collegiatecounterstrike-cert.pem /etc/nginx/ssl/
COPY collegiatecounterstrike-priv.pem.key /etc/nginx/ssl/
