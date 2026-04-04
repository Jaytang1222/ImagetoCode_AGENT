# 多智能体图表复现框架

基于阿里云 DashScope API 的多智能体流水线，从参考图表自动生成 ECharts 代码，通过多轮迭代优化实现高质量图表复现。

## 核心功能

- **Agent 1**：多模态模型读图生成 ECharts 代码
- **Agent 2**：视觉差异评估（颜色、坐标轴、文本、趋势）
- **Agent 3**：代码修正指导
- **Agent 4**：融合反馈执行渐进式修订
- **多维验证器**：VLM + 算法融合打分（颜色/文本/结构一致性，支持图表类型自适应）

## 快速开始

### 1. 环境要求

- Python 3.9+
- 阿里云 DashScope API Key
- Tesseract OCR（用于文本一致性验证）

### 2. 安装依赖

```bash
cd MultiAgentFrame-main
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_api_key_here
TESSERACT_CMD=your_tesseract_path_here
```

需要先安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)，然后在 `.env` 中配置正确的安装路径。

### 4. 运行

准备参考图表（如 `data/test.png`），执行：

```bash
python experiments/main.py -i data/test.png -o outputs --max-loops 5 --threshold 0.75
```

### 5. 查看结果

输出目录 `outputs/` 包含：
- `current_echarts.js`：生成的 ECharts 代码
- `preview.html`：可在浏览器中预览
- `generated_chart.png`：渲染截图
- `report_agent2_*.txt`、`report_agent3_*.txt`：各轮评判报告
- `validator_round*.txt`：验证结果

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i` / `--input` | 输入参考图路径 | `input.png` |
| `-o` / `--out` | 输出目录 | `outputs` |
| `--max-loops` | 最大迭代轮数 | `5` |
| `--threshold` | 验证通过阈值（0~1） | `0.75` |

## 工作流程

```
参考图 → Agent1(生成代码) → 渲染截图 → Agent2(视觉评估) 
       → Agent3(代码分析) → Agent4(修订代码) → 多维验证器
       → 未通过则进入下一轮迭代
```

## 多维验证器

融合四个维度评估图表一致性：

1. **颜色一致性**：RGB 直方图 + 网格色块匹配 + HSV 距离
2. **文本一致性**：OCR + BLEU 评分 + 布局偏差
3. **结构一致性**：SSIM + 空间拓扑关系
4. **VLM 感知**：语义和整体观感补充

支持图表类型自适应（line/bar/scatter/pie/radar/heatmap），动态调整权重和阈值。

## 项目结构

```
MultiAgentFrame-main/
├── Agents/              # 四个智能体实现
├── Authenticator/       # 多维验证器
├── utils/               # API 调用和渲染工具
├── experiments/         # 主入口
├── data/                # 测试数据
├── outputs/             # 输出目录
├── requirements.txt     # 依赖列表
└── .env                 # 环境变量配置
```

## 依赖说明

主要依赖（详见 `requirements.txt`）：
- `dashscope`：阿里云 API
- `playwright`：浏览器自动化
- `pytesseract`：OCR 文本识别
- `numpy`、`Pillow`：图像处理
- `python-dotenv`：环境变量管理
