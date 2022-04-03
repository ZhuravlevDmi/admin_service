FROM python:3.10
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Novosibirsk
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
