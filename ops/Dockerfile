# 使用轻量级的 Ubuntu 作为底座
FROM ubuntu:22.04

# 设置环境变量，方便后续维护
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV CATALINA_HOME=/home/exec/tomcat
ENV PATH=$PATH:$JAVA_HOME/bin:$CATALINA_HOME/bin

# 1. 安装 JDK 17 和必要的工具
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. 创建运行目录并安装 Tomcat 10
WORKDIR /home/exec
RUN wget https://archive.apache.org/dist/tomcat/tomcat-10/v10.1.18/bin/apache-tomcat-10.1.18.tar.gz -O tomcat.tar.gz \
    && tar -xzf tomcat.tar.gz \
    && mv apache-tomcat-10.1.18 $CATALINA_HOME \
    && rm tomcat.tar.gz \
    && rm -rf $CATALINA_HOME/webapps/*

# 3. 赋予执行权限
RUN chmod +x $CATALINA_HOME/bin/*.sh

# 暴露 Tomcat 默认端口
EXPOSE 8080

# 保持镜像简洁，不设置 CMD（留给应用层 Dockerfile 设置）
