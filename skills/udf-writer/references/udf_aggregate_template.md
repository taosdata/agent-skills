# TDengine C UDF 聚合函数模板与数据结构

本文档提供了用 C 语言开发 TDengine 聚合函数（User Defined Aggregate Function, UDAF）的模板，以及相关的核心数据结构。

## 聚合函数模板

聚合函数用于对数据进行分组和计算，从而生成汇总信息（多行输入，单行输出）。它的工作流程如下：

1. **初始化结果缓冲区**：首先调用 `aggfn_start`，生成一个用于存储中间结果的缓冲区（result buffer）。
2. **更新中间结果**：对于每个数据块，调用 `aggfn` 根据输入数据更新中间结果。
3. **生成最终结果**：在所有数据块的中间结果更新完成后，调用 `aggfn_finish` 从中间结果产生最终结果。

```c
#include "taos.h"
#include "taoserror.h"
#include "taosudf.h"

// 初始化函数（可选）
// 如果不需要初始化，可以省略此定义。
// 初始化函数名必须是 UDF 名称与 _init 后缀的连接。
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t aggfn_init() {
    // 初始化逻辑
    return TSDB_CODE_SUCCESS;
}

// 聚合启动函数
// 在此函数中初始化中间结果值或状态（interBuf）。
// 函数名必须是 UDF 名称与 _start 后缀的连接。
// @param interBuf: 待初始化的中间值缓冲区
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t aggfn_start(SUdfInterBuf* interBuf) {
    // 在 interBuf 中初始化中间结果
    return TSDB_CODE_SUCCESS;
}

// 聚合计算/减少函数
// 该函数将旧状态（interBuf）与一个数据块（inputBlock）进行聚合，并输出新状态（newInterBuf）。
// @param inputBlock: 输入数据块
// @param interBuf: 旧状态缓冲区
// @param newInterBuf: 新状态缓冲区
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t aggfn(SUdfDataBlock* inputBlock, SUdfInterBuf *interBuf, SUdfInterBuf *newInterBuf) {
    // 从 inputBlock 和 interBuf 读取数据，并输出到 newInterBuf
    return TSDB_CODE_SUCCESS;
}

// 聚合结束函数
// 该函数将中间值（interBuf）转换为最终输出结果（result）。
// 函数名必须是 UDF 名称与 _finish 后缀的连接。
// @param interBuf: 中间值缓冲区
// @param result: 最终输出结果
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t aggfn_finish(SUdfInterBuf* interBuf, SUdfInterBuf *result) {
    // 从 interBuf 读取数据并处理，然后输出到 result
    return TSDB_CODE_SUCCESS;
}

// 清理函数（可选）
// 如果没有清理相关的处理，可以省略此定义。
// 销毁函数名必须是 UDF 名称与 _destroy 后缀的连接。
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t aggfn_destroy() {
    // 清理逻辑
    return TSDB_CODE_SUCCESS;
}
```

---

## C UDF 聚合函数相关数据结构

编写 C 聚合函数时，核心的数据结构定义如下：

```c
typedef struct SUdfColumnMeta {
  int16_t type;
  int32_t bytes;
  uint8_t precision;
  uint8_t scale;
} SUdfColumnMeta;

typedef struct SUdfColumnData {
  int32_t numOfRows;
  int32_t rowsAlloc;
  union {
    struct {
      int32_t nullBitmapLen;
      char   *nullBitmap;
      int32_t dataLen;
      char   *data;
    } fixLenCol;

    struct {
      int32_t  varOffsetsLen;
      int32_t *varOffsets;
      int32_t  payloadLen;
      char    *payload;
      int32_t  payloadAllocLen;
    } varLenCol;
  };
} SUdfColumnData;

typedef struct SUdfColumn {
  SUdfColumnMeta colMeta;
  bool           hasNull;
  SUdfColumnData colData;
} SUdfColumn;

typedef struct SUdfDataBlock {
  int32_t numOfRows;
  int32_t numOfCols;
  SUdfColumn **udfCols;
} SUdfDataBlock;

typedef struct SUdfInterBuf {
  int32_t bufLen;
  char   *buf;
  int8_t  numOfResult; // 结果行数，为 0 或 1
} SUdfInterBuf;
```

### 数据结构说明

- **SUdfDataBlock**：包含行数 `numOfRows` 和列数 `numOfCols`。`udfCols[i]` (0 <= i <= numOfCols-1) 表示每一列数据，类型为 `SUdfColumn*`。
- **SUdfColumn**：包含列的数据类型定义 `colMeta` 和列的数据 `colData`，以及是否有空值 `hasNull`。
- **SUdfColumnMeta**：定义了列的数据类型（对应 `taos.h` 的类型定义）、字节长度、精度和小数位数。
- **SUdfColumnData**：数据可以是变长或定长。定长数据存放在 `fixLenCol` 中，变长数据（如 `VARCHAR`）存放在 `varLenCol` 中。
- **SUdfInterBuf**：定义了中间结构缓冲区，包含缓冲区长度 `bufLen`，指向实际数据的指针 `buf`，以及结果行数 `numOfResult`。
