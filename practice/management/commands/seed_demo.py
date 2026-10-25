"""幂等写入自编示例题；不含真实学生数据，不联网抓取资料。"""
from django.core.management.base import BaseCommand
from practice.models import KnowledgePoint, KnowledgeSnippet, Question

ITEMS = [
    ("pod", "Pod 与容器", "Pod 是 Kubernetes 调度和管理的基本运行单元。",
     "https://kubernetes.io/docs/concepts/workloads/pods/",
     "Pod 可以包含一个或多个紧密协作的容器，共享网络命名空间等资源。",
     "Kubernetes 中最小的可部署计算单元是什么？",
     {"A": "容器镜像", "B": "Pod", "C": "Deployment", "D": "Service"}, "B",
     "Pod 是最小的可部署计算单元。镜像是运行容器的模板，Deployment 则管理 Pod 的期望状态。"),
    ("deployment", "Deployment 更新与回退", "Deployment 通过 ReplicaSet 管理 Pod 副本。",
     "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/",
     "Deployment 通过更改 Pod 模板产生修订；删除其管理的 Pod 后，ReplicaSet 会补足期望副本。",
     "删除由 Deployment 管理的一个 Pod 后，在副本期望值不变且资源充足时通常会怎样？",
     {"A": "Deployment 自动删除", "B": "永远减少一个副本", "C": "控制器创建替代 Pod", "D": "必须重建集群"}, "C",
     "ReplicaSet 持续比较实际副本数与期望值，在 Pod 被删除后创建替代 Pod，并非恢复同一个 Pod。"),
    ("service", "Service 与访问入口", "Service 为一组匹配标签的 Pod 提供稳定访问入口。",
     "https://kubernetes.io/docs/concepts/services-networking/service/",
     "NodePort 类型通过节点端口提供访问，仍受安全组、防火墙、路由和后端就绪状态影响。",
     "NodePort 已创建但浏览器访问超时，应该优先检查哪项？",
     {"A": "立即重装 Django", "B": "只修改网页标题", "C": "删除所有节点", "D": "安全组、端口和 Service 后端"}, "D",
     "创建 Service 不会自动放行云安全组。应核对访问 IP、NodePort、网络规则及 EndpointSlice 中的就绪后端。"),
    ("storage", "持久卷与数据库", "PV 描述存储资源，PVC 描述应用的存储申请。",
     "https://kubernetes.io/docs/concepts/storage/persistent-volumes/",
     "持久卷的生命周期独立于单个 Pod；本地卷依赖所属节点，不能等同于跨节点高可用。",
     "SQLite 文件只放在容器可写层中，有什么主要风险？",
     {"A": "Pod 替换后数据库可能丢失", "B": "自动变成 MySQL", "C": "不能进行查询", "D": "必然使用 GPU"}, "A",
     "容器可写层不适合作为持久数据库存储。应挂载独立数据目录，并设置备份与恢复措施。"),
    ("registry", "镜像仓库与凭据", "私有镜像拉取需要集群中的凭据。",
     "https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/",
     "imagePullSecrets 所引用的 Secret 必须位于 Pod 所在命名空间，且注册表地址应与镜像匹配。",
     "电脑已经 docker login，集群仍无法拉取私有镜像，应该怎样处理？",
     {"A": "把密码写入 Dockerfile", "B": "在 Pod 命名空间创建并引用拉取 Secret", "C": "清空数据库", "D": "关闭 kubelet"}, "B",
     "本机登录状态不会自动传递给 Kubernetes。应在应用命名空间中配置 imagePullSecrets，核对账号和仓库地址。"),
]
EXTRA = [
    ("deployment", "rollback", "kubectl rollout undo 会自动回退哪一项？",
     {"A": "外部数据库的全部数据", "B": "云服务器系统盘", "C": "Deployment 的历史 Pod 模板", "D": "Git 的所有提交"}, "C",
     "rollout undo 使用历史 Pod 模板恢复工作负载配置，不会自动撤销数据库迁移或外部数据变更。"),
    ("pod", "kubectl", "工作节点执行 kubectl 连接 localhost:8080 被拒绝，首先检查什么？",
     {"A": "是否配置了正确的 kubeconfig", "B": "CPU 是否为四核", "C": "数据库密码", "D": "浏览器缓存"}, "A",
     "这通常表示 kubectl 没有有效的集群连接配置，不代表集群控制平面必然停止。应检查执行位置与 KUBECONFIG。"),
    ("storage", "update", "单副本 SQLite 演示应用采用先停旧 Pod 再起新 Pod，会有什么影响？",
     {"A": "保证零停机", "B": "更新期间可能短暂不可访问", "C": "必然删除 PV", "D": "必须使用两个 GPU"}, "B",
     "这种策略限制新旧应用同时访问本地 SQLite，但会带来短暂中断，不应宣称零停机或高可用。"),
]
class Command(BaseCommand):
    help = "导入 5 个知识点、5 段自编摘要及 8 道示例单选题"
    def handle(self, *args, **options):
        for code, title, summary, url, snippet, stem, choices, answer, reference in ITEMS:
            point, _ = KnowledgePoint.objects.update_or_create(code=code, defaults={"title": title, "summary": summary})
            KnowledgeSnippet.objects.update_or_create(point=point, title=title + "资料摘要",
                defaults={"content": snippet, "source_url": url, "published": True})
            Question.objects.update_or_create(code=code + "-basic", defaults={
                "point": point, "stem": stem, "options": choices, "answer": answer,
                "reference": reference, "published": True})
        for point_code, code, stem, choices, answer, reference in EXTRA:
            Question.objects.update_or_create(code=code, defaults={
                "point": KnowledgePoint.objects.get(code=point_code), "stem": stem,
                "options": choices, "answer": answer, "reference": reference, "published": True})
        self.stdout.write(self.style.SUCCESS("示例数据准备完成：5 个知识点，8 道题；重复执行不会重复创建。"))
