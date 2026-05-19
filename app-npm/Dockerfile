# 使用官方 Node.js 镜像作为基础镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 配置 npm 使用 JFrog Artifactory 作为私有仓库（可选）
ARG JPD_URL
ARG NPM_REGISTRY=https://${JPD_URL}/artifactory/api/npm/slash-npm-virtual/
ARG NPM_AUTH_TOKEN

RUN npm config set registry ${NPM_REGISTRY}
RUN if [ -n "$NPM_AUTH_TOKEN" ]; then \
    npm config set //${JPD_URL}/artifactory/api/npm/slash-npm-virtual/:_authToken=${NPM_AUTH_TOKEN}; \
    fi

# 先复制 package.json，利用 Docker 缓存层
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY src/ ./src/

# 暴露端口（如果是 web 服务）
EXPOSE 3000

# 启动命令
CMD ["node", "src/index.js"]
