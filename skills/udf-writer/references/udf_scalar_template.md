# TDengine C UDF 标量函数模板与数据结构

本文档提供了用 C 语言开发 TDengine 标量函数（Scalar Function）的模板，以及相关的核心数据结构。

## 标量函数模板

标量函数是一种将输入数据转换为输出数据的函数，通常用于对单个数据值进行计算和转换（单行输入，单行输出）。

```c
#include "taos.h"
#include "taoserror.h"
#include "taosudf.h"

// 初始化函数（可选）
// 如果不需要初始化，可以省略此定义。
// 初始化函数名必须是 UDF 名称与 _init 后缀的连接。
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t scalarfn_init() {
    // 初始化逻辑
    return TSDB_CODE_SUCCESS;
}

// 标量函数主计算函数
// @param inputDataBlock: 输入数据块，由多列组成，每列由 SUdfColumn 定义
// @param resultColumn: 输出列
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t scalarfn(SUdfDataBlock* inputDataBlock, SUdfColumn* resultColumn) {
    // 从 inputDataBlock 读取数据并处理，然后输出到 resultColumn
    return TSDB_CODE_SUCCESS;
}

// 清理函数（可选）
// 如果没有清理相关的处理，可以省略此定义。
// 销毁函数名必须是 UDF 名称与 _destroy 后缀的连接。
// @return 返回值需为 taoserror.h 中定义的错误码
int32_t scalarfn_destroy() {
    // 清理逻辑
    return TSDB_CODE_SUCCESS;
}
```

---

## C UDF 标量函数相关数据结构

编写 C 标量函数时，核心的数据结构定义如下：

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
```

### 数据结构说明

- **SUdfDataBlock**：包含行数 `numOfRows` 和列数 `numOfCols`。`udfCols[i]` (0 <= i <= numOfCols-1) 表示每一列数据，类型为 `SUdfColumn*`。
- **SUdfColumn**：包含列的数据类型定义 `colMeta` 和列的数据 `colData`，以及是否有空值 `hasNull`。
- **SUdfColumnMeta**：定义了列的数据类型（对应 `taos.h` 的类型定义）、字节长度、精度和小数位数。
- **SUdfColumnData**：数据可以是变长或定长。定长数据存放在 `fixLenCol` 中，变长数据（如 `VARCHAR`）存放在 `varLenCol` 中。
