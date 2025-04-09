import json
import fastf1
import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional, Union

# 设置缓存目录
PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = os.path.join(PROJECT_ROOT, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)


def load_f1_data(
        drivers: Union[str, List[str]],
        seasons: Union[int, List[int]],
        circuits: Optional[List[str]] = None,
        data_columns: Optional[List[str]] = None,
) -> Dict:
    """
    加载F1数据，支持多个维度的筛选

    Args:
        drivers: 车手代号或车手代号列表（如 'HAM' 或 ['HAM', 'VER']）
        seasons: 赛季或赛季列表（如 2023 或 [2021, 2022, 2023]）
        circuits: 赛道名称列表（如 ['Monza', 'Spa']），默认为所有赛道
        data_columns: 需要获取的数据列名（如 ['LapTime', 'Speed', 'Position']）

    Returns:
        包含筛选后数据的字典
    """
    drivers = [drivers] if isinstance(drivers, str) else drivers
    seasons = [seasons] if isinstance(seasons, int) else seasons
    circuits = circuits if circuits else []
    data_columns = data_columns if data_columns else ['LapTime', 'Position']

    sessions_data = {}

    fastf1.set_log_level('WARNING')
    fastf1.Cache.enable_cache(CACHE_DIR)

    for season in seasons:
        try:
            schedule = fastf1.get_event_schedule(season)
            if schedule.empty:
                print(f"赛季 {season} 无可用数据")
                continue

            if circuits:
                schedule = schedule[schedule['EventName'].isin(circuits)]

            for idx, event in schedule.iterrows():
                try:
                    race = fastf1.get_session(season, event['EventName'], 'R')
                    quali = fastf1.get_session(season, event['EventName'], 'Q')
                    race.load()
                    quali.load()

                    event_data = {'race': {}, 'quali': {}}

                    # 处理比赛数据
                    for driver in drivers:
                        # 使用 DriverNumber 筛选特定车手
                        race_laps = race.laps[race.laps['DriverNumber'].astype(str) == str(driver)]
                        quali_laps = quali.laps[quali.laps['DriverNumber'].astype(str) == str(driver)]

                        # 检查请求的数据列是否可用
                        available_columns = [col for col in data_columns if col in race_laps.columns]
                        if not available_columns:
                            print(f"警告: 在数据中未找到以下列: {set(data_columns) - set(race_laps.columns)}")
                            continue

                        if not race_laps.empty:
                            event_data['race'][driver] = race_laps[available_columns]
                        if not quali_laps.empty:
                            event_data['quali'][driver] = quali_laps[available_columns]

                    sessions_data[(season, event['EventName'])] = event_data

                except Exception as e:
                    print(f"加载数据出错 - 赛季: {season}, 赛道: {event['EventName']}, 错误: {e}")
        except Exception as e:
            print(f"加载赛季数据出错 - 赛季: {season}, 错误: {e}")

    return sessions_data


def save_driver_data(
        drivers: Optional[str],
        seasons: Union[int, List[int]],
        circuits: Union[str, List[str]],
        data_columns: List[str]
) -> None:
    # 处理输入参数
    seasons = [seasons] if isinstance(seasons, int) else seasons
    circuits = [circuits] if isinstance(circuits, str) else circuits

    base_path = Path(__file__).parent
    output_dir = base_path / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 遍历每个赛季和赛道
    for season in seasons:
        for circuit in circuits:
            session = fastf1.get_session(season, circuit, 'R')
            try:
                session.load()
                if not hasattr(session, 'laps') or session.laps.empty:
                    print(f"警告: {season} 赛季 {circuit} 的数据不可用")
                    continue

                # 如果没有指定车手，获取所有参赛车手
                all_drivers = drivers.split(',') if drivers else session.drivers

                # 为每个数据列创建数据集
                for data_col in data_columns:
                    data_dict = {}
                    # 获取每个车手的数据
                    for driver in all_drivers:
                        driver_laps = session.laps[session.laps['DriverNumber'] == driver]
                        if not driver_laps.empty and data_col in driver_laps.columns:
                            values = driver_laps[data_col].values
                            if len(values) > 0:
                                if 'Time' in data_col:
                                    values = [float(v) / 1e9 if pd.notnull(v) else None for v in values]
                                else:
                                    values = values.tolist()
                                data_dict[driver] = values

                    # 保存为json文件
                    if data_dict:
                        output_file = output_dir / f"{season}_{circuit}_{data_col}.json"
                        with open(output_file, 'w') as f:
                            json.dump(data_dict, f, indent=4)

            except Exception as e:
                print(f"错误: 无法加载 {season} 赛季 {circuit} 的数据: {e}")
                continue


if __name__ == "__main__":
    save_driver_data(
        drivers='',
        seasons=[2018, 2019],
        circuits=['Italian Grand Prix'],
        data_columns=['Sector1Time', 'Sector2Time', 'Sector3Time', 'LapTime', 'SpeedFL']
    )

