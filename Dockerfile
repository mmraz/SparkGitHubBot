FROM python:alpine 

LABEL maintainer="Michael Mraz <michael.mraz@here.com>"

RUN pip install flask

ADD gitlab-bot.py

EXPOSE 8080

ENTRYPOINT ["python", "gitlab-bot.py"]
