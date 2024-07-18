FROM python:3.10


WORKDIR /opt

COPY . /opt

RUN pip install .

EXPOSE 5006

CMD ["python", "-m", "ditto.main"]