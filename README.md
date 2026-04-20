# 多智能体图表复现框架

基于阿里云 DashScope API 的多智能体流水线，从参考图表自动生成 Matplotlib/ECharts 代码，通过多轮迭代优化实现高质量图表复现。

## 核心功能

- **Agent 1**：多模态模型读图生成 Matplotlib/ECharts 代码（可选格式）
- **Agent 2**：视觉差异评估（颜色、坐标轴、文本、趋势）
- **Agent 3**：代码修正指导
- **Agent 4**：融合反馈执行渐进式修订
- **多维验证器**：VLM + 算法融合打分（颜色/文本/结构一致性，支持图表类型自适应）
  - 渐变色检测（KMeans 聚类）
  - OCR 后处理校正（自动修正 0/O、1/l/I 混淆）
  - 自适应 BLEU（短文本用 BLEU-2，长文本用 BLEU-4）
  - 多尺度 SSIM + Harris 角点检测
  - VLM 评分校准（解决量纲不一致问题）

## 快速开始

### 1. 环境要求

- Python 3.9+
- 阿里云 DashScope API Key
- Tesseract OCR（用于文本一致性验证）
- (可选) Playwright 浏览器（用于 ECharts 渲染）

### 2. 安装依赖

```bash
cd MultiAgentFrame-main
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器（仅使用 ECharts 时需要）

```bash
playwright install chromium
```

### 4. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_api_key_here
TESSERACT_CMD=your_tesseract_path_here
```

需要先安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)，然后在 `.env` 中配置正确的安装路径。

### 5. 运行

准备参考图表（如 `data/test.png`），执行：

#### 生成 Matplotlib 代码（默认）

```bash
python experiments/main.py -i data/test.png -o outputs --max-loops 5 --threshold 0.75 --format matplotlib
```

或简写（matplotlib 为默认）：

```bash
python experiments/main.py -i data/test.png -o outputs
```

#### 生成 ECharts 代码（新增）

```bash
python experiments/main.py -i data/test.png -o outputs --max-loops 5 --threshold 0.75 --format echarts
```

### 6. 查看结果

输出目录 `outputs/` 包含：

**Matplotlib 格式**：
- `current_matplotlib.py`：生成的 Matplotlib Python 代码
- `generated_chart.png`：渲染截图
- `report_agent2_*.txt`、`report_agent3_*.txt`：各轮评判报告
- `validator_round*.txt`：验证结果

**ECharts 格式**：
- `current_echarts.js`：生成的 ECharts JavaScript 代码
- `preview.html`：可在浏览器中预览的 HTML 文件
- `generated_chart.png`：渲染截图
- `report_agent2_*.txt`、`report_agent3_*.txt`：各轮评判报告
- `validator_round*.txt`：验证结果

## 命令行参数

| 参数 | 说明 | 默认值 | 选项 |
|------|------|--------|------|
| `-i` / `--input` | 输入参考图路径 | `input.png` | - |
| `-o` / `--out` | 输出目录 | `outputs` | - |
| `--max-loops` | 最大迭代轮数 | `5` | - |
| `--threshold` | 验证通过阈值（0~1） | `0.75` | 0.0 ~ 1.0 |
| `--format` | 输出代码格式 | `matplotlib` | `matplotlib` / `echarts` |

## 验证器优化特性

### 1. 渐变色检测
- 使用 KMeans 聚类提取主色
- 检测图像中的渐变强度
- 根据渐变强度自适应调整 HSV 权重

### 2. OCR 后处理校正
- 自动修正常见混淆：0↔O、1↔l↔I
- 校正括号、百分号等特殊字符
- 提升文本识别准确率约 10%

### 3. 自适应 BLEU
- 短文本（≤5 字符）：使用 BLEU-2
- 中等文本（5-15 字符）：使用 BLEU-3
- 长文本（>15 字符）：使用 BLEU-4
- 解决短文本 BLEU-4 过于严格的问题

### 4. 多尺度 SSIM
- 在 3 个尺度（原图、1/2、1/4）上计算 SSIM
- 加权平均提升对渲染差异的鲁棒性
- 对抗锯齿、字体渲染差异更宽容

### 5. Harris 角点检测
- 融合边缘检测 + 角点检测
- 提升关键点提取稳定性
- 对图表结构特征更敏感

### 6. VLM 评分校准
- 自动检测 VLM 评分与算法评分的差异
- 差异 > 0.2 时进行校准（校准因子 0.6）
- 解决主观评分与客观算法量纲不一致问题

## 依赖说明

主要依赖（详见 `requirements.txt`）：

### 核心依赖
- `dashscope>=1.14.0`：阿里云 API
- `numpy>=1.24.0`：数值计算
- `Pillow>=10.0.0`：图像处理
- `pytesseract>=0.3.10`：OCR 文本识别
- `matplotlib>=3.7.0`：Matplotlib 绘图
- `pandas>=2.0.0`：数据处理
- `python-dotenv>=1.0.0`：环境变量管理

### 验证器优化
- `scikit-learn>=1.3.0`：KMeans 聚类（渐变色检测）
- `scipy>=1.11.0`：多尺度 SSIM、Harris 角点检测

### ECharts 渲染
- `playwright>=1.40.0`：浏览器自动化

## 技术亮点

- **多模态模型驱动**：基于阿里云 Qwen-VL 系列模型
- **多轮迭代优化**：Agent1→2→3→4→验证器→迭代，直至通过
- **双语法输出**：支持 Matplotlib Python 和 ECharts JavaScript
- **多维验证**：颜色/文本/结构三维度 + VLM 评分
- **图表类型自适应**：根据图表类型动态调整权重和阈值
- **算法优化**：渐变色检测、自适应 BLEU、多尺度 SSIM

## 更新日志

### v1.1.0 (2026-04-20)
- ✨ 新增 ECharts 代码输出支持
- 🚀 验证器性能优化：渐变色检测、OCR 校正、自适应 BLEU
- 🚀 多尺度 SSIM + Harris 角点检测
- 🚀 VLM 评分校准机制
- 🔧 优化图表类型权重配置
- 📦 新增依赖：scikit-learn、scipy、playwright

### v1.0.0
- 初版发布
- 支持 Matplotlib 代码生成
- 多智能体流水线
- 多维验证器

## 许可证

MIT License
