import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from pathlib import Path

# Set font for display
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# Set output directory
base_path = Path('.')
output_dir = base_path / 'analysis_result'
output_dir.mkdir(parents=True, exist_ok=True)

# 1. Load all JSON files
data_dir = base_path / 'rawdata_1'
all_data = {}

for file in data_dir.glob('*.json'):
    with open(file, 'r') as f:
        data = json.load(f)
        season_circuit_metric = file.stem
        all_data[season_circuit_metric] = data

# 2. Initialize data analysis storage
analysis_results = {}

# 3. Analyze each data file
for file_name, data in all_data.items():
    try:
        parts = file_name.split('_')
        season = parts[0]
        metric = parts[-1]
        circuit = ' '.join(parts[1:-1])
        
        drivers_data = {}
        for driver, data_dict in data.items():
            try:
                valid_values = []
                year = int(season)
                
                # Pre-1995 data format
                if year < 1995:
                    if isinstance(data_dict, dict) and 'total_time' in data_dict:
                        total_time = float(data_dict['total_time'])
                        if total_time > 0:
                            valid_values.append(total_time)
                
                # Post-1995 lap time format
                elif year > 1995:
                    for lap_num, lap_data in data_dict.items():
                        if isinstance(lap_data, dict) and 'time' in lap_data:
                            try:
                                val = float(lap_data['time'])
                                if val > 0:
                                    valid_values.append(val)
                            except (ValueError, TypeError):
                                continue
                
                if valid_values:
                    drivers_data[driver] = {
                        'mean': float(np.mean(valid_values)),
                        'std': float(np.std(valid_values)) if len(valid_values) > 1 else 0,
                        'min': float(np.min(valid_values)),
                        'max': float(np.max(valid_values)),
                        'values': valid_values
                    }
            except Exception as e:
                print(f"Error processing driver {driver} data: {e}")
                continue
        
        if drivers_data:
            is_total_time = int(season) < 1995
            time_label = 'Total Time (seconds)' if is_total_time else 'Lap Time (seconds)'
            
            # Draw boxplot
            plt.figure(figsize=(12, 6))
            data_for_plot = [values['values'] for values in drivers_data.values()]
            plt.boxplot(data_for_plot, tick_labels=list(drivers_data.keys()))
            plt.title(f'{season} Season {circuit} - {metric} Distribution')
            plt.xticks(rotation=45)
            plt.ylabel(time_label)
            plt.tight_layout()
            plt.savefig(output_dir / f'{file_name}_boxplot.png')
            plt.close()
        
            # Draw trend plot for lap times only
            if not is_total_time:
                plt.figure(figsize=(12, 6))
                for driver, stats in drivers_data.items():
                    plt.plot(stats['values'], label=driver)
                plt.title(f'{season} Season {circuit} - {metric} Lap Progression')
                plt.xlabel('Lap Number')
                plt.ylabel('Lap Time (seconds)')
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(output_dir / f'{file_name}_trend.png')
                plt.close()
        
        if not drivers_data:
            print(f"Warning: No valid data in {file_name}")
            continue

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
        continue

print("Analysis completed! Results saved to analysis_result directory")