# CI/CD 集成

> 版本：v1.0 | 状态：reference
> 来源：auditor v6.2 增强层A参考

---

## 集成方式

### 1. 作为 CI/CD Pipeline 的一部分

```bash
# 变更提交前触发 auditor
openclaw audit --scope workspace --risk-level auto
```

### 2. Git Hooks 集成

```bash
# .git/hooks/pre-commit
openclaw audit --scope staged --output json > audit-result.json
```

### 3. CI Pipeline Stage

```yaml
# .github/workflows/audit.yml
- name: Auditor Check
  run: openclaw audit --scope changed --fail-on P0
```

---

## 增强层A触发条件

- S1战略评估时
- 涉及CI/CD配置的变更
- 多文件变更需验证一致性

---

## 输出格式

```json
{
  "audit_id": "audit-{YYYYMMDD}-{seq}",
  "passed": true,
  "findings": [],
  "warnings": [],
  "blocked": false
}
```