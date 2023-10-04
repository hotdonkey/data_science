FROM tiangolo/uwsgi-nginx-flask:python3.9
WORKDIR /usr/src/app
COPY ./src ./
COPY ./requirements.txt ./
COPY ./uwsgi.ini ./
ARG TARGETPLATFORM=linux/arm64/v8
RUN pip install -r requirements.txt
CMD ["python","flask_server.py"]