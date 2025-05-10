# F1 Legendary Drivers Performance Analysis System
# F1 传奇车手性能分析系统

## Project Introduction | 项目简介

This project is a performance analysis system for F1 (Formula One) legendary drivers based on historical data. The system analyzes race data from the Monza circuit between 1985-2024, using machine learning methods to evaluate and rank legendary drivers from different eras.

本项目是一个基于F1（一级方程式赛车）历史数据的传奇车手性能分析系统。系统通过分析1985-2024年蒙扎赛道的比赛数据，使用机器学习方法对不同时代的传奇车手进行性能评估和排名。

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
├── data/                      # 数据相关文件
│   ├── datacalling_*.py      # 数据获取脚本
│   ├── lap_time_raw/         # 原始圈速数据
│   ├── lap_time_zscore/      # 标准化后的圈速数据
│   ├── lap_time_zscore_feature/  # 特征工程结果
│   └── eda/                  # 探索性数据分析
├── model/                    # 模型相关文件
│   ├── feature_engineering.py # 特征工程
│   ├── regression.py         # 回归模型
│   ├── rank.py              # 车手排名
│   └── feature_weights.json  # 特征权重
└── plan/                     # 项目规划文档


## 技术栈

- Python 3.x
- NumPy：数值计算
- Pandas：数据处理
- Scikit-learn：机器学习模型
- Matplotlib & Seaborn：数据可视化
- Requests：API数据获取

## 核心功能实现

### 1. 数据采集与预处理

- 通过Ergast F1 API获取历史比赛数据
- 分别处理1995年前后两种不同格式的比赛数据
- 数据清洗和标准化处理

### 2. 特征工程

主要特征包括：
- 平均Z-Score
- Z-Score方差
- 最佳/最差圈速
- 中位数表现
- 圈速衰减率
- 异常值比例

### 3. 性能建模

使用弹性网络回归模型，结合以下特征：
- 圈速统计特征
- 完赛率
- 历史表现
- 赛季因素

### 4. 排名系统

基于以下因素综合评估：
- 模型预测得分
- 历史成绩
- 跨时代表现校准

## 使用说明

1. 数据获取：
```bash
python data/datacalling_after1995.py  # 获取1996年后数据
python data/datacalling_before1995.py  # 获取1995年前数据
```
2. 特征工程：
```bash
python model/feature_engineering.py
```
3. 性能建模：
```bash
python model/regression.py
```
4. 排名系统：
```bash
python model/rank.py
```
## 分析结果
系统能够对不同时代的F1传奇车手进行客观的性能评估，主要结论包括：

- 基于圈速的标准化评分
- 跨时代性能比较
- 车手特点分析

## 注意事项
- 数据获取需要稳定的网络连接
- 部分历史数据可能存在缺失
- 跨时代比较需要考虑技术发展因素