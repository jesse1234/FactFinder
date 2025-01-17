FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
# Copy local code to container image
ENV APP_HOME /back-end
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
