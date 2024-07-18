FROM python:3.10

WORKDIR /opt

COPY . /opt

RUN pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 5006

CMD ["python", "-m", "ditto.main", "ser"]