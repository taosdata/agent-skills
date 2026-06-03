import pandas as pd
import numpy as np

def align_and_resample_features(data_dict, time_col='ts', freq='1min', fill_method='linear'):
    """
    将多个采集频率不一致的特征列按照时间戳对齐，并进行缺失值处理与重采样。
    
    参数:
    ----------
    data_dict : dict
        输入字典数据，如 {"ts": [...], "feature_a": [...], "feature_b": [...]}
        各个特征数组的长度需一致，非采集时刻可用 None 或 np.nan 填充。
    time_col : str
        时间戳列的名称，默认是 'ts'
    freq : str
        目标重采样频率，如 '1min' (一分钟), '5s' (五秒) 等
    fill_method : str
        缺失值插值对齐策略：
        - 'linear': 线性插值
        - 'time': 时间加权插值
        - 'ffill': 前向填充
    
    返回:
    -------
    pd.DataFrame
        对齐后的多变量特征 DataFrame
    """
    # 1. 转换为 DataFrame
    df = pd.DataFrame(data_dict)
    
    # 2. 转换时间列为 DatetimeIndex
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col], unit='ms')
    df = df.set_index(time_col)
    
    # 3. 对数据进行均值重采样（在窗口内如果有多个数据点则取平均）
    resampled = df.resample(freq).mean()
    
    # 4. 特征对齐与插值缺失值处理
    if fill_method in ['linear', 'time']:
        aligned_df = resampled.interpolate(method=fill_method)
    else:
        aligned_df = resampled
        
    # 双保险填充：对插值可能无法覆盖的首尾缺失数据执行前向与后向填充
    aligned_df = aligned_df.ffill().bfill()
    
    return aligned_df

if __name__ == "__main__":
    # 测试样例数据
    test_data = {
        "ts": [1710000000000, 1710000030000, 1710000060000, 1710000090000],
        "temperature": [23.4, np.nan, 23.8, 24.1],
        "pressure": [101.3, 101.4, np.nan, 101.5]
    }
    
    aligned_res = align_and_resample_features(test_data, freq='30s')
    print("=== 对齐后特征结果 ===")
    print(aligned_res)
