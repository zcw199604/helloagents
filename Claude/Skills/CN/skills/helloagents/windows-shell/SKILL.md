---
name: windows-shell
description: Windows PowerShell 编码规则与语法约束；Platform=win32 且需要使用 shell 命令时读取
---

# Windows PowerShell 环境规则

**适用范围:** Platform=win32 且 AI 内置工具无法满足、需要使用 shell 命令时；bootstrap G1 中的 PowerShell 段落已迁移至此 Skill。

---

## 核心原则

- 文件操作优先使用 AI 内置工具，仅在必要时使用 shell 命令
- 使用 shell 命令时须遵循下方"编码规则"和"语法约束"
- 跨平台兼容: 仅使用 PowerShell 原生 cmdlet 和语法
- 执行前验证: 在内部思考中验证语法完整性（转义闭合、括号匹配、参数格式），不确定时查询文档

---

## 编码规则

```yaml
读取: 自动检测并使用文件原编码或指定 -Encoding UTF8
写入: 默认必须添加 -Encoding UTF8，除非有特殊编码要求
传递: 自动检测并使用文件原编码
```

---

## 语法约束

```yaml
文件操作: 默认添加 -Force 避免目标冲突
环境变量: 使用 $env:VAR 格式，禁止 $VAR
命令行参数: 禁止 -NoProfile（必须加载用户 Profile，确保 UTF-8 编码）
重定向: 禁止 << 和 <()，用 Here-String @'...'@ 传递多行文本
Here-String: 结束标记 '@ 或 "@ 须独占一行且在行首
cmdlet参数: 复合参数（如 -Context）须显式指定 -Path，禁止纯管道输入
变量引用: $ 后须为合法变量名，使用 ${var} 形式避免歧义
路径参数: 文件名和路径须用双引号包裹，如 "file.txt"、"$filePath"，避免 null 错误和空格问题
转义序列: 字面 $ 用反引号，如 "Price: `$100"
引号嵌套: 双引号内双引号须转义 ""，或改用单引号包裹
转义字符: `n(换行) `t(制表符) `$(字面$)
参数组合: 多参数组合前须验证兼容性，遇互斥错误时按提示调整
命令连接: PS5.1 禁止 && 和 ||，用分号或 if ($?) 判断
比较运算: 禁止 > < 用于比较（会被解析为重定向），须用 -gt -lt -eq -ne
空值比较: $null 须置于比较左侧，如 $null -eq $var
```
