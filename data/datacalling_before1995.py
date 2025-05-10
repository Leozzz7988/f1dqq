import json
import requests
import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional, Union
from time import sleep

# Set cache directory | 设置缓存目录
PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = os.path.join(PROJECT_ROOT, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def get_ergast_data(endpoint: str, offset: int = 0) -> Dict:
    """Get data from Ergast API | 从 Ergast API 获取数据"""
    base_url = 'http://ergast.com/api/f1'
    # Use offset and limit parameters for pagination | 使用 offset 和 limit 参数进行分页
    response = requests.get(f'{base_url}/{endpoint}.json?limit=1000&offset={offset}')
    if response.status_code == 200:
        return response.json()
    return {}

def get_all_laps_data(season: int, round: str) -> List:
    """Get all lap time data for a race | 获取一场比赛的所有圈速数据"""
    all_laps = []
    offset = 0
    limit = 100  # Get 100 laps of data each time | 每次获取100圈数据
    
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
        
        # 检查是否还有更多数据 | Check if there is more data
        total = int(data['MRData'].get('total', '0'))
        if offset + limit >= total:
            break
            
        offset += limit
        sleep(0.1)  # 避免请求过快 | Avoid requesting too frequently
        
    return all_laps

def convert_time_to_seconds(time_str: str) -> float:
    """Convert time string to seconds | 将时间字符串转换为秒数"""
    if not time_str or time_str.startswith('+'):
        return 0.0
        
    # Handle "1:20:29.065" format (hours:minutes:seconds.milliseconds) | 处理 "1:20:29.065" 格式（时:分:秒.毫秒）
    parts = time_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    # Handle "1:23.456" format (minutes:seconds.milliseconds) | 处理 "1:23.456" 格式（分:秒.毫秒）
    elif len(parts) == 2:
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    # Handle "23.456" format (seconds.milliseconds) | 处理 "23.456" 格式（秒.毫秒）
    return float(time_str)

def load_f1_data(
        drivers: Union[str, List[str]],
        seasons: Union[int, List[int]],
        circuits: Optional[List[str]] = None,
) -> Dict:
    """
    Load F1 data from Ergast API | 从 Ergast API 加载F1数据

    Args:
        drivers: Driver names (e.g., 'Senna' or 'Hamilton') | 车手名字（如 'Senna' 或 'Hamilton'）
        seasons: Season or list of seasons | 赛季或赛季列表
        circuits: List of circuit names, defaults to all circuits | 赛道名称列表，默认为所有赛道

    Returns:
        Dictionary containing filtered data | 包含筛选后数据的字典
    """
    drivers = [drivers] if isinstance(drivers, str) else drivers
    seasons = [seasons] if isinstance(seasons, int) else seasons
    circuits = circuits if circuits else []

    sessions_data = {}

    for season in seasons:
        try:
            schedule_data = get_ergast_data(f'{season}')
            if 'MRData' not in schedule_data or 'RaceTable' not in schedule_data['MRData']:
                print(f"Warning: {season} season data structure is incomplete | 警告: {season} 赛季数据结构不完整")
                continue
                
            races = schedule_data['MRData']['RaceTable'].get('Races', [])
            if not races:
                print(f"Warning: {season} season has no race data | 警告: {season} 赛季没有比赛数据")
                continue

            for race in races:
                circuit_name = race['raceName']
                if circuits and circuit_name not in circuits:
                    continue

                race_data = {}

                # First get race results to obtain driver information | 首先获取比赛结果以获取车手信息
                race_results = get_ergast_data(f'{season}/{race["round"]}/results')
                
                # Get the finishing time of the race winner | 获取第一名的完赛时间
                winner_time = 0.0
                
                # Only calculate total time when driver finished and has time record | 只有当车手完赛并且有时间记录时才计算总时间
                
                # Only record status for non-finishing drivers | 未完赛车手只记录状态

        except Exception as e:
            print(f"Error loading season data - Season: {season}, Error: {str(e)} | 加载赛季数据出错 - 赛季: {season}, 错误: {str(e)}")
            continue

    return sessions_data

def save_driver_data(
        drivers: Optional[str],
        seasons: Union[int, List[int]],
        circuits: Optional[List[str]] = None
) -> None:
    """Save F1 data to JSON files | 保存F1数据到JSON文件"""
    
    # Get data | 获取数据
    data = load_f1_data(
        drivers=drivers.split(',') if drivers else [],
        seasons=seasons,
        circuits=circuits
    )

    # Reorganize data structure | 重新组织数据结构
    combined_data = {}
    for (season, circuit), session_data in data.items():
        if session_data:  # Ensure data exists | 确保有数据
            combined_data[str(season)] = {
                'circuit': circuit,
                'results': session_data
            }

    # Save data | 保存数据
    for (season, circuit), session_data in data.items():
        output_file = output_dir / f"{season}_{circuit.replace(' ', '_')}_TotalTime_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    save_driver_data(
        drivers='',
        seasons=list(range(1986, 2024)),
        circuits=['Italian Grand Prix']
    )