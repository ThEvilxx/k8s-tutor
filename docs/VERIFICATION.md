# 本次验证记录

日期：2026-10-26。环境：Windows，独立虚拟环境，Python 3.12.14。测试环境位于课程工作文件/缓存中，不依赖损坏的系统 Anaconda，不修改原 EasonRecommendation 项目。

- python manage.py check：通过，0 个问题。
- python manage.py makemigrations --check --dry-run：通过，没有未生成迁移。
- python manage.py test --verbosity=2：21 项测试全部通过（含答案快照不被题库变更覆盖）。
- 测试覆盖：规则判分、非法选项、答案快照、学生记录隔离、讲解 POST 限制、未发布资料过滤、演示模式无外部调用、超时降级、模型文本不改判、HTML 转义、种子数据幂等、健康接口和教师后台权限。
- 依赖版本见 requirements-tested.txt；requirements.txt 为允许的版本范围。

真实 API 尚未调用；新项目容器和远程集群尚未发布。Dockerfile 和 K8s 清单为交付框架，不将其写成线上验证结果。Web/数据库健康与模型正确性需要分别验收。
