import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

# 设置画布大小
fig, ax = plt.subplots(figsize=(9, 6))

# 模拟数据以复现图表分布
# 为了复现直方图的高度和 KDE 曲线的形状，我们需要构造特定均值和方差的数据
np.random.seed(42)

# Compact (蓝色): 分布在 18-25 左右，较宽
# 为了复现双峰或宽分布，混合两个正态分布
data_compact = np.concatenate([
    np.random.normal(19, 1.5, 150),
    np.random.normal(21, 2.0, 100)
])

# SUV (橙黄色): 分布在 10-16 左右
data_suv = np.concatenate([
    np.random.normal(11.5, 1.0, 100),
    np.random.normal(13.5, 1.2, 100)
])

# Minivan (绿色): 分布在 16-17 左右，非常集中（导致高峰）
data_minivan = np.random.normal(16.5, 0.5, 80)

# 定义颜色 (近似取色)
color_compact = '#56B4F9'
color_suv = '#FDBF5E'
color_minivan = '#56B958'

# 绘制直方图
# density=True 确保直方图面积为 1，与 KDE 曲线尺度一致
# edgecolor='white' 复现柱子之间的间隔
ax.hist(data_compact, bins=15, density=True, alpha=0.8, color=color_compact, 
        label='_nolegend_', edgecolor='white', linewidth=1)
ax.hist(data_suv, bins=15, density=True, alpha=0.8, color=color_suv, 
        label='_nolegend_', edgecolor='white', linewidth=1)
ax.hist(data_minivan, bins=15, density=True, alpha=0.8, color=color_minivan, 
        label='_nolegend_', edgecolor='white', linewidth=1)

# 绘制 KDE (核密度估计) 曲线
def plot_kde_line(data, color, label, linewidth=2.5):
    # 使用 gaussian_kde 计算密度
    kde = gaussian_kde(data)
    # 生成 x 轴数据点，范围覆盖数据并稍作延伸
    x_min = min(data) - 2
    x_max = max(data) + 2
    x = np.linspace(x_min, x_max, 200)
    # 绘制曲线
    ax.plot(x, kde(x), color=color, linewidth=linewidth, label=label)

plot_kde_line(data_compact, color_compact, 'Compact')
plot_kde_line(data_suv, color_suv, 'SUV')
plot_kde_line(data_minivan, color_minivan, 'minivan')

# 设置标题
ax.set_title('Density Plot of City Mileage by Vehicle Type', fontsize=14, pad=15)

# 设置 X 轴标签和范围
ax.set_xlabel('cty', fontsize=12)
ax.set_xlim(5, 35)
ax.set_xticks(np.arange(5, 36, 5))

# 设置 Y 轴范围和刻度
ax.set_ylim(0, 0.35)
ax.set_yticks(np.arange(0, 0.36, 0.05))
# 格式化 Y 轴刻度为两位小数
ax.set_yticklabels(['{:.2f}'.format(x) for x in np.arange(0, 0.36, 0.05)])

# 设置图例
# loc='upper right' 对应右上角，frameon=False 去除图例边框
ax.legend(loc='upper right', fontsize=11, frameon=False)

# 调整布局并保存
plt.tight_layout()
plt.savefig(output_path, dpi=100, bbox_inches='tight')