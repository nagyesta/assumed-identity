FROM python:3.11.5-alpine3.18
LABEL maintainer="nagyesta@gmail.com"
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py  /app/
EXPOSE 80
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "80"]
