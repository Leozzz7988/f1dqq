import fastf1
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from ..data.datacalling import load_driver_data

class DriverModel:
    def __init__(self, driver_name: str, seasons: List[int]):
        self.driver_name = driver_name
        self.seasons = seasons
        self.sessions_data = load_driver_data(driver_name, seasons)

    def _load_historical_data(self):
        """加载历史数据"""
        for season in self.seasons:
            try:
                schedule = fastf1.get_event_schedule(season)
                if schedule.empty:
                    print(f"No data available for season {season}")
                    continue
                    
                for idx, event in schedule.iterrows():
                    try:
                        race = fastf1.get_session(season, event['EventName'], 'R')
                        quali = fastf1.get_session(season, event['EventName'], 'Q')
                        race.load()
                        quali.load()
                        self.sessions_data[(season, event['EventName'])] = {
                            'race': race,
                            'quali': quali
                        }
                    except Exception as e:
                        print(f"Error loading data for {season} {event['EventName']}: {e}")
            except Exception as e:
                print(f"Error loading schedule for season {season}: {e}")

    def analyze_speed(self) -> Dict:
        """
        速度分析
        - 最快圈速：统计每场比赛的最快圈速并计算平均值
        - 杆位率：计算获得杆位的比例
        - 排位赛表现：分析平均排位赛位置
        """
        fastest_laps = []
        quali_positions = []
        pole_positions = 0
        
        for session_data in self.sessions_data.values():
            quali = session_data['quali']
            driver_quali = quali.laps.pick_driver(self.driver_name)
            if not driver_quali.empty:
                fastest_laps.append(driver_quali['LapTime'].min())
                quali_position = driver_quali['Position'].iloc[0]
                quali_positions.append(quali_position)
                if quali_position == 1:
                    pole_positions += 1

        return {
            'avg_fastest_lap': np.mean(fastest_laps),
            'pole_rate': pole_positions / len(self.sessions_data),
            'avg_quali_position': np.mean(quali_positions)
        }

    def analyze_attack(self) -> Dict:
        """
        进攻能力分析
        - 位置变化：计算比赛中的超车次数和位置提升
        - 超车效率：分析成功超车的比例和平均超车用时
        """
        position_changes = []
        overtake_speeds = []

        for session_data in self.sessions_data.values():
            race = session_data['race']
            driver_race = race.laps.pick_driver(self.driver_name)
            if not driver_race.empty:
                start_pos = driver_race['Position'].iloc[0]
                end_pos = driver_race['Position'].iloc[-1]
                position_changes.append(start_pos - end_pos)

        return {
            'avg_position_gain': np.mean(position_changes),
            'overtake_efficiency': len([x for x in position_changes if x > 0]) / len(position_changes)
        }

    def analyze_defense(self) -> Dict:
        """
        防守能力分析
        - 起步后位置保持：分析发车后的位置保持能力
        - 防守成功率：计算成功防守的比例
        """
        defense_stats = []
        first_lap_positions = []

        for session_data in self.sessions_data.values():
            race = session_data['race']
            driver_race = race.laps.pick_driver(self.driver_name)
            if not driver_race.empty:
                first_lap_pos = driver_race[driver_race['LapNumber'] == 1]['Position'].iloc[0]
                first_lap_positions.append(first_lap_pos)

        return {
            'first_lap_retention': np.mean(first_lap_positions),
            'defense_success_rate': len([x for x in first_lap_positions if x <= 3]) / len(first_lap_positions)
        }

    def analyze_tyre_management(self) -> Dict:
        """
        轮胎管理分析
        - stint长度：分析每个轮胎使用时长
        - 轮胎策略：评估不同轮胎配置的使用效果
        """
        stint_lengths = []
        tyre_strategies = []

        for session_data in self.sessions_data.values():
            race = session_data['race']
            driver_race = race.laps.pick_driver(self.driver_name)
            if not driver_race.empty:
                stints = driver_race.groupby('Stint')['LapNumber'].count()
                stint_lengths.extend(stints.values)
                
        return {
            'avg_stint_length': np.mean(stint_lengths),
            'long_stint_ability': len([x for x in stint_lengths if x > np.mean(stint_lengths)]) / len(stint_lengths)
        }

    def analyze_wet_performance(self) -> Dict:
        """
        雨战表现分析
        - 雨战成绩：统计雨天比赛的完赛位置
        - 雨战完赛率：分析雨天比赛的完赛情况
        """
        wet_race_results = []
        wet_incidents = 0

        for session_data in self.sessions_data.values():
            race = session_data['race']
            if race.weather_data is not None and 'Wet' in race.weather_data['Weather'].values:
                driver_race = race.laps.pick_driver(self.driver_name)
                if not driver_race.empty:
                    wet_race_results.append(driver_race['Position'].iloc[-1])

        return {
            'wet_race_avg_position': np.mean(wet_race_results) if wet_race_results else None,
            'wet_race_completion_rate': 1 - (wet_incidents / len(wet_race_results)) if wet_race_results else None
        }

    def analyze_stability(self) -> Dict:
        """
        稳定性分析
        - DNF率：计算未完赛的比例
        - 事故率：统计比赛中的事故发生频率
        """
        dnf_count = 0
        incidents = 0

        for session_data in self.sessions_data.values():
            race = session_data['race']
            driver_race = race.laps.pick_driver(self.driver_name)
            if not driver_race.empty:
                if 'DNF' in driver_race['Status'].values:
                    dnf_count += 1

        return {
            'reliability': 1 - (dnf_count / len(self.sessions_data)),
            'incident_rate': incidents / len(self.sessions_data)
        }

    def get_complete_profile(self) -> Dict:
        """获取完整的车手数据分析结果"""
        return {
            'speed': self.analyze_speed(),
            'attack': self.analyze_attack(),
            'defense': self.analyze_defense(),
            'tyre_management': self.analyze_tyre_management(),
            'wet_performance': self.analyze_wet_performance(),
            'stability': self.analyze_stability()
        }
#w1, w2,w3,w4,w5
#Ham_speed = w1 * + w2 =

hamilton = DriverModel("HAM", [2021,2022,2023,2024])
profile = hamilton.get_complete_profile()