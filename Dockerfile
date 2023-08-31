FROM python:3.9-slim

WORKDIR /app

COPY app.py /app/
COPY . /app/

RUN pip install flask
RUN pip install numpy

ENV USE_CUSTOM_DICTIONARY False
VOLUME /app/custom_dictionary/dictionary.csv
EXPOSE 5000

CMD ["python", "app.py"]
