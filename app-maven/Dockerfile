# User my AliCloud kubernetes JPD 
# FROM slash.jfrog.local:30012/slash-docker-framework/docker-framework:v1.0

# Use Soleng JPD docker framework image
FROM demo.jfrogchina.com/slash-docker-dev-local/docker-framework:latest

LABEL MAINTAINER="Slash"

RUN rm -rf /home/exec/tomcat/webapps/*

ADD target/*.war /home/exec/tomcat/webapps/ROOT.war

CMD /bin/bash -c cd /home/exec; /home/exec/tomcat/bin/catalina.sh run
