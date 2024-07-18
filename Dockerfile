FROM python:3.10

WORKDIR /opt

COPY . /opt

RUN pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 5006

ENV BOKEH_ALLOW_WS_ORIGIN code.yzzzz.com.cn

CMD ["python", "-m", "ditto.main", "ser"]
