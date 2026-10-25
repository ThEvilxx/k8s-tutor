# 数据库设计

采用 Django ORM，演示数据库 SQLite，数据目录与代码镜像分离。正式多用户部署可更换 PostgreSQL/MySQL，但需要同步完成依赖、配置、迁移与性能验证，当前未实现数据库切换开关。

| 实体 | 主要字段 | 约束和用途 |
|---|---|---|
| auth_user | username、password、is_staff | Django 内置；密码使用框架哈希 |
| KnowledgePoint | code、title、summary | code 唯一；课程知识点 |
| Question | code、point_id、stem、options、answer、reference、published | 单选题；标准答案必须在 A-D 的有效选项中 |
| KnowledgeSnippet | point_id、title、content、source_url、source_version、published | 教师审核资料；仅使用已发布记录 |
| Attempt | user_id、question_id、selected、answer_snapshot、reference_snapshot、is_correct、created_at | 保存判分快照；按用户和是否正确建索引 |
| Explanation | attempt_id、body、mode、model、references、input_tokens、output_tokens、created_at | attempt 唯一；保存讲解、提供给模型的来源及 usage |

关系：User 1:N Attempt；KnowledgePoint 1:N Question；KnowledgePoint 1:N KnowledgeSnippet；Question 1:N Attempt；Attempt 1:0..1 Explanation。

错题本不单独建表，使用 Attempt.objects.filter(user=当前用户, is_correct=False)。重练产生新记录，历史不被覆盖。当前未保存题干、选项和资料正文的完整历史版本；生产审计需增加不可变内容版本和引用快照。

权限：视图同时使用登录检查和 user=request.user 过滤；越权读取或请求讲解返回 404。讲解只允许 POST，启用 CSRF；教师后台使用 is_staff 和 Django 权限。删除用户级联清理其作答和讲解；数据保留期限由学校规定，试用环境应提供人工删除流程。
