FROM python:3.13-alpine
ENV PYTHONUNBUFFERED=1 DATA_DIR=/data PORT=8000 TZ=Europe/Amsterdam
RUN apk add --no-cache tzdata && adduser -D -u 1000 app && mkdir /data && chown app /data
WORKDIR /app
COPY app/ /app/
USER app
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=5s CMD wget -qO- http://127.0.0.1:8000/api/state >/dev/null || exit 1
CMD ["python", "server.py"]
