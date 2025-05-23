FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p data/vids data/subtitles data/result
RUN python -c "import nltk; nltk.download('punkt_tab')"

CMD ["python", "video_recap.py"]