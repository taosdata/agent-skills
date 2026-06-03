# TDengine UDF 编写辅助 (udf-writer)

协助开发与调试 TDengine 用户自定义函数（UDF），生成符合规范的 C/C++ 或 Python UDF 代码，并指导加载与部署。

## 概述

本技能为开发 TDengine UDF（User Defined Function）的用户或 Agent 提供辅助指引。由于 UDF 运行在 TDengine 服务端进程中，对内存安全、空值校验、执行性能有着极高要求。本技能可根据用户的功能要求和目标语言（C/C++ 或 Python），自动生成合规、健壮的 UDF 框架代码，并提供对应的动态库编译指令（C 语言）以及在 TDengine 中注册加载函数的 `CREATE FUNCTION` SQL 命令与测试样例，显著降低 UDF 的编写门槛。

## 触发场景

- 用户需要编写 TDengine 的用户自定义函数时
- 用户提到“写一个 UDF”、“编写自定义函数”、“TDengine UDF 编写”
- 想要了解如何在 TDengine 中创建标量函数（Scalar Function）或聚合函数（UDAF）

## 核心功能

1. **自动生成模板代码**：生成包含头文件引用（如 `#include <taosudf.h>`）、包含输入输出类型定义的标准函数框架。
2. **严谨的安全防护**：代码逻辑中默认包含空值/空指针校验（Null Value / Null Indicator），并在 C/C++ UDF 中强调内存安全（防止内存泄漏与越界）。
3. **闭环的编译与部署指引**：不仅生成代码，还提供如何将其编译成 `.so` 共享库，以及在 TDengine 命令行中如何使用 SQL 语句将 UDF 注册生效的步骤。

## 作者

- Author: limingjun
- Team: 售前
- Version: 0.1.0
