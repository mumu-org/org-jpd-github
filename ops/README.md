# 工程部署
## 1. 环境
使用阿里云 vm 自建 kubernetes 环境部署的 JFrog Platform  
访问地址：  
https://slash.jfrog.local:30012/

kubernetes master worker 需配置 hosts
```
<JPD IP>  slash.jfrog.local
```

## 1. 构建基础镜像
构建 Dockerfile
```
docker build --platform linux/amd64 -t docker-framework:v1.0 -f Dockerfile .
docker tag docker-framework:v1.0 slash.jfrog.local:30012/slash-docker-framework/docker-framework:v1.0
docker push slash.jfrog.local:30012/slash-docker-framework/docker-framework:v1.0
```

## 2. 构建应用镜像
```
cd ../app-maven

docker build --platform linux/amd64 -t docker-app-maven:v2.0.0 -f Dockerfile .
docker tag docker-app-maven:v2.0.0 slash.jfrog.local:30012/slash-docker-virtual/docker-app-maven:v2.0.0
docker push slash.jfrog.local:30012/slash-docker-virtual/docker-app-maven:v2.0.0
```

## 3. Helm 部署

```
kubectl create secret docker-registry slash-jpd-docker-registry \
  --namespace=slash-runtime-demo \
  --docker-server=slash.jfrog.local:30012 \
  --docker-username=<username> \
  --docker-password=<password/token>

kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 4. Troubleshooting
### Q1 自签证书 JPD，pull image 问题
kubernetes 部署应用从自签证书环境的 JFrog 拉取镜像报错
```
tls: failed to verify certificate: x509: certificate relies on legacy Common Name field, use SANs instead
```

<h3>解决方案：</h3>

kubernetes 默认使用的是 Containerd  
- 登录到 k8s-worker 节点
- 找到 [plugins."io.containerd.grpc.v1.cri".registry.configs] 部分，添加如下配置：
```
[plugins."io.containerd.grpc.v1.cri".registry.configs."slash.jfrog.local:30012".tls] insecure_skip_verify = true
```
- 重启 Containerd
```
sudo systemctl restart containerd
```




