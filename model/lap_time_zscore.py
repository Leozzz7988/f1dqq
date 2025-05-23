import json
import os
from pathlib import Path
import numpy as np
from typing import Dict, Any

def calculate_relative_delta(data: Dict[str, Any], year: int) -> Dict[str, Any]:
    """
    Calculate season baseline normalization (Relative Delta) | 计算赛季基准归一化（Relative Delta）
    For each lap, calculate the relative difference from the fastest lap time of the year | 对于每圈，计算与当年最快圈时间的相对差距
    """
    normalized_data = {}
    
    if year < 1995:
        # 1995年之前的总时间数据 | Total time data before 1995
        valid_times = [v['total_time_raw'] for v in data.values() if v['total_time_raw'] > 0]
        if not valid_times:
            return {}
            
        min_time = min(valid_times)
        for driver, result in data.items():
            if result['total_time_raw'] > 0:
                delta = (result['total_time_raw'] - min_time) / min_time
                normalized_data[driver] = {'relative_delta': float(delta)}
    else:
        # 1996年之后的单圈时间数据 | Lap time data after 1996
        all_laps = set()
        for driver_data in data.values():
            all_laps.update(driver_data.keys())
            
        for lap in all_laps:
            lap_times = []
            for driver_data in data.values():
                if lap in driver_data and isinstance(driver_data[lap], dict):
                    time = driver_data[lap].get('time')
                    if time and time > 0:
                        lap_times.append(time)
            
            if lap_times:
                min_time = min(lap_times)
                for driver, driver_data in data.items():
                    if lap in driver_data and isinstance(driver_data[lap], dict):
                        time = driver_data[lap].get('time')
                        if time and time > 0:
                            if driver not in normalized_data:
                                normalized_data[driver] = {}
                            delta = (time - min_time) / min_time
                            normalized_data[driver][lap] = {'relative_delta': float(delta)}
    
    return normalized_data

def standardize_lap_data(data: Dict[str, Any], year: int) -> Dict[str, Any]:
    """
    Standardize lap data processing | 对每圈数据进行标准化处理
    1. First perform season baseline normalization | 先进行赛季基准归一化
    2. Then perform Z-score standardization within laps | 再进行圈内Z-score标准化
    3. Sort lap numbers for each driver | 对每个车手的圈数进行排序
    """
    # 第一步：赛季基准归一化 | Step 1: Season baseline normalization
    normalized_data = calculate_relative_delta(data, year)
    if not normalized_data:
        return {}
    
    # 第二步：圈内Z-score标准化 | Step 2: Z-score standardization within laps
    if year < 1995:
        # 处理1995年之前的总时间数据 | Process total time data before 1995
        deltas = [v['relative_delta'] for v in normalized_data.values()]
        mean_delta = np.mean(deltas)
        std_delta = np.std(deltas)
        
        standardized_data = {}
        for driver, result in normalized_data.items():
            z_score = (result['relative_delta'] - mean_delta) / std_delta
            standardized_data[driver] = {
                'relative_delta': float(result['relative_delta']),
                'z_score': float(z_score)
            }
    else:
        # 处理1996年之后的单圈时间数据 | Process lap time data after 1996
        standardized_data = {}
        all_laps = set()
        for driver_data in normalized_data.values():
            all_laps.update(driver_data.keys())
        
        for lap in all_laps:
            lap_deltas = []
            for driver_data in normalized_data.values():
                if lap in driver_data:
                    delta = driver_data[lap]['relative_delta']
                    lap_deltas.append(delta)
            
            if lap_deltas:
                mean_delta = np.mean(lap_deltas)
                std_delta = np.std(lap_deltas)
                
                for driver, driver_data in normalized_data.items():
                    if lap in driver_data:
                        if driver not in standardized_data:
                            standardized_data[driver] = {}
                        delta = driver_data[lap]['relative_delta']
                        z_score = (delta - mean_delta) / std_delta
                        standardized_data[driver][lap] = {
                            'relative_delta': float(delta),
                            'z_score': float(z_score)
                        }
    
    # 第三步：对每个车手的圈数进行排序 | Step 3: Sort lap numbers for each driver
    sorted_data = {}
    for driver, driver_data in standardized_data.items():
        if year < 1995:
            sorted_data[driver] = driver_data
        else:
            # 将圈数转换为整数并排序 | Convert lap numbers to integers and sort
            sorted_laps = sorted(driver_data.keys(), key=lambda x: int(x))
            sorted_data[driver] = {lap: driver_data[lap] for lap in sorted_laps}
    
    return sorted_data

def process_all_files():
    """
    Process all data files | 处理所有数据文件
    """
    # 修改路径定位方式 | Modify path locating method
    base_path = Path(__file__).parent.parent  # 向上一级到项目根目录 | Go up one level to project root directory
    input_dir = base_path / 'data' / 'lap_time_raw'
    output_dir = base_path / 'data' / 'lap_time_zscore'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for file in input_dir.glob('*_Italian_Grand_Prix_*results.json'):
        try:
            year = int(file.name.split('_')[0])
            
            # 读取原始数据，确保使用 UTF-8 编码 | Read raw data, ensure using UTF-8 encoding
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 标准化处理 | Standardization processing
            standardized_data = standardize_lap_data(data, year)
            
            # 保存处理后的数据，确保使用 UTF-8 编码 | Save processed data, ensure using UTF-8 encoding
            output_file = output_dir / f'{year}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(standardized_data, f, indent=4, ensure_ascii=False)
                
            print(f"Successfully processed data for year {year} | 成功处理 {year} 年的数据")
            
        except Exception as e:
            print(f"处理文件 {file.name} 时出错: {e} | Error processing file {file.name}: {e}")

if __name__ == "__main__":
    process_all_files()