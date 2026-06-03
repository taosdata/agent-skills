import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from taosanalytics.service import AbstractForecastService

# 1. 定义标准的 PyTorch LSTM 预测网络
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # 输入形状 x: (batch_size, sequence_length, input_size)
        out, _ = self.lstm(x)
        # 取最后一个时刻的输出进行预测
        out = self.fc(out[:, -1, :])
        return out

# 2. 编写符合 TDgpt anode 加载约定的 Service 类
# 类名必须以 "_" 开始，以 "Service" 结束，且从 AbstractForecastService 继承
class _LstmForecastService(AbstractForecastService):
    name = 'lstm_fc'  # 在 SQL 中调用的算法简称，必须全小写
    desc = "Time-series forecasting model based on PyTorch LSTM"

    def __init__(self):
        super().__init__()
        self.model = None
        self.lookback_window = 60  # 默认的历史回顾滑动窗口大小
        
        # 归一化缩放参数，生产环境下可通过 set_params 加载自 .info 文件
        self.mean = 0.0
        self.std = 1.0

    def execute(self):
        """
        核心预测执行方法
        基类调用此方法前，已将待预测的历史序列数据设置在 self.list 中。
        """
        # 安全验证：如果输入为空或数据太短，防止计算崩溃
        if self.input_is_empty() or len(self.list) < self.lookback_window:
            raise ValueError(f"Input sequence length ({len(self.list)}) is less than lookback window ({self.lookback_window})")

        # 对输入序列提取最近的 lookback_window 个点，并转为 numpy
        input_seq = np.array(self.list[-self.lookback_window:], dtype=np.float32)
        
        # 归一化处理
        input_seq_normalized = (input_seq - self.mean) / self.std
        
        # 调整形状为 PyTorch LSTM 期待的三维张量: (batch_size=1, seq_len, input_size=1)
        x_tensor = torch.tensor(input_seq_normalized).unsqueeze(0).unsqueeze(-1)

        # 执行模型推理
        if self.model is None:
            raise RuntimeError("Model is not initialized. Please load the model weights first.")
        
        self.model.eval()
        with torch.no_grad():
            pred_tensor = self.model(x_tensor)  # 预测输出 shape: (1, output_size)
            pred_val = pred_tensor.item()
            
        # 反归一化得到真实预测物理值
        pred_val_real = pred_val * self.std + self.mean

        # 构建输出返回格式
        # 预测值的数量取决于用户参数 self.rows
        # 本模板演示单步预测后自回归扩展 self.rows 个预测点，或直接重复映射
        pred_list = [pred_val_real] * self.rows
        
        # 生成对应的预测结果时间轴（使用基类的 start_ts 与 time_step）
        ts_list = [self.start_ts + i * self.time_step for i in range(self.rows)]

        res = []
        res.append(ts_list)        # 第1个元素：时间戳数组
        res.append(pred_list)      # 第2个元素：预测结果数组
        
        if self.return_conf:
            # 如果要求返回置信区间上下界，在此填充。无区间模型可直接填充预测值本身
            res.append(pred_list)  # 第3个元素：置信区间下界
            res.append(pred_list)  # 第4个元素：置信区间上界

        # 返回符合 TDgpt 约定的字典
        return {
            "mse": 0.0,            # 本次预测的拟合最小均方误差 (Float)
            "res": res             # 结果数组结构
        }

    def set_params(self, params):
        """
        加载模型参数与执行参数的方法，由 anode 执行器自动调用。
        """
        # 1. 优先调用父类方法解析标准时序参数（如 fc_rows, start_ts, time_step）
        super().set_params(params)

        # 2. 从参数中提取滑动窗口与模型配置信息
        if "lookback" in params:
            self.lookback_window = int(params["lookback"])

        # 3. 动态加载模型权重
        if "model_name" in params:
            model_name = params["model_name"]
            
            # 从默认路径获取模型文件存放位置
            # 可结合 anode 的 conf 模块获取绝对路径，例如:
            # from taosanalytics.core import conf
            # model_dir = os.path.join(conf.get_model_directory(), model_name)
            model_file_path = f"/usr/local/taos/taosanode/model/{model_name}/{model_name}.pth"
            info_file_path = f"/usr/local/taos/taosanode/model/{model_name}/{model_name}.info"
            
            if os.path.exists(model_file_path):
                # 初始化网络结构
                self.model = LSTMModel(input_size=1, hidden_size=64, num_layers=2, output_size=1)
                self.model.load_state_dict(torch.load(model_file_path, map_location=torch.device('cpu')))
            else:
                raise FileNotFoundError(f"Model file not found at: {model_file_path}")
                
            # 加载特征归一化标准差/均值参数
            if os.path.exists(info_file_path):
                import joblib
                info = joblib.load(info_file_path)
                self.mean = info.get("mean", 0.0)
                self.std = info.get("std", 1.0)
                
        return True
