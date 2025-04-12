import json
import requests
import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional, Union
from time import sleep

# 设置缓存目录
PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = os.path.join(PROJECT_ROOT, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def get_ergast_data(endpoint: str, offset: int = 0) -> Dict:
    """从 Ergast API 获取数据"""
    base_url = 'http://ergast.com/api/f1'
    # 使用 offset 和 limit 参数进行分页
    response = requests.get(f'{base_url}/{endpoint}.json?limit=1000&offset={offset}')
    if response.status_code == 200:
        return response.json()
    return {}

def get_all_laps_data(season: int, round: str) -> List:
    """获取一场比赛的所有圈速数据"""
    all_laps = []
    offset = 0
    limit = 100  # 每次获取100圈数据
    
    while True:
        url = f'http://ergast.com/api/f1/{season}/{round}/laps.json?limit={limit}&offset={offset}'
        response = requests.get(url)
        if response.status_code != 200:
            break
            
        data = response.json()
        if not ('MRData' in data and 
                'RaceTable' in data['MRData'] and 
                'Races' in data['MRData']['RaceTable'] and 
                data['MRData']['RaceTable']['Races']):
            break
            
        laps_data = data['MRData']['RaceTable']['Races'][0].get('Laps', [])
        if not laps_data:
            break
            
        all_laps.extend(laps_data)
        
        # 检查是否还有更多数据
        total = int(data['MRData'].get('total', '0'))
        if offset + limit >= total:
            break
            
        offset += limit
        sleep(0.1)  # 避免请求过快
        
    return all_laps

def convert_time_to_seconds(time_str: str) -> float:
    """将时间字符串转换为秒数"""
    if not time_str:
        return 0.0
        
    # 处理 "1:23.456" 格式
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    # 处理 "23.456" 格式
    return float(time_str)

def load_f1_data(
        drivers: Union[str, List[str]],
        seasons: Union[int, List[int]],
        circuits: Optional[List[str]] = None,
) -> Dict:
    """
    从 Ergast API 加载F1数据

    Args:
        drivers: 车手名字（如 'Senna' 或 'Hamilton'）
        seasons: 赛季或赛季列表
        circuits: 赛道名称列表，默认为所有赛道

    Returns:
        包含筛选后数据的字典
    """
    drivers = [drivers] if isinstance(drivers, str) else drivers
    seasons = [seasons] if isinstance(seasons, int) else seasons
    circuits = circuits if circuits else []

    sessions_data = {}

    for season in seasons:
        try:
            schedule_data = get_ergast_data(f'{season}')
            if 'MRData' not in schedule_data or 'RaceTable' not in schedule_data['MRData']:
                print(f"警告: {season} 赛季数据结构不完整")
                continue
                
            races = schedule_data['MRData']['RaceTable'].get('Races', [])
            if not races:
                print(f"警告: {season} 赛季没有比赛数据")
                continue

            for race in races:
                circuit_name = race['raceName']
                if circuits and circuit_name not in circuits:
                    continue

                race_data = {}

                # 首先获取比赛结果以获取车手信息
                race_results = get_ergast_data(f'{season}/{race["round"]}/results')
                if not ('MRData' in race_results and 
                       'RaceTable' in race_results['MRData'] and 
                       'Races' in race_results['MRData']['RaceTable'] and 
                       race_results['MRData']['RaceTable']['Races']):
                    continue
                
                results = race_results['MRData']['RaceTable']['Races'][0]['Results']
                driver_info_map = {r['Driver']['driverId']: r['Driver'] for r in results if 'Driver' in r}

                # 获取圈速数据
                print(f"正在获取 {season} 赛季 {circuit_name} 的圈速数据...")
                laps_data = get_all_laps_data(season, race["round"])
                total_laps = len(laps_data)
                print(f"共获取到 {total_laps} 圈数据")
                
                if total_laps == 0:
                    print(f"警告: 未能获取到 {season} 赛季 {circuit_name} 的圈速数据")
                    continue
                
                for lap in laps_data:
                    lap_number = lap.get('number', '0')
                    timings = lap.get('Timings', [])
                    
                    for timing in timings:
                        driver_id = timing.get('driverId', '')
                        if driver_id in driver_info_map:
                            driver_info = driver_info_map[driver_id]
                            driver_name = f"{driver_info.get('givenName', '')} {driver_info.get('familyName', '')}"
                            
                            if not drivers or any(d.lower() in driver_name.lower() for d in drivers):
                                if driver_name not in race_data:
                                    race_data[driver_name] = {}
                                
                                # 将圈速时间转换为秒
                                lap_time = timing.get('time', '')
                                seconds = convert_time_to_seconds(lap_time)
                                race_data[driver_name][lap_number] = {
                                    'time': seconds
                                }

                if race_data:
                    sessions_data[(season, circuit_name)] = race_data
                sleep(0.1)

        except Exception as e:
            print(f"加载赛季数据出错 - 赛季: {season}, 错误: {str(e)}")
            continue

    return sessions_data  # 修正这里的缩进，和 for 循环对齐

def save_driver_data(
        drivers: Optional[str],
        seasons: Union[int, List[int]],
        circuits: Optional[List[str]] = None
) -> None:
    """保存F1数据到JSON文件"""
    seasons = [seasons] if isinstance(seasons, int) else seasons
    circuits = [circuits] if isinstance(circuits, str) else circuits if circuits else None

    base_path = Path(__file__).parent
    output_dir = base_path / 'rawdata_1'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取数据
    data = load_f1_data(
        drivers=drivers.split(',') if drivers else [],
        seasons=seasons,
        circuits=circuits
    )

    # 保存数据
    for (season, circuit), session_data in data.items():
        output_file = output_dir / f"{season}_{circuit.replace(' ', '_')}_Lapstime_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    save_driver_data(
        drivers='',
        seasons=list(range(1996, 2025)),
        #seasons=[2010],
        circuits=['Italian Grand Prix']
        
        
    )