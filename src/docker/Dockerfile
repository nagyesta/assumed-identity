FROM python:3.12.1-alpine3.18
LABEL maintainer="nagyesta@gmail.com"
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py  /app/
EXPOSE 80
CMD [ "sh", "-c", "ls /app" ]
ENTRYPOINT ["sh", "-c", "python app.py --host ${ASSUMED_ID_HOST:-0.0.0.0} --port ${ASSUMED_ID_PORT:-80}"]
