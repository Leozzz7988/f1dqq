import json
import os
import numpy as np
from pathlib import Path

def calculate_time_gap_and_zscore(data_dir: str = "data/total_time_raw"):
    """
    计算每年比赛中各选手与最快完赛时间的时差，并进行z-score标准化
    
    Args:
        data_dir: total_time数据文件夹路径
    """
    # 获取数据目录的绝对路径
    base_path = Path(__file__).parent.parent
    data_path = base_path / data_dir
    
    # 遍历所有年份的数据文件
    for file in data_path.glob("*_Italian_Grand_Prix_TotalTime_results.json"):
        try:
            # 读取JSON文件
            with open(file, 'r', encoding='utf-8') as f:
                race_data = json.load(f)
            
            # 找出该年度最快完赛时间
            fastest_time = float('inf')
            for driver_data in race_data.values():
                time = driver_data.get('total_time_raw', 0)
                if time > 0 and time < fastest_time:  # 排除未完赛（时间为0）的情况
                    fastest_time = time
            
            # 计算每个车手的完赛时差
            time_gaps = []
            for driver, data in race_data.items():
                if data['total_time_raw'] > 0:  # 只处理完赛的车手
                    time_gap = data['total_time_raw'] - fastest_time
                    time_gaps.append(time_gap)
                    race_data[driver]['total_time_gap'] = time_gap
            
            # 计算z-score
            if time_gaps:
                mean_gap = np.mean(time_gaps)
                std_gap = np.std(time_gaps)
                
                for driver, data in race_data.items():
                    if data['total_time_raw'] > 0:
                        z_score = (data['total_time_gap'] - mean_gap) / std_gap
                        race_data[driver]['z_score'] = float(z_score)
                    else:
                        race_data[driver]['total_time_gap'] = 0.0
                        race_data[driver]['z_score'] = 0.0
            
            # 保存处理后的数据
            output_file = file.parent / file.name.replace('TotalTime', 'TimeGap')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(race_data, f, indent=4, ensure_ascii=False)
            
            print(f"成功处理 {file.name}")
            
        except Exception as e:
            print(f"处理文件 {file.name} 时出错: {e}")

if __name__ == "__main__":
    calculate_time_gap_and_zscore()