# Docker 和 Kubernetes 部署指南

以下是本新项目可复用的部署步骤，本次仅验证本地 Django 框架和配置，不代表新项目已部署到云端。之前歌曲推荐应用的镜像地址不能当作本项目镜像使用。

## 本机 Docker

在仓库根目录运行：

```powershell
docker build --platform linux/amd64 --provenance=false --sbom=false -t k8s-tutor:v1 .
$env:DJANGO_SECRET_KEY = [guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
docker volume create k8s-tutor-data
docker run --rm --mount source=k8s-tutor-data,target=/data -e DJANGO_SECRET_KEY -e DJANGO_DB_PATH=/data/db.sqlite3 k8s-tutor:v1 python manage.py migrate
docker run --rm --mount source=k8s-tutor-data,target=/data -e DJANGO_SECRET_KEY -e DJANGO_DB_PATH=/data/db.sqlite3 k8s-tutor:v1 python manage.py seed_demo
docker run --rm -it --mount source=k8s-tutor-data,target=/data -e DJANGO_SECRET_KEY -e DJANGO_DB_PATH=/data/db.sqlite3 k8s-tutor:v1 python manage.py createsuperuser
docker run -d --name k8s-tutor-v1 -p 127.0.0.1:18001:8000 --mount source=k8s-tutor-data,target=/data -e DJANGO_SECRET_KEY -e DJANGO_DB_PATH=/data/db.sqlite3 -e LLM_MODE=mock k8s-tutor:v1
```

打开 http://127.0.0.1:18001/ 。数据保存在 named volume，不在镜像里。

## ACR

在同一个 ACR 实例中创建新的私有仓库 k8s-tutor。以下 REGISTRY 只包含域名和命名空间，执行前换成你自己的地址：

```powershell
$registry = "crpi-78yyu7ue20yop9jy.cn-guangzhou.personal.cr.aliyuncs.com/easonrecommendation"
docker login crpi-78yyu7ue20yop9jy.cn-guangzhou.personal.cr.aliyuncs.com
docker tag k8s-tutor:v1 "${registry}/k8s-tutor:v1"
docker push "${registry}/k8s-tutor:v1"
```

没有授权自动执行云端仓库创建或推送；上述由操作者在自己账号执行。

## 三节点集群

确认集群为 node1 控制平面、node2/node3 工作节点。在 node2 上创建 /srv/k8s-tutor/data，演示当前容器默认 root 可读写；将来切换非 root 时必须调整目录属主与权限。这个路径独立于原 eason 应用数据。

在 node1 上：

```bash
kubectl apply -f deploy/k8s/namespace.yaml
read -r -p "ACR username: " ACR_USER
read -r -s -p "ACR password: " ACR_PASSWORD; echo
kubectl -n k8s-tutor create secret docker-registry acr-pull-secret --docker-server=crpi-78yyu7ue20yop9jy.cn-guangzhou.personal.cr.aliyuncs.com --docker-username="$ACR_USER" --docker-password="$ACR_PASSWORD"
unset ACR_USER ACR_PASSWORD
DJANGO_KEY=$(openssl rand -hex 32)
kubectl -n k8s-tutor create secret generic tutor-secrets --from-literal=DJANGO_SECRET_KEY="$DJANGO_KEY"
unset DJANGO_KEY
kubectl apply -f deploy/k8s/storage.yaml
kubectl apply -f deploy/k8s/config.yaml
REGISTRY=crpi-78yyu7ue20yop9jy.cn-guangzhou.personal.cr.aliyuncs.com/easonrecommendation
sed "s#image: k8s-tutor:v1#image: $REGISTRY/k8s-tutor:v1#g" deploy/k8s/app.yaml | kubectl apply -f -
kubectl -n k8s-tutor rollout status deployment/k8s-tutor --timeout=180s
kubectl -n k8s-tutor get pods,service,pvc -o wide
kubectl -n k8s-tutor exec -it deployment/k8s-tutor -- python manage.py createsuperuser
```

上述 sed 替换清单中两个镜像地址，不修改原文件；也可在编辑器中替换后再 apply。Init container 在每次 Pod 启动执行幂等 migrate 和 seed_demo，会重置种子题的标准内容，仅适用于本演示；正式环境迁移应拆为受控一次性发布任务，种子数据只在初始化时导入。

config.yaml 默认允许 localhost 与节点私网IP。先通过控制平面 kubectl port-forward service/k8s-tutor 18001:8000 进行验证；在本机浏览器访问需另建 SSH 隧道，或将 manifests 复制到已有 kubeconfig 的本机后本地 port-forward。若使用公网 NodePort 30081，先将公网 IP/域名加入 ConfigMap 的 DJANGO_ALLOWED_HOSTS，重启 Deployment，并把安全组来源限制为自己的公网IP/32；不使用通配主机名。正式部署使用 Ingress/TLS。

## 更新回退演示

先记录 v1 截图和历史。修改首页标题为 V2，构建并上传新镜像，保留 v1。然后：

```bash
kubectl -n k8s-tutor set image deployment/k8s-tutor web="$REGISTRY/k8s-tutor:v2" prepare="$REGISTRY/k8s-tutor:v2"
kubectl -n k8s-tutor rollout status deployment/k8s-tutor --timeout=180s
kubectl -n k8s-tutor get deployment,pods,replicaset -o wide
kubectl -n k8s-tutor rollout history deployment/k8s-tutor
kubectl -n k8s-tutor rollout undo deployment/k8s-tutor
kubectl -n k8s-tutor rollout status deployment/k8s-tutor --timeout=180s
```

不要在这个实验中同时修改数据库模型。init container 和主容器都在 Pod 模板中，一并更新后再回退。回退后检查镜像标签和网页内容，确认学习记录仍存在。演示会短暂不可用，不宣称无损数据库回退或高可用。

## 资源清理

先导出备份并核对后续课程是否复用集群。删除新项目 namespace 不影响 eason-lab；本地 PV 为 Retain，需要人工决定数据处理。本文不包含自动删除目录、云实例或仓库的命令。
