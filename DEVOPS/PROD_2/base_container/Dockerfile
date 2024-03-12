FROM python:3.11-slim
WORKDIR /usr/src/app
COPY ./src/ .
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD [ "python", "./plot.py" ]