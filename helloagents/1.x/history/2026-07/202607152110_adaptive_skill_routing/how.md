# 技术设计: 自适应 Skill 路由与 Eval 基线

## 技术方案

### 核心技术

- Python 标准库实现 eval 数据校验与结果评分。
- JSON 保存可审查、可跨平台读取的行为用例。
- unittest 固化 eval schema、覆盖要求、bootstrap 体量和路由语义。

### 实现要点

- `evals/skill_routing_cases.json` 使用稳定枚举描述 `route`、`action`、`confirmation`、`artifacts` 和 `risk`。
- `scripts/eval_skills.py` 默认校验数据集；通过 `--results` 对外部执行结果进行评分。
- routing 从文件数量阈值改为低/中/高风险判定，并把系统化调试拆为“调查门禁 + 风险化实施出口”。
- develop 新增“用户明确授权的自适应开发入口”，仅适用于低/中风险且无 EHRB 的普通改动。

## 设计边界

- **范围内:** 行为 eval、bootstrap 常驻信息、routing/develop 授权与路径描述。
- **范围外:** lifecycle 状态持久化、hooks、外部模型 runner、现有方案包格式。
- **模块职责:** eval 定义行为基线；routing 决定风险路径；develop 负责诊断与实施门禁；bootstrap 只做最小调度。
- **接口契约:** `python scripts/eval_skills.py [--results PATH]` 返回 0 表示数据或结果满足门槛，返回 1 表示校验或评分失败。
- **数据边界:** eval 文件不包含密钥、PII 或外部数据；结果文件仅包含 case ID 和结构化实际结果。
- **依赖边界:** 仅使用 Python 标准库，不新增第三方依赖。
- **大型项目最小改动:** 不调整无关 Skills，不修改安装副本，不处理既有 bridge 漂移。

## 架构决策 ADR

### ADR-008: 默认采用风险自适应路由并保留严格命令路径

**上下文:** 文件数量不能可靠代表风险，且用户明确改动请求被重复确认阻断。

**决策:** 普通请求按可逆性、外部副作用、公共契约、数据迁移和不确定性分级；低/中风险连续实施，高风险方案确认。现有 `~auto/~plan/~exec` 继续保留。

**理由:** 让流程成本与真实风险成比例，同时保持兼容性和高风险控制。

**替代方案:** 继续按文件数路由并仅放宽 Bug → 拒绝原因: 仍无法覆盖单文件功能、多文件机械改动等常见边界。

**影响:** routing/develop 规则和 bootstrap 摘要需要同步；必须通过 eval 防止安全边界回退。

**状态:** 已采纳

## 安全与性能

- **安全:** EHRB、生产、支付、权限、不可逆变更和敏感数据用例必须保持确认或只读路径。
- **性能:** bootstrap 行数和字节数纳入测试；eval 校验为本地线性扫描。

## 测试与部署

- **测试:** 先添加 eval/schema/bootstrap/路由契约测试并确认失败，再完成实现；运行全量 unittest、Skill 审计和安全审计。
- **部署:** 仅修改仓库源文件，不安装到用户全局目录；安装仍由现有 `manage_skills.py --install` 显式执行。
