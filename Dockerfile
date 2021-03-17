FROM python:3.9-slim as builder

RUN python3 -m venv /opt/venv
COPY requirements.txt /opt/venv
WORKDIR /opt/venv/
RUN . /opt/venv/bin/activate && pip install -r requirements.txt

FROM python:3.9-slim
COPY --from=builder /opt/venv /opt/venv
COPY *.py /opt/venv/
WORKDIR /opt/venv/

ENV CONFIG_FILE /config.yml
ENV PORT 8080

CMD . /opt/venv/bin/activate && exec python server.py
EXPOSE 8080/tcp
