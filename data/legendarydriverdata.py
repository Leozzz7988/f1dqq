import json
from pathlib import Path

def load_driver_years():
    """加载车手年份数据"""
    base_path = Path(__file__).parent
    try:
        with open(base_path / 'driver_years.json', 'r', encoding='utf-8') as f:  # 修改为正确的文件名
            return json.load(f)
    except FileNotFoundError:
        print("错误：找不到 driver_years.json 文件")
        return None
    except json.JSONDecodeError:
        print("错误：driver_years.json 文件格式不正确")
        return None

def load_preprocessed_data(year):
    """加载预处理后的数据"""
    base_path = Path(__file__).parent
    try:
        with open(base_path / 'lap_time_zscore' / f'{year}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"警告：{year}年的数据文件不存在")
        return None
    except json.JSONDecodeError:
        print(f"错误：{year}年的数据文件格式不正确")
        return None

def get_driver_full_name(driver_key):
    """获取车手的完整名称"""
    driver_names = {
        "Senna": "Ayrton Senna",
        "Hill": "Damon Hill",
        "Schumacher": "Michael Schumacher",
        "Villeneuve": "Jacques Villeneuve",
        "Hakkinen": "Mika Häkkinen",
        "Coulthard": "David Coulthard",
        "Rosberg": "Nico Rosberg",
        "Alonso": "Fernando Alonso",
        "Raikkonen": "Kimi Räikkönen",
        "Hamilton": "Lewis Hamilton",
        "Vettel": "Sebastian Vettel",
        "Verstappen": "Max Verstappen"
    }
    return driver_names.get(driver_key, driver_key)

def extract_driver_data():
    """提取所有传奇车手的数据"""
    driver_years = load_driver_years()
    if not driver_years:
        print("错误：无法加载车手年份数据")
        return

    legendary_data = {}

    for driver_key, years_data in driver_years.items():
        participated_years = years_data.get('participated', [])
        if not participated_years:
            print(f"警告：{driver_key} 没有参赛记录")
            continue

        driver_full_name = get_driver_full_name(driver_key)
        driver_data = {}

        for year in participated_years:
            year_data = load_preprocessed_data(year)
            if year_data:
                # 在年度数据中查找车手数据（使用完整名称）
                for name, data in year_data.items():
                    if driver_full_name.lower() in name.lower():
                        # 检查数据结构并相应处理
                        if isinstance(data, dict):
                            if 'z_score' in data:  # 直接存储的 z_score（total_time_raw 数据）
                                driver_data[str(year)] = {'total_time_raw': {'z_score': data['z_score']}}
                            else:  # 按圈数存储的数据
                                filtered_data = {}
                                for lap_num, lap_data in data.items():
                                    if isinstance(lap_data, dict) and 'z_score' in lap_data:
                                        filtered_data[lap_num] = {'z_score': lap_data['z_score']}
                                if filtered_data:
                                    driver_data[str(year)] = filtered_data
                        print(f"成功提取 {driver_full_name} 在 {year} 年的数据")
                        break

        if driver_data:
            legendary_data[driver_full_name] = driver_data
        else:
            print(f"警告：未找到 {driver_full_name} 的任何数据")

    if not legendary_data:
        print("错误：未能提取到任何车手数据")
        return

    # 保存数据
    base_path = Path(__file__).parent
    output_file = base_path / 'legendary_drivers_data.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(legendary_data, f, indent=4, ensure_ascii=False)
        print(f"成功保存数据到 {output_file}")
    except Exception as e:
        print(f"保存数据时出错：{e}")

if __name__ == "__main__":
    extract_driver_data()