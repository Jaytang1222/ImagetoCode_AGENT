from pyecharts.charts import Pie
from pyecharts.options import LabelOpts, TitleOpts, LegendOpts

# 数据准备
data = [
    ("供应链金融", 34),
    ("跨境支付结算", 15),
    ("贸易融资", 13),
    ("资产托管", 8),
    ("保险", 6),
    ("股权交易", 4),
    ("企业贷款", 7),
    ("其他", 9)
]

# 创建环形图
pie = Pie()
pie.add(
    "",
    data,
    radius=["40%", "70%"],  # 内外圆半径，形成环形
    label_opts=LabelOpts(
        formatter="{b}: {c} ({d}%)",
        position="outside"
    ),
)

pie.set_global_opts(
    title_opts=TitleOpts(title="图表 7：金融区块链应用落地领域分布（单位：个，%）"),
    legend_opts=LegendOpts(is_show=True, orient="vertical", pos_right="10%"),
)

# 渲染为 HTML 文件
pie.render("financial_blockchain_pie.html")