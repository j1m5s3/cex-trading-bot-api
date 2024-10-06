FROM python:3.10.13-slim

ARG OS_ENV

RUN echo "OS_ENV=$OS_ENV"

ENV OS_ENV=$OS_ENV
ENV RUNTIME_ENV=DOCKER

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python"]
CMD ["app.py"]