FROM python:3.11.0-slim

ARG FLASK_USER=ledokolych

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /smr_scheduler

RUN groupadd -r ${FLASK_USER} && \
    useradd -m -r -g ${FLASK_USER} ${FLASK_USER} && \
    chown -R ${FLASK_USER}:${FLASK_USER} /smr_scheduler

USER ${FLASK_USER}

WORKDIR /smr_scheduler

RUN pip install --upgrade pip && \
    pip install -q --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python", "website/app.py" ]