FROM python:3.8.10-slim

WORKDIR /app

COPY ./backend/ .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]