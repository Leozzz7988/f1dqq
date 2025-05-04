import json
import os
from pathlib import Path
from typing import Dict, List

def get_monza_years_by_driver() -> Dict[str, List[int]]:
    """
    获取车手在蒙扎参赛的年份记录
    
    Returns:
        Dict[str, List[int]]: 车手名字和对应的参赛年份列表
    """
    # 使用相对路径
    base_path = Path(__file__).parent.parent
    data_dir = base_path / 'data' / 'rawdata_1'
    driver_years = {
        "Senna": [],
        "Hill": [],
        "Schumacher": [],
        "Villeneuve": [],
        "Hakkinen": [],
        "Coulthard": [],
        "Rosberg": [],
        "Alonso": [],
        "Raikkonen": [],
        "Hamilton": [],
        "Vettel": [],
        "Verstappen": []
    }
    
    # 遍历数据目录下的所有文件
    for filename in os.listdir(data_dir):
        if "Italian_Grand_Prix" in filename:
            # 从文件名中提取年份
            year = int(filename.split('_')[0])
            
            # 读取文件内容
            with open(os.path.join(data_dir, filename), 'r') as f:
                data = json.load(f)
                
            # 检查每个车手是否出现在数据中
            for driver_name, driver_data in data.items():
                if "Senna" in driver_name:
                    driver_years["Senna"].append(year)
                elif "Hill" in driver_name and "Damon" in driver_name:
                    driver_years["Hill"].append(year)
                elif "Schumacher" in driver_name and "Michael" in driver_name:
                    driver_years["Schumacher"].append(year)
                elif "Villeneuve" in driver_name and "Jacques" in driver_name:
                    driver_years["Villeneuve"].append(year)
                elif any(name in driver_name for name in ["Häkkinen", "Hakkinen"]):
                    driver_years["Hakkinen"].append(year)
                elif "Coulthard" in driver_name:
                    driver_years["Coulthard"].append(year)
                elif "Rosberg" in driver_name and "Nico" in driver_name:
                    driver_years["Rosberg"].append(year)
                elif "Alonso" in driver_name:
                    driver_years["Alonso"].append(year)
                elif any(name in driver_name for name in ["Räikkönen", "Raikkonen"]):
                    driver_years["Raikkonen"].append(year)
                elif "Hamilton" in driver_name:
                    driver_years["Hamilton"].append(year)
                elif "Vettel" in driver_name:
                    driver_years["Vettel"].append(year)
                elif "Verstappen" in driver_name and "Max" in driver_name:
                    driver_years["Verstappen"].append(year)
    
    # 对每个车手的年份列表进行排序和去重
    for driver in driver_years:
        driver_years[driver] = sorted(list(set(driver_years[driver])))
    
    return driver_years

def save_to_json(data: Dict[str, List[int]], output_file: str = "monza_years.json"):
    """
    将数据保存为JSON文件
    
    Args:
        data (Dict[str, List[int]]): 要保存的数据
        output_file (str): 输出文件名
    """
    # 使用相对路径创建输出目录
    base_path = Path(__file__).parent.parent
    output_dir = base_path / 'data' 
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    output_path = output_dir / output_file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    # 获取车手参赛年份数据
    driver_years = get_monza_years_by_driver()
    
    # 保存为JSON文件
    save_to_json(driver_years)