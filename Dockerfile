FROM python:3.10

WORKDIR /opt

COPY . /opt

RUN pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 5006

ENV BOKEH_ALLOW_WS_ORIGIN=*

CMD ["python", "-m", "ditto.main", "serv"]
