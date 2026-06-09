# Workspace 4-Zone 上下文分区模型

> 版本：v1.0 | 状态：active
> 来源：agent-planner F9 Workspace卫生 → skill-context-hygiene 引用
> 定位：规划时辅助 Workspace 卫生检查和上下文分区

---

## 4-Zone 模型

| Zone | 内容 | 持久性 | 清理策略 |
|------|------|--------|---------|
| **system** | Agent身份/SOUL/IDENTITY/技能定义 | 永久 | 不清理 |
| **stable** | memory-config.md/workspace结构，长期偏好 | 长期 | 7天无访问后降级到 dynamic |
| **dynamic** | memory/日常任务状态 | 中期 | 30天自动清理 |
| **transient** | 单次会话临时数据 | 临时 | 会话结束立即清理 |

---

## Workspace 卫生规范

- 单个方案产出文件 ≤ 10个（含归档）
- 每次方案迭代完成后，立即归档旧版到 `archive/` 子目录
- workspace 根目录文件 ≤ 50个，超过则强制归档最旧文件
- 临时文件（`_tw_*`）用完即删

---

## 规划时使用

1. **F1 验证前**：检查 system zone 是否完整（SOUL/IDENTITY 存在）
2. **F9 交付前**：确保无 transient zone 内容残留
3. **长期项目**：定期检查 stable zone 是否有 7天+未访问文件
