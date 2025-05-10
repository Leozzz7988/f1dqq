import json
from pathlib import Path

def load_data():
    """加载特征权重和传奇车手统计数据"""
    base_path = Path(__file__).parent.parent
    
    # 加载特征权重
    with open(base_path / 'model' / 'feature_weights.json', 'r', encoding='utf-8') as f:
        weights = json.load(f)
    
    # 加载传奇车手统计数据
    with open(base_path / 'data' / 'legendary_drivers_statistics.json', 'r', encoding='utf-8') as f:
        stats = json.load(f)
        
    return weights, stats

def calculate_score(driver_stats, weights):
    """计算单个车手的得分"""
    score = 0
    
    # 计算各个特征的加权和
    feature_mappings = {
        'mean_z_score': 'w_mean_z_score',
        'var_z_score': 'w_var_z_score',
        'best_z_score': 'w_best_z_score',
        'median_z_score': 'w_median_z_score',
        'z_score_decay_rate': 'w_z_score_decay_rate',
        'best_delta': 'w_best_delta',
        'worst_delta': 'w_worst_delta',
        'median_delta': 'w_median_delta',
        'outlier_ratio': 'w_outlier_ratio'
    }
    
    for stat_key, weight_key in feature_mappings.items():
        if stat_key in driver_stats and weight_key in weights:
            score += driver_stats[stat_key] * weights[weight_key]
    
    return score

def rank_drivers():
    """计算并输出传奇车手排名"""
    # 加载数据
    weights, stats = load_data()
    
    # 计算每个车手的得分
    driver_scores = []
    for driver_name, driver_stats in stats.items():
        score = calculate_score(driver_stats, weights)
        driver_scores.append((driver_name, score))
    
    # 修改这里：按得分从小到大排序（去掉reverse=True）
    driver_scores.sort(key=lambda x: x[1])
    
    # 打印排名结果
    print("\nHistorical Legends in Parallel Monza Race:")
    print("-" * 40)
    print(f"{'Ranking':<6}{'Driver':<20}{'Score':<10}")
    print("-" * 40)
    
    for rank, (driver, score) in enumerate(driver_scores, 1):
        print(f"{rank:<6}{driver:<20}{score:.4f}")

if __name__ == "__main__":
    rank_drivers()