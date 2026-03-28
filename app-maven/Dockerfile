FROM soleng.jfrog.io/slash-docker-dev-local/docker-framework:latest

LABEL MAINTAINER="Slash"

RUN rm -rf /home/exec/tomcat/webapps/*

ADD target/app-simple-boot-*.war /home/exec/tomcat/webapps/ROOT.war

CMD /bin/bash -c cd /home/exec; /home/exec/tomcat/bin/catalina.sh run
