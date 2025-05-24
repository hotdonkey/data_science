FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir nltk

RUN python -c "import nltk; nltk.download('punkt')"
RUN python -c "import nltk; nltk.download('punkt_tab')"

RUN mkdir -p /app/data/vids /app/data/subtitles /app/data/result

COPY . .

CMD ["python", "video_recap.py"]