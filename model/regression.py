import json
import numpy as np
from pathlib import Path
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV


def load_data():
    """加载特征数据和目标变量数据"""
    base_path = Path(__file__).parent.parent
    feature_path = base_path / 'data' / 'lap_time_zscore_feature'
    target_path = base_path / 'data' / 'total_time_gap_zscore'

    features = []
    targets = []
    driver_names = []
    seasons = []

    # 遍历1996-2024年的数据
    for year in range(1996, 2025):
        # 加载特征数据
        feature_file = feature_path / f'{year}.json'
        if not feature_file.exists():
            continue

        with open(feature_file, 'r', encoding='utf-8') as f:
            feature_data = json.load(f)

        # 加载目标变量数据
        target_file = target_path / f'{year}_Italian_Grand_Prix_TimeGap_results.json'
        if not target_file.exists():
            continue

        with open(target_file, 'r', encoding='utf-8') as f:
            target_data = json.load(f)

        # 只选择在两个数据集中都存在且完赛的车手
        for driver in feature_data:
            if driver in target_data and target_data[driver]['total_time'] != 0:
                # 提取特征
                driver_features = [
                    feature_data[driver]['mean_z_score'],
                    feature_data[driver]['var_z_score'],
                    feature_data[driver]['best_z_score'],
                    feature_data[driver]['worst_z_score'],
                    feature_data[driver]['z_score_range'],
                    feature_data[driver]['median_z_score'],
                    feature_data[driver]['z_score_decay_rate'],
                    feature_data[driver]['mean_delta'],
                    feature_data[driver]['var_delta'],
                    feature_data[driver]['best_delta'],
                    feature_data[driver]['worst_delta'],
                    feature_data[driver]['delta_range'],
                    feature_data[driver]['median_delta'],
                    feature_data[driver]['delta_decay_rate'],
                    feature_data[driver]['outlier_ratio']
                ]

                features.append(driver_features)
                targets.append(target_data[driver]['z_score'])
                driver_names.append(driver)
                seasons.append(year)

    return np.array(features), np.array(targets), driver_names, seasons


def train_elastic_net():
    """训练Elastic Net回归模型"""
    # 加载数据
    X, y, driver_names, seasons = load_data()

    # 添加车手名字和赛季作为特征
    # 对车手名进行编码
    unique_drivers = np.unique(driver_names)
    driver_dict = {driver: i for i, driver in enumerate(unique_drivers)}
    driver_features = np.array([driver_dict[driver] for driver in driver_names]).reshape(-1, 1)

    # 将赛季转换为特征
    season_features = np.array(seasons).reshape(-1, 1)

    # 合并所有特征
    X = np.hstack([X, driver_features, season_features])

    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 分割训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # 定义参数网格
    param_grid = {
        'alpha': [0.001, 0.01, 0.1, 0.5, 1.0],
        'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
    }

    # 创建基础模型
    base_model = ElasticNet(random_state=42, max_iter=10000)

    # 创建网格搜索对象
    grid_search = GridSearchCV(
        base_model,
        param_grid,
        cv=5,
        scoring='r2',
        n_jobs=-1
    )

    # 执行网格搜索
    grid_search.fit(X_train, y_train)

    # 输出最佳参数
    print("Optimal hyperparameters:")
    print(f"alpha: {grid_search.best_params_['alpha']}")
    print(f"l1_ratio: {grid_search.best_params_['l1_ratio']}")

    # 使用最佳参数的模型进行评估
    best_model = grid_search.best_estimator_
    train_score = best_model.score(X_train, y_train)
    test_score = best_model.score(X_test, y_test)

    print(f"\nTraining R²: {train_score:.4f}")
    print(f"Testing R²: {test_score:.4f}")

    # 获取特征重要性并保存为JSON
    feature_names = [
        'mean_z_score', 'var_z_score', 'best_z_score', 'worst_z_score',
        'z_score_range', 'median_z_score', 'z_score_decay_rate',
        'mean_delta', 'var_delta', 'best_delta', 'worst_delta',
        'delta_range', 'median_delta', 'delta_decay_rate', 'outlier_ratio',
        'driver_id', 'season'
    ]

    # 创建权重字典
    weights_dict = {}
    for name, coef in zip(feature_names, best_model.coef_):
        weights_dict[f'w_{name}'] = float(coef)  # 转换为float以确保JSON序列化

    # 保存权重到JSON文件
    output_path = Path(__file__).parent.parent / 'model' / 'feature_weights.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(weights_dict, f, indent=4, ensure_ascii=False)

    print("\n特征权重已保存到:", output_path)

    # 输出所有参数组合的性能
    print("\n所有参数组合的性能:")
    means = grid_search.cv_results_['mean_test_score']
    stds = grid_search.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, grid_search.cv_results_['params']):
        print(f"alpha={params['alpha']}, l1_ratio={params['l1_ratio']}: {mean:.4f} (+/-{std:.4f})")


if __name__ == "__main__":
    train_elastic_net()