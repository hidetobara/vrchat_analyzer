
FROM python:3.8

RUN apt update -y && apt upgrade -y && apt -y install python3-pip vim supervisor less \
	&& apt clean
RUN pip3 install flask gunicorn
RUN pip3 install google-cloud-bigquery google-cloud-storage

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD exec gunicorn --bind :8080 --workers 1 --threads 4 --timeout 0 app:app