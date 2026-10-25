# 后期运维

## 每次演示

检查 kubectl get nodes、工作负载 Ready、/healthz/ HTTP 200、登录与错题页面、PV/PVC Bound、磁盘余量。健康接口只检查 Web 进程可响应，不代表数据库和外部模型完整可用；数据库故障通过业务检查补充。

## 备份和恢复

SQLite 运行时不能仅凭复制单文件保证一致性。使用 Python sqlite3.Connection.backup 在容器内生成一致性快照，再用 docker cp 或 kubectl cp 导出；kubectl cp 需要镜像内有 tar。提供 scripts/backup_db.py，输出位置必须是独立备份文件；备份包含学生记录，不进入仓库或公共截图。

恢复前停止应用写入，备份当前文件，将快照恢复到独立测试目录，运行 python manage.py check 和登录/题目/错题测试。确认后再恢复正式目录。Retain 只影响卷回收策略，不等于云端备份。

## 更新与回退

发布唯一标签 v1/v2 或提交号，不覆盖已验证的标签。发布前测试、备份数据库，执行 set image、rollout status，记录镜像 digest 和页面版本。APP_VERSION 可作为展示标识，但不能仅凭它证明镜像已替换，需同时检查 image 字段、Pod 和 ReplicaSet。

当前单副本 maxSurge=0、maxUnavailable=1 会短暂中断。rollback 恢复 Pod 模板但不撤销迁移；包含不兼容 schema 时停止自动回退，按备份恢复流程处理。不要以 rollout undo 当数据库恢复工具。

## 故障检查顺序

Pending 看 describe 的调度/存储事件；ImagePullBackOff 查完整镜像地址、Secret 命名空间及网络；CrashLoopBackOff 查 logs --previous、密钥和数据目录；Service 不通先容器/EndpointSlice 再节点端口/安全组。模型超时先看 fallback 标签和端点连通性，避免反复重试产生费用。所有日志省略密钥、请求头、账号和详细学生答案。

## 正式开放前

使用 HTTPS、显式 ALLOWED_HOSTS、secure cookies、CSRF trusted origins；限制教师权限；配置账号策略、按用户限流、模型预算和告警。当前没有全站限流、异步队列和并发付费幂等锁，只适合受控课堂演示。试用记录到期清理，保留期限由课程管理决定。
