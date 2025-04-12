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
    if not time_str or time_str.startswith('+'):
        return 0.0
        
    # 处理 "1:20:29.065" 格式（时:分:秒.毫秒）
    parts = time_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    # 处理 "1:23.456" 格式（分:秒.毫秒）
    elif len(parts) == 2:
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    # 处理 "23.456" 格式（秒.毫秒）
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
                
                # 获取第一名的完赛时间
                winner_time = 0.0
                for result in results:
                    if result.get('position') == '1' and 'Time' in result:
                        winner_time = convert_time_to_seconds(result['Time'].get('time', '0'))
                        break
                
                for result in results:
                    if 'Driver' not in result:
                        continue
                        
                    driver_name = f"{result['Driver'].get('givenName', '')} {result['Driver'].get('familyName', '')}"
                    driver_family_name = result['Driver'].get('familyName', '')
                    
                    if not drivers or any(d.lower() in driver_name.lower() or d.lower() in driver_family_name.lower() for d in drivers):
                        if driver_name not in race_data:
                            race_data[driver_name] = {}
                        
                        # 只有当车手完赛并且有时间记录时才计算总时间
                        if 'Time' in result or result.get('status', '') == 'Finished':
                            total_seconds = winner_time
                            if 'Time' in result:
                                time_str = result['Time'].get('time', '')
                                if time_str.startswith('+'):
                                    # 将差值转换为秒数并加上第一名的时间
                                    diff_seconds = convert_time_to_seconds(time_str[1:])
                                    total_seconds = winner_time + diff_seconds
                                else:
                                    total_seconds = convert_time_to_seconds(time_str)
                            
                            race_data[driver_name] = {
                                'total_time': total_seconds
                            }
                        else:
                            # 未完赛车手只记录状态
                            race_data[driver_name] = {
                                'total_time': 0.0
                            }

                if race_data:
                    sessions_data[(season, circuit_name)] = race_data

        except Exception as e:
            print(f"加载赛季数据出错 - 赛季: {season}, 错误: {str(e)}")
            continue


    return sessions_data

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

    # 重新组织数据结构
    combined_data = {}
    for (season, circuit), session_data in data.items():
        if session_data:  # 确保有数据
            combined_data[str(season)] = {
                'circuit': circuit,
                'results': session_data
            }

    # 保存数据
    for (season, circuit), session_data in data.items():
        output_file = output_dir / f"{season}_{circuit.replace(' ', '_')}_TotalTime_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    save_driver_data(
        drivers='',
#        seasons=[1985],
        seasons=list(range(1986, 1995)),
        circuits=['Italian Grand Prix']
    )