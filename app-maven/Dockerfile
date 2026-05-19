FROM slash.jfrog.local:30012/slash-docker-framework/docker-framework:v1.0

LABEL MAINTAINER="Slash"

RUN rm -rf /home/exec/tomcat/webapps/*

ADD target/*.war /home/exec/tomcat/webapps/ROOT.war

CMD /bin/bash -c cd /home/exec; /home/exec/tomcat/bin/catalina.sh run
