---
name: lifecycle
description: 方案包生命周期与流程状态管理；实际创建/迁移方案包、扫描遗留方案或需要记录命令授权与等待项时读取。
invocation: model
side_effects: may_move_plan_packages
requires: []
completion_criteria: 存在方案包时其状态、迁移位置、history 索引和遗留扫描均已完成；流程状态已在终态清理，无方案包路径未创建伪生命周期记录。
---

# 方案包生命周期与流程状态

**适用范围:** 方案包的创建路径、任务状态、迁移和遗留扫描，以及三项会话内流程状态。无方案包的改动不触发迁移。

不由 `lifecycle` 负责: 知识库内容（`kb`）、任务执行和验证（`develop`）、输出模板（`output-format`）。

---

## 方案包

**任务状态符号:**
- `[ ]` 待执行
- `[√]` 已完成
- `[X]` 执行失败
- `[-]` 已跳过
- `[?]` 待确认

**创建:**

```yaml
路径: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/
同名冲突: 目录已存在时使用版本后缀 _v2, _v3...
```

**迁移（方案包已执行时必须完成）:**

```yaml
步骤:
  1. task.md 的任务状态和备注反映实际执行结果
  2. 移动到 helloagents/<branch-name>/history/YYYY-MM/（YYYY-MM 取自方案包目录名）
  3. 更新 helloagents/<branch-name>/history/index.md

no-clobber 不变量:
  - QA 通过后、写入任何 history 链接前计算唯一目标并记为 RESOLVED_ARCHIVE_PATH
  - 目标已存在时递增 _v2, _v3 后缀；无法获得唯一目标时停止并保留 plan 源目录
  - 移动前再次复核目标；被占用时重算，并先修正已写入的链接
  - 禁止覆盖或合并既有归档
  - 移动或索引更新失败时保留可恢复证据，不得报告为成功
```

**遗留方案扫描:**

```yaml
时机: 方案包创建后（方案设计、~plan 完成），或方案包迁移后（~exec、~auto、设计后执行完成）
规则: 扫描 helloagents/<branch-name>/plan/，排除本次创建或执行的方案包
输出: 存在遗留项时才提示，格式见 output-format 的遗留方案清单
```

用户明确表示某个遗留方案不再执行时，把未完成任务标为 `[-]` 并备注“已取消”，再按迁移规则归档。

---

## 流程状态

只维护三项，均为会话内状态，不写入文件:

```yaml
ACTIVE_COMMAND: none | auto | plan | exec
  - 用户输入对应命令时设置，只对该命令的本次任务有效
  - 不替代 EHRB 确认，也不扩大命令本身的范围（plan 不写业务代码）

CURRENT_PACKAGE: 本次创建或执行的方案包路径
  - RESOLVED_ARCHIVE_PATH 是它的唯一归档目标；知识库链接、history 索引、迁移和最终输出引用同一个值

PENDING: 正在等待用户回答的一个问题及其选项
  - 输出询问时记录；同一时间只有一个
  - 回复只消费一次，随后清除
  - 回复与等待的问题不对应时不套用；用户提出明确的新需求时先清除再重新路由
```

**终态清理:** 任务成功、取消、终止、出错，或用户提出新需求时，清除以上全部状态。命令授权和等待项不得沿用到下一个任务。清理只针对流程状态，不删除 `plan/`、`history/` 文件或工作区改动。

**上下文恢复:** 同一任务因上下文压缩或会话恢复而继续时，不视为新任务。从 `CURRENT_PACKAGE`、`task.md` 状态和已有验证证据确认进度，已标记完成且证据仍有效的任务不重放；状态无法确认时做有边界的只读探查，不凭空推断已完成。通用的复核边界见 bootstrap。

---

## 正反例

**应触发:**
- 方案设计完成后创建方案包目录。
- 开发实施完成后把方案包迁移到 `history/YYYY-MM/`。
- 命令完成时扫描 `plan/` 中剩余未执行的方案包。

**不应触发:**
- 只更新 `wiki/modules/*.md` 的内容；这是 `kb` 的职责。
- 无方案包的低/中风险改动。

---

## 完成门禁

- 方案包路径符合 `helloagents/<branch-name>/plan|history/YYYY-MM/YYYYMMDDHHMM_<feature>/`。
- `task.md` 中每个任务都有状态符号，非完成项有备注。
- 迁移后 `history/index.md` 已更新，未覆盖既有归档。
- 遗留扫描已排除本次创建或执行的方案包。
- 终态已清理流程状态，不存在跨任务的命令授权或等待项残留。
