# Multi-stage Dockerfile for Jellyfin Media Downloader

FROM python:3.11-alpine

RUN addgroup -g 1000 downloader && \
    adduser -u 1000 -G downloader -s /bin/sh -D downloader


ENV PATH=/home/downloader/.local/bin:$PATH

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY getJellyfin.py .

RUN mkdir -p /data && chown -R downloader:downloader /data /app

USER downloader

ENV JELLYFIN_URL=""
ENV USER_NAME=""
ENV JELLYFIN_PASSWORD=""
ENV DOWNLOAD_PATH="/data"
ENV DRY_RUN="false"

VOLUME ["/data"]

CMD ["python3", "getJellyfin.py"]
