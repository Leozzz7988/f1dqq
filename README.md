# F1 Legendary Drivers Performance Analysis System
# F1 传奇车手性能分析系统

## Project Introduction | 项目简介

This project is a performance analysis system for F1 (Formula One) legendary drivers based on historical data. The system analyzes race data from the Monza circuit between 1985-2024, using machine learning methods to evaluate and rank legendary drivers from different eras.

本项目是一个基于F1（一级方程式赛车）历史数据的传奇车手性能分析系统。系统通过分析1985-2024年蒙扎赛道的比赛数据，使用机器学习方法对不同时代的传奇车手进行性能评估和排名。

Link to the full report | 完整报告的链接

https://docs.google.com/document/d/1rvrO-lkVA3T7h1nOe9vtnrE43F8K90zjTDkcutHkOPo/edit?tab=t.0

## Features | 功能特点

- Data Collection: Automatically retrieve race data for the Monza Grand Prix from 1985-2024 using the Ergast F1 API
- 数据采集：自动从Ergast F1 API获取1985-2024年蒙扎大奖赛的比赛数据

- Data Processing | 数据处理：
  - Lap time standardization (Z-Score)
  - 圈速标准化（Z-Score）
  - Race completion time difference analysis
  - 完赛时间差异分析
  - Feature engineering and statistical analysis
  - 特征工程和统计分析

- Performance Evaluation | 性能评估：
  - Driver performance modeling using elastic net regression
  - 使用弹性网络回归模型进行车手性能建模
  - Multi-dimensional feature weight analysis
  - 多维度特征权重分析
  - Cross-era driver performance comparison
  - 跨时代车手性能比较

- Visualization Analysis | 可视化分析：
  - Lap time distribution box plots
  - 圈速分布箱线图
  - Race progression trend charts
  - 比赛进程趋势图
  - Performance metrics statistical charts
  - 性能指标统计图

## Project Structure | 项目结构
f1dqq/

├── data/                      # Data related files | 数据相关文件

│   ├── datacalling_*.py      # Data fetching scripts | 数据获取脚本

│   ├── lap_time_raw/         # Raw lap time data | 原始圈速数据

│   ├── lap_time_zscore/      # Standardized lap time data | 标准化后的圈速数据

│   ├── lap_time_zscore_feature/  # Feature engineering results | 特征工程结果

│   └── eda/                  # Exploratory data analysis | 探索性数据分析

├── model/                    # Model related files | 模型相关文件

│   ├── feature_engineering.py # Feature engineering | 特征工程

│   ├── regression.py         # Regression model | 回归模型

│   ├── rank.py              # Driver ranking | 车手排名

│   └── feature_weights.json  # Feature weights | 特征权重

└── plan/                     # Project planning documents | 项目规划文档



## Tech Stack | 技术栈

- Python 3.x
- NumPy: Numerical computation | 数值计算
- Pandas: Data processing | 数据处理
- Scikit-learn: Machine learning models | 机器学习模型
- Matplotlib & Seaborn: Data visualization | 数据可视化
- Requests: API data retrieval | API数据获取

## Core Functionality Implementation | 核心功能实现

### 1. Data Collection and Preprocessing | 数据采集与预处理

- Retrieve historical race data through Ergast F1 API
- 通过Ergast F1 API获取历史比赛数据
- Process two different data formats before and after 1995
- 分别处理1995年前后两种不同格式的比赛数据
- Data cleaning and standardization processing
- 数据清洗和标准化处理

### 2. Feature Engineering | 特征工程

Main features include | 主要特征包括：
- Average Z-Score | 平均Z-Score
- Z-Score variance | Z-Score方差
- Best/Worst lap times | 最佳/最差圈速
- Median performance | 中位数表现
- Lap time decay rate | 圈速衰减率
- Outlier ratio | 异常值比例

### 3. Performance Modeling | 性能建模

Using elastic net regression model, combining the following features | 使用弹性网络回归模型，结合以下特征：
- Lap time statistical features | 圈速统计特征
- Completion rate | 完赛率
- Historical performance | 历史表现
- Season factors | 赛季因素

### 4. Ranking System | 排名系统

Comprehensive evaluation based on | 基于以下因素综合评估：
- Model prediction scores | 模型预测得分
- Historical results | 历史成绩
- Cross-era performance calibration | 跨时代表现校准

## Usage Instructions | 使用说明

1. Data Collection | 数据获取：
```bash
python data/datacalling_after1995.py  # Get post-1996 data | 获取1996年后数据
python data/datacalling_before1995.py  # Get pre-1995 data | 获取1995年前数据
```

2. Feature Engineering | 特征工程：
```bash
python model/feature_engineering.py
```
3. Performance Modeling | 性能建模：
```bash
python model/regression.py
```
4. Ranking System | 排名系统：
```bash
python model/rank.py
```
## Analysis Results | 分析结果
The system can objectively evaluate F1 legendary drivers from different eras, with main conclusions including:
系统能够对不同时代的F1传奇车手进行客观的性能评估，主要结论包括：

- Standardized lap time scores | 基于圈速的标准化评分
- Cross-era performance comparison | 跨时代性能比较
- Driver characteristics analysis | 车手特点分析

## Notes | 注意事项
- Stable network connection required for data retrieval | 数据获取需要稳定的网络连接
- Some historical data may be missing | 部分历史数据可能存在缺失
- Cross-era comparison needs to consider technological advancement factors | 跨时代比较需要考虑技术发展因素