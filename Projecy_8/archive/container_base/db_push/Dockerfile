FROM python:latest
WORKDIR /usr/src/app
COPY ./src ./
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python","db_push.py"]