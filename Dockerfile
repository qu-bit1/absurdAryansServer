FROM python:3.9-slim

WORKDIR /app

COPY app.py /app/
COPY . /app/

RUN pip install flask

ENV USE_CUSTOM_DICTIONARY False
VOLUME /app/custom_dictionary/dictionary.csv
EXPOSE 5000

CMD ["python", "app.py"]
