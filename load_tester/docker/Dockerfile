FROM locustio/locust

ADD locust-tasks /locust-tasks

EXPOSE 5558

RUN chmod 755 /locust-tasks/run.sh

ENTRYPOINT ["/locust-tasks/run.sh"] 
