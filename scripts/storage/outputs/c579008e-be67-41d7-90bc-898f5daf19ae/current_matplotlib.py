import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(9, 6))

# 数据
x = np.array([5, 10, 15, 20, 25])
gnn_ts = np.array([0.5, 1.0, 2.0, 2.5, 3.0])
diff_ts = np.array([1.0, 2.0, 3.0, 5.0, 6.0])
mlsimp = np.array([40, 42, 50, 65, 70])
s3 = np.array([45, 47, 60, 62, 65])

# 柱状图参数
bar_width = 0.2
colors = ['#add8e6', '#00008b', '#90ee90', '#228b22']
hatches = ['-', '|', '/', '\\']
labels = ['GNN-TS', 'Diff-TS', 'MLSIMP', 'S3']

# 绘制柱状图
for i, (data, color, hatch, label) in enumerate(zip(
    [gnn_ts, diff_ts, mlsimp, s3], 
    colors, 
    hatches, 
    labels
)):
    offset = (i - 1.5) * bar_width
    ax.bar(x + offset, data, width=bar_width, color=color, hatch=hatch, 
           edgecolor='black', label=label, alpha=0.8)

# 配置坐标轴
ax.set_xlabel('Data size (×10³)', fontsize=12)
ax.set_ylabel('Training time (s/epoch)', fontsize=12)
ax.set_ylim(0, 80)
ax.set_yticks(np.arange(0, 81, 20))
ax.set_xticks(x)

# 图例配置
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fontsize=10, frameon=False)

# 网格和布局
ax.grid(False)
plt.tight_layout()
plt.savefig(output_path, dpi=100, bbox_inches='tight')