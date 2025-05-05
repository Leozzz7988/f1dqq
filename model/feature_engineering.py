import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from scipy import stats

def calculate_driver_statistics(driver_data: Dict[str, Any]) -> Dict[str, Any]:
    """计算单个车手的统计特征"""
    all_z_scores = []
    all_deltas = []
    
    # 收集所有年份的数据
    for year_data in driver_data.values():
        if isinstance(year_data, dict):
            # 处理按圈数据
            if any(isinstance(v, dict) and ('z_score' in v or 'relative_delta' in v) 
                  for v in year_data.values()):
                for lap_data in year_data.values():
                    if isinstance(lap_data, dict):
                        if 'z_score' in lap_data:
                            all_z_scores.append(lap_data['z_score'])
                        if 'relative_delta' in lap_data:
                            all_deltas.append(lap_data['relative_delta'])
            # 处理总时间数据
            elif 'total_time_raw' in year_data and 'z_score' in year_data['total_time_raw']:
                all_z_scores.append(year_data['total_time_raw']['z_score'])

    if not all_z_scores and not all_deltas:
        return {}

    stats_dict = {}
    
    # 1. 计算平均值
    if all_z_scores:
        stats_dict['mean_z_score'] = np.mean(all_z_scores)
    if all_deltas:
        stats_dict['mean_delta'] = np.mean(all_deltas)
    
    # 2. 计算方差
    if all_z_scores:
        stats_dict['var_z_score'] = np.var(all_z_scores)
    if all_deltas:
        stats_dict['var_delta'] = np.var(all_deltas)
    
    # 3. 最佳值与最差值
    if all_z_scores:
        stats_dict['best_z_score'] = np.min(all_z_scores)
        stats_dict['worst_z_score'] = np.max(all_z_scores)
        stats_dict['z_score_range'] = stats_dict['worst_z_score'] - stats_dict['best_z_score']
    if all_deltas:
        stats_dict['best_delta'] = np.min(all_deltas)
        stats_dict['worst_delta'] = np.max(all_deltas)
        stats_dict['delta_range'] = stats_dict['worst_delta'] - stats_dict['best_delta']
    
    # 4. 计算中位数
    if all_z_scores:
        stats_dict['median_z_score'] = np.median(all_z_scores)
    if all_deltas:
        stats_dict['median_delta'] = np.median(all_deltas)
    
    # 5. 计算衰减斜率（使用简单线性回归）
    if len(all_z_scores) > 1:
        x = np.arange(len(all_z_scores))
        slope, _, _, _, _ = stats.linregress(x, all_z_scores)
        stats_dict['z_score_decay_rate'] = slope
    if len(all_deltas) > 1:
        x = np.arange(len(all_deltas))
        slope, _, _, _, _ = stats.linregress(x, all_deltas)
        stats_dict['delta_decay_rate'] = slope
    
    # 6. 异常检测（使用3个标准差作为阈值）
    if all_z_scores:
        z_mean = np.mean(all_z_scores)
        z_std = np.std(all_z_scores)
        outliers = [z for z in all_z_scores if abs(z - z_mean) > 3 * z_std]
        stats_dict['outlier_count'] = len(outliers)
        stats_dict['outlier_ratio'] = len(outliers) / len(all_z_scores) if all_z_scores else 0
    
    return stats_dict

