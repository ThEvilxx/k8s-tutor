# 作业要求与提交核对

| 老师要求 | 对应交付 |
|---|---|
| 教学智能体中的一个功能点 | Kubernetes 知识练习与错题讲解 |
| 功能介绍 | Word 第1章、README、DESIGN |
| 大模型介入合理性 | Word 第3章、LLM.md、practice/services.py |
| 数据来源、数据库设计、可行性 | Word 第4/5章、DATA_MODEL、models、迁移与种子题 |
| 部署方案、后期运维 | Word 第6/7章、Dockerfile、deploy/k8s、OPERATIONS |
| 用户部署费用和硬件 | Word 第8章、COSTS.md |
| Git 仓库、readme、Makefile、requirements、Django 框架 | k8s-tutor 独立本地仓库 |

提交前检查 Word 中姓名学号、功能范围和费用假设；检查 Git 没有真实密钥、数据库及学生信息。
提交包提供源代码和文档；隐藏 .git 不在普通源码 ZIP 中，需真实远程 URL 时在本人 GitHub/Gitee 创建空仓库并按 README 推送。未自动替用户创建账号或公开发布代码。

## 可选现场演示及截图

F01 项目目录及 git log；F02 migrate/check/test；F03 登录与题库；F04 错误作答与规则判分；F05 演示讲解和来源链接；F06 个人错题及重练；F07 教师题库后台。
后续真实调用 API 后才能增加“真实模型讲解”截图。新项目真实云部署后才能增加 ACR、Deployment、V2/回退截图，不能复用歌曲推荐网页冒充新项目。

## 推荐答辩说明

我选择教学智能体的练习与错题讲解功能。程序负责客观判分，模型负责解释并给复习建议；默认演示模式能断网运行。资料由教师审核，当前按知识点筛选，不把它描述成已经完成的向量 RAG。数据与镜像分离，Kubernetes 单副本更新有中断。后续重点是内容审核、真实模型评估和多用户稳定性。
