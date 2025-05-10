import json
import os
from pathlib import Path
from typing import Dict, List, Tuple


def get_monza_years_by_driver() -> Dict[str, Dict[str, List[int]]]:
    """
    Get driver's participation records at Monza, including years of participation, completion, and DNF | 获取车手在蒙扎的参赛年份记录，包括参赛年份、完赛年份和未完赛年份

    Returns:
        Dict[str, Dict[str, List[int]]]: Driver names and their corresponding lists of participation, completion, and DNF years | 车手名字和对应的参赛、完赛、未完赛年份列表
    """
    # Use relative path | 使用相对路径
    base_path = Path(__file__).parent.parent
    data_dir = base_path / 'data' / 'lap_time_raw'

    # Add career year limits for drivers | 添加车手的生涯年份限制
    driver_career_limits = {
        "Senna": (1984, 1994),  # Ayrton Senna: 1984-1994
        "Hill": (1992, 1999),  # Damon Hill: 1992-1999
        "Schumacher": (1991, 2012),  # Michael Schumacher: 1991-2012
        "Villeneuve": (1996, 2006),  # Jacques Villeneuve: 1996-2006
        "Hakkinen": (1991, 2001),  # Mika Häkkinen: 1991-2001
        "Coulthard": (1994, 2008),  # David Coulthard: 1994-2008
        "Rosberg": (2006, 2016),  # Nico Rosberg: 2006-2016
        "Alonso": (2001, 2024),  # Fernando Alonso: 2001-present | 2001-至今
        "Raikkonen": (2001, 2021),  # Kimi Räikkönen: 2001-2021
        "Hamilton": (2007, 2024),  # Lewis Hamilton: 2007-present | 2007-至今
        "Vettel": (2007, 2022),  # Sebastian Vettel: 2007-2022
        "Verstappen": (2015, 2024)  # Max Verstappen: 2015-present | 2015-至今
    }

    driver_years = {
        driver: {
            "participated": [],
            "finished": [],  # Add list for completed races | 新增完赛年份列表
            "dnf": []
        } for driver in driver_career_limits.keys()
    }

    # Traverse all files in the data directory | 遍历数据目录下的所有文件
    for filename in os.listdir(data_dir):
        if "Italian_Grand_Prix" in filename:
            year = int(filename.split('_')[0])

            with open(os.path.join(data_dir, filename), 'r') as f:
                data = json.load(f)

            # Check if each driver appears in the data | 检查每个车手是否出现在数据中
            for driver_name, driver_data in data.items():
                # Check if race was completed | 检查是否完赛
                dnf = False
                if year < 1995:
                    if isinstance(driver_data, dict) and driver_data.get('total_time_raw', 0) == 0:
                        dnf = True
                else:
                    if isinstance(driver_data, dict):
                        lap_numbers = [int(lap) for lap in driver_data.keys() if lap.isdigit()]
                        if not lap_numbers or max(lap_numbers) < 53:
                            dnf = True

                # Update data based on driver name | 根据车手名字更新数据
                target_driver = None
                if "Senna" in driver_name:
                    target_driver = "Senna"
                elif "Hill" in driver_name and "Damon" in driver_name:
                    target_driver = "Hill"
                elif "Schumacher" in driver_name and "Michael" in driver_name:
                    target_driver = "Schumacher"
                elif "Villeneuve" in driver_name and "Jacques" in driver_name:
                    target_driver = "Villeneuve"
                elif any(name in driver_name for name in ["Häkkinen", "Hakkinen"]):
                    target_driver = "Hakkinen"
                elif "Coulthard" in driver_name:
                    target_driver = "Coulthard"
                elif "Rosberg" in driver_name and "Nico" in driver_name:
                    target_driver = "Rosberg"
                elif "Alonso" in driver_name:
                    target_driver = "Alonso"
                elif any(name in driver_name for name in ["Räikkönen", "Raikkonen"]):
                    target_driver = "Raikkonen"
                elif "Hamilton" in driver_name:
                    target_driver = "Hamilton"
                elif "Vettel" in driver_name:
                    target_driver = "Vettel"
                elif "Verstappen" in driver_name and "Max" in driver_name:
                    target_driver = "Verstappen"

                if target_driver:
                    # Check if the year is within driver's career range | 检查年份是否在车手的生涯范围内
                    career_start, career_end = driver_career_limits[target_driver]
                    if career_start <= year <= career_end:
                        # Add to participation years list | 添加到参赛年份列表
                        driver_years[target_driver]["participated"].append(year)
                        # If DNF, also add to DNF years list | 如果未完赛，也添加到未完赛年份列表
                        if dnf:
                            driver_years[target_driver]["dnf"].append(year)

    # Sort and deduplicate year lists for each driver, and calculate completion years | 对每个车手的年份列表进行排序和去重，并计算完赛年份
    for driver in driver_years:
        # Sort and deduplicate participation and DNF years | 对参赛和未完赛年份进行排序和去重
        driver_years[driver]["participated"] = sorted(list(set(driver_years[driver]["participated"])))
        driver_years[driver]["dnf"] = sorted(list(set(driver_years[driver]["dnf"])))

        # Calculate completion years: years of participation not included in DNF years | 计算完赛年份：参赛年份中不包含在未完赛年份中的年份
        finished_years = [
            year for year in driver_years[driver]["participated"]
            if year not in driver_years[driver]["dnf"]
        ]
        driver_years[driver]["finished"] = sorted(finished_years)

    return driver_years


def save_to_json(data: Dict[str, Dict[str, List[int]]], output_file: str = "driver_years.json"):
    """
    Save data to JSON file | 将数据保存为JSON文件

    Args:
        data (Dict[str, Dict[str, List[int]]]): Data to be saved | 要保存的数据
        output_file (str): Output filename | 输出文件名
    """
    # Create output directory using relative path | 使用相对路径创建输出目录
    base_path = Path(__file__).parent.parent
    output_dir = base_path / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save file | 保存文件
    output_path = output_dir / output_file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    # Get driver participation year data | 获取车手参赛年份数据
    driver_years = get_monza_years_by_driver()

    # Save as JSON file | 保存为JSON文件
    save_to_json(driver_years)