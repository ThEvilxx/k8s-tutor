# Kubernetes 知识练习与错题讲解助手

人工智能系统部署与运维课程期末项目，作者：谢应江（230010083）。

本项目选择教学智能体中的“知识点练习与错题讲解”功能。学生登录后选择知识点、提交单选答案、查看错题，并获得参考资料辅助的讲解。判分由服务端规则完成，大模型只负责讲解，不修改分数。

## 当前实现与边界

已实现 Django 项目、关系模型及迁移、5 个知识点和 8 道自编示例题、登录、按知识点筛选、规则判分、作答快照、个人错题、资料筛选、演示讲解、可选 API 适配器、教师后台、Docker 和 K8s 配置。测试覆盖权限隔离、判分、调用降级、HTML 转义等行为。

默认 `LLM_MODE=mock`，页面明确标注“未调用大模型”。API 模式需要自行设置有效密钥；本次交付不包含真实付费模型调用或新项目的云端部署验证。示例资料是依据官方文档自编的摘要，不能当作已经导入了教师课件。

未实现：向量库与语义 RAG、多班级、多租户、自动生成正式考题、分布式任务队列、跨请求并发付费去重、全站限流、完整的教师成绩分析。当前错题本是 Attempt 中错误作答的查询视图，不是额外的数据表。学生账号由教师在后台创建，不开放注册。

## 快速启动

需要 Python 3.11+。Windows PowerShell 示例（若电脑默认 Python 已损坏，请使用一个正常的 Python 绝对路径）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_DEBUG = "True"
$env:LLM_MODE = "mock"
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

打开 http://127.0.0.1:8000/ 。用刚创建的账号登录；/admin/ 可维护知识点、题目和资料。教师可在后台创建普通用户，普通用户不能进入教师管理区。

Linux/macOS 先 `source .venv/bin/activate`，再 `export DJANGO_DEBUG=True`。安装了 make 时可用：

```bash
make install
make migrate
make seed
make check
make test
make run
```

Windows 没有 make 也能逐条使用上述 Python 命令。默认数据库位于 data/db.sqlite3，不进入 Git。程序从进程环境变量读取配置，不自动加载 .env.example。

## 课堂演示顺序

1. 登录，选择 Deployment 知识点。
2. 故意选择错误答案，提交后查看程序判分。
3. 点击“获取讲解”，确认显示“演示讲解 未调用大模型”，并能打开资料链接。
4. 打开“我的错题”，进入记录并重练；历史错误保留。
5. 换一个普通账号，确认看不到前一个账号的记录。
6. 教师从 /admin/ 维护题库和资料，学生只能看到已发布内容。

截图位置和提交核对见 docs/SUBMISSION.md。

## API 模式

使用百炼 OpenAI 兼容 Chat Completions 接口，通过 Python 标准库发送请求，不额外依赖 SDK：

```powershell
$env:LLM_MODE = "api"
$env:LLM_API_KEY = "在本机输入自己的有效密钥"
$env:LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL = "qwen-plus"
python manage.py runserver
```

不要把真实密钥写进 README、Git 或截图。API Key 地域应与接入端点匹配。默认 20 秒超时、最多 800 输出 tokens、非思考模式。教师资料最多取同知识点的 3 段，每段最多 1200 字符。调用失败时显示明确的标准解析降级标签，判分保持不变。已保存讲解顺序重复访问会复用；并发请求仍可能重复调用，应在公开服务前补充任务锁、限流和预算控制。

## 目录

```text
config/                  Django 配置、URL、WSGI
practice/                模型、表单、视图、讲解服务、测试及迁移
practice/management/     幂等示例数据导入
templates/               登录、练习、作答结果、错题页面
static/                  页面样式
deploy/k8s/              独立命名空间、存储、配置和 Deployment 示例
docs/                    需求设计、模型设计、部署、费用、运维及提交核对
Dockerfile               无数据库和真实密钥的应用镜像
Makefile                 常用开发命令
requirements.txt         最小依赖清单
.env.example             环境变量说明，不自动读取
```

## 容器与 Kubernetes

详见 docs/DEPLOYMENT.md。演示使用单副本 SQLite、本地 PV 绑定 node2，更新先停旧 Pod 再启动新 Pod，有短暂中断，不是高可用。释放节点不会保留其本地盘。先完成备份再释放云资源。

之前歌曲推荐项目已验证过 Docker → ACR → K8s → 更新 → 回退流程；本项目沿用这套方法，不把歌曲应用的部署截图当作本项目已经部署的证据。

## 验证

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

实际依赖版本和本次验证记录见 docs/VERIFICATION.md；不把拟定指标写成已达成结果。

## Git 提交

本地目录已初始化为独立 Git 仓库。公开仓库尚未创建。提交代码前检查：

```bash
git status --short
git check-ignore .env data/db.sqlite3
git log -1 --oneline
```

如需交到 GitHub/Gitee，在自己的账号创建空仓库，再设置真实远程地址并推送：

```bash
git remote add origin <你创建的远程仓库地址>
git push -u origin main
```

不要推送 .env、SQLite、用户记录和真实凭据。提交方案文档时以期末项目目录中的 Word 成品为准。
