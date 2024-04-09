FROM python:3.10
WORKDIR /app
COPY . ./
COPY ./requirements.txt ./
RUN apt-get update && apt-get install -y build-essential
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
VOLUME /app/data
CMD [ "python", "flask_server.py" ]
