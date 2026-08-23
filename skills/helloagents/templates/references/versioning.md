# 版本号解析规则

## A3 | 版本号解析规则

### 多语言版本号来源（优先级: 主 > 次）

| 语言/框架 | 主来源 | 次来源 |
|----------|--------|--------|
| JavaScript/TypeScript | package.json → version | index.js/ts → VERSION常量 |
| Python | pyproject.toml → [project].version | setup.py/__init__.py → __version__ |
| Java(Maven) | pom.xml → \<version\> | - |
| Java(Gradle) | gradle.properties/build.gradle → version | - |
| Go | Git标签(tag) | - |
| Rust | Cargo.toml → [package].version | - |
| .NET | .csproj → \<Version\>/\<AssemblyVersion\> | - |
| C/C++ | CMakeLists.txt → project(...VERSION) | 头文件 → #define PROJECT_VERSION |

**用途:** 供 G7 版本管理规则引用，确定各语言项目的版本号文件位置。