def process_legendary_drivers():
    """处理所有传奇车手的数据并生成统计特征"""
    base_path = Path(__file__).parent.parent / 'data'
    input_file = base_path / 'legendary_drivers_data.json'
    output_file = base_path / 'legendary_drivers_statistics.json'
    driver_years_file = base_path / 'driver_years.json'
    
    # 定义车手名称映射字典
    driver_names_reverse = {
        "Ayrton Senna": "Senna",
        "Damon Hill": "Hill",
        "Michael Schumacher": "Schumacher",
        "Jacques Villeneuve": "Villeneuve",
        "Mika Häkkinen": "Hakkinen",
        "David Coulthard": "Coulthard",
        "Nico Rosberg": "Rosberg",
        "Fernando Alonso": "Alonso",
        "Kimi Räikkönen": "Raikkonen",
        "Lewis Hamilton": "Hamilton",
        "Sebastian Vettel": "Vettel",
        "Max Verstappen": "Verstappen"
    }
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            legendary_data = json.load(f)
        with open(driver_years_file, 'r', encoding='utf-8') as f:
            driver_years = json.load(f)
    except Exception as e:
        print(f"读取数据文件时出错：{e}")
        return
    
    # 计算每个车手的统计特征
    statistics = {}
    for driver_key, driver_data in legendary_data.items():
        # 计算基本统计特征
        driver_stats = calculate_driver_statistics(driver_data)
        if not driver_stats:
            continue
            
        # 获取车手简称
        driver_key_short = driver_names_reverse.get(driver_key)
        
        # 计算完赛率
        if driver_key_short and driver_key_short in driver_years:
            years_data = driver_years[driver_key_short]
            participated_count = len(years_data.get('participated', []))
            finished_count = len(years_data.get('finished', []))
            if participated_count > 0:
                driver_stats['finish_rate'] = finished_count / participated_count
            else:
                driver_stats['finish_rate'] = 0.0
        
        statistics[driver_key] = driver_stats
    
    # 收集所有非Senna车手的outlier特征值
    outlier_counts = []
    outlier_ratios = []
    for driver_name, stats in statistics.items():
        if driver_name != "Ayrton Senna" and "outlier_count" in stats:
            outlier_counts.append(stats["outlier_count"])
            outlier_ratios.append(stats["outlier_ratio"])
    
    # 计算中位数并填充Senna的缺失值
    if outlier_counts and outlier_ratios:
        median_outlier_count = float(np.median(outlier_counts))
        median_outlier_ratio = float(np.median(outlier_ratios))
        
        if "Ayrton Senna" in statistics:
            statistics["Ayrton Senna"]["outlier_count"] = median_outlier_count
            statistics["Ayrton Senna"]["outlier_ratio"] = median_outlier_ratio
    
    # 保存结果
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=4, ensure_ascii=False)
        print(f"统计特征已保存到 {output_file}")
    except Exception as e:
        print(f"保存统计特征时出错：{e}")

def process_all_drivers():
    """处理所有参赛车手的数据并生成统计特征"""
    base_path = Path(__file__).parent.parent
    input_dir = base_path / 'data' / 'lap_time_zscore'
    output_dir = base_path / 'data' / 'lap_time_zscore_feature'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 遍历每个年份的数据文件
    for file in input_dir.glob('*.json'):
        try:
            year = int(file.stem)
            
            # 读取该年度的数据
            with open(file, 'r', encoding='utf-8') as f:
                year_data = json.load(f)
            
            # 为每个车手计算统计特征
            year_statistics = {}
            for driver_name, driver_data in year_data.items():
                # 检查是否完成了53圈
                if isinstance(driver_data, dict) and len(driver_data) >= 53:
                    # 检查是否所有圈数都有有效的z-score数据
                    valid_laps = [
                        lap_data for lap_data in driver_data.values()
                        if isinstance(lap_data, dict) and 
                        'z_score' in lap_data and 
                        lap_data['z_score'] is not None
                    ]
                    
                    if len(valid_laps) >= 53:  # 确保有53圈有效数据
                        # 将单年数据转换为与原函数兼容的格式
                        driver_yearly_data = {str(year): driver_data}
                        
                        # 计算统计特征
                        driver_stats = calculate_driver_statistics(driver_yearly_data)
                        if driver_stats:
                            year_statistics[driver_name] = driver_stats
            
            # 保存该年度的统计结果
            if year_statistics:  # 只在有数据时保存
                output_file = output_dir / f'{year}.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(year_statistics, f, indent=4, ensure_ascii=False)
                print(f"成功处理 {year} 年的数据，共 {len(year_statistics)} 位完赛车手")
            else:
                print(f"警告：{year} 年没有有效的完赛数据")
            
        except Exception as e:
            print(f"处理 {file.name} 时出错: {e}")

if __name__ == "__main__":
    process_all_drivers()
    process_legendary_drivers()