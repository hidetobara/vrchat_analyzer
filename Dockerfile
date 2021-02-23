
FROM python:3.8

RUN apt update -y && apt upgrade -y && apt -y install python3-pip vim supervisor less default-mysql-server default-mysql-client \
	&& apt clean
RUN pip3 install flask gunicorn mysql-connector-python
RUN pip3 install google-cloud-bigquery google-cloud-storage
RUN pip3 install gspread oauth2client

ENV APP_HOME /app 
WORKDIR $APP_HOME
COPY . ./

RUN chmod 744 /app/running.sh
CMD ["/app/running.sh"]