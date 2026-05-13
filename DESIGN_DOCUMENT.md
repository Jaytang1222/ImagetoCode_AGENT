# 多智能体图表复现系统 - 设计文档

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 系统架构](#2-系统架构)
- [3. 代码规范](#3-代码规范)
- [4. 验证标准](#4-验证标准)
- [5. API 接口规范](#5-api-接口规范)
- [6. 数据流与状态管理](#6-数据流与状态管理)
- [7. 部署与运维](#7-部署与运维)

---

## 1. 项目概述

### 1.1 项目简介

**多智能体图表复现系统**是一个基于阿里云 DashScope（通义千问）API 的智能化图表生成平台。系统通过多智能体协作流水线，从参考图表图片出发，自动生成 ECharts JavaScript 代码，并通过视觉评判、代码评估与反馈修订实现多轮迭代优化，最终输出高保真度的图表复现代码。

### 1.2 核心功能

| 组件 | 职责 | 模型类型 | 默认模型 |
|------|------|----------|----------|
| **Agent 1** | 代码生成：读取参考图，生成 ECharts JS | VLM | `qwen-vl-max` |
| **Agent 2** | 视觉评判：对比原图与复现截图 | VLM | `qwen-vl-max` |
| **Agent 3** | 代码评估：分析代码质量与改进建议 | LLM | `qwen-plus` |
| **Agent 4** | 反馈修订：综合评估报告优化代码 | LLM | `qwen-plus` |
| **多维验证器** | 自动化打分：颜色/文本/结构一致性 | VLM + 算法 | `qwen-vl-max` |

### 1.3 技术栈

#### 后端
- **语言**: Python 3.9+
- **Web 框架**: Flask 3.0+
- **AI API**: DashScope SDK >= 1.14.0
- **浏览器自动化**: Playwright >= 1.40.0
- **图像处理**: Pillow >= 10.0.0, NumPy >= 1.24.0
- **OCR**: PyTesseract >= 0.3.10 + Tesseract OCR
- **跨域支持**: Flask-CORS >= 4.0.0

#### 前端
- **语言**: 原生 HTML5 + CSS3 + JavaScript (ES6+)
- **架构**: 单页应用 (SPA)
- **样式**: 自定义 CSS + 渐变背景 + 响应式设计
- **功能特性**: 
  - 拖拽上传与文件选择
  - 实时任务状态轮询
  - 进度条可视化
  - Agent 状态动态高亮
  - 代码预览与下载
  - 图表在线预览（iframe 模态框）
  - 历史记录查看与管理
  - **自动生成图片预览**: 任务完成后在上传区下方自动显示生成的 PNG 图片
  - **Python 代码查看**: 支持查看 `agent1_generated_matplotlib.py` 文件内容

---

## 2. 系统架构

### 2.1 总体架构图

```
graph TB
    User[用户] --> Frontend[前端界面]
    Frontend -->|HTTP REST API| Backend[Flask 后端]
    
    subgraph "后端服务层"
        Backend --> UploadHandler[文件上传处理器]
        Backend --> TaskManager[任务管理器]
        Backend --> StatusMonitor[状态监控器]
    end
    
    subgraph "多智能体流水线"
        TaskManager --> AgentPipeline[Agent Pipeline]
        AgentPipeline --> Agent1[Agent 1: 代码生成]
        Agent1 --> Renderer[ECharts 渲染器]
        Renderer --> Agent2[Agent 2: 视觉评判]
        Agent2 --> Agent3[Agent 3: 代码评估]
        Agent3 --> Agent4[Agent 4: 反馈修订]
        Agent4 --> Validator[多维验证器]
        Validator -->|未通过| Agent2
        Validator -->|通过| ResultStore[结果存储]
    end
    
    subgraph "外部依赖"
        Agent1 --> DashScope[DashScope API]
        Agent2 --> DashScope
        Agent3 --> DashScope
        Agent4 --> DashScope
        Validator --> DashScope
        Renderer --> Chromium[Playwright Chromium]
        Validator --> Tesseract[Tesseract OCR]
    end
    
    ResultStore --> FileSystem[文件系统 outputs/]
    StatusMonitor --> Frontend
```

### 2.2 目录结构

```
v2.1/
├── main.py                      # Flask 后端入口（含 API 路由）
├── web_app.py                   # 备用 Web 应用入口
├── agent_pipeline.py            # 多智能体流水线编排器
├── echarts_render.py            # ECharts 渲染与截图模块
├── requirements.txt             # Python 依赖清单
│
├── Agents/                      # 智能体模块
│   ├── agent1_code_generation.py       # Agent 1: 代码生成
│   ├── agent2_visual_judgment.py       # Agent 2: 视觉评判
│   ├── agent3_code_evaluation.py       # Agent 3: 代码评估
│   └── agent4_feedback_revision.py     # Agent 4: 反馈修订
│
├── Authenticator/               # 验证器模块
│   ├── __init__.py                     # 导出接口
│   ├── multidim_validator.py           # 多维验证器主逻辑
│   ├── color_consistency_validator.py  # 颜色一致性评估
│   ├── text_consistency_validator.py   # 文本一致性评估
│   └── structural_consistency_validator.py  # 结构一致性评估
│
├── utils/                       # 工具函数
│   ├── dashscope_api.py         # DashScope API 封装
│   └── matplotlib_render.py     # Matplotlib 渲染（历史遗留）
│
├── frontend/                    # 前端静态资源
│   └── index.html               # 单页应用主界面（原生 HTML/CSS/JS）
│
├── uploads/                     # 用户上传文件存储
├── outputs/                     # 任务输出目录
│   └── {timestamp}/             # 按时间戳组织的任务文件夹
│       ├── echarts_*.js         # 生成的 ECharts 代码
│       ├── preview.html         # 预览 HTML
│       ├── generated_chart.png  # 渲染截图
│       ├── report_agent2_*.txt  # Agent 2 报告
│       ├── report_agent3_*.txt  # Agent 3 报告
│       └── validator_round*.txt # 验证器报告
│
└── .env                         # 环境变量配置（不提交到 Git）
```

### 2.3 前端功能说明

当前前端采用原生 HTML/CSS/JavaScript 实现，主要功能模块包括：

#### 核心功能
- **文件上传**: 支持拖拽和点击选择，实时显示文件名与大小
- **上传图片即时预览**: 用户选择参考图片后，立即在上传区域容器内显示缩略图预览（基于 FileReader API，无需等待后端上传完成）
- **参数配置**: 可调整最大迭代轮数（1-10）和验证阈值（0-1）
- **任务状态监控**: 
  - 进度条实时更新（0-100%）
  - 状态消息动态显示（pending/running/completed/failed/error）
  - Agent 卡片高亮动画（active/completed 状态切换）
- **结果展示**:
  - 生成图表图片预览
  - ECharts 代码片段预览（前 500 字符）
  - 下载按钮组（代码/图片/在线预览）
  - **自动生成图片预览**: 任务完成后在上传区下方自动显示生成的 PNG 图片，支持放大查看和下载
- **历史记录**: 
  - 输出目录列表展示
  - 时间戳格式化显示
  - 文件大小统计
  - iframe 模态框预览 preview.html
  - **PNG 图片预览功能**:
    - 任务列表中的“预览图片”按钮
    - 图片模态框展示（居中显示，自适应窗口大小）
    - 用户手动关闭控制（无自动关闭）
    - 加载失败时显示友好占位图
  - **Python 代码查看功能**:
    - 任务列表中的“查看代码”按钮
    - 显示 `agent1_generated_matplotlib.py` 文件内容
    - 语法友好的代码展示界面
    - 支持错误提示和网络异常处理

#### UI 组件
- **上传区域** (`.upload-area`): 虚线边框 + 悬停/拖拽效果
- **进度条** (`.progress-bar`): 渐变填充 + 百分比文本
- **Agent 状态卡片** (`.agent-card`): 左侧彩色边框 + 脉冲动画
- **状态消息** (`.status-message`): 根据状态变色（黄/蓝/绿/红）
- **预览模态框** (`#previewModal`): 全屏遮罩 + iframe 嵌入
- **图片预览模态框** (`#imagePreviewModal`): 全屏遮罩 + `<img>` 标签展示 PNG 图表

#### 交互逻辑
```javascript
// 关键函数
handleFileSelect(file)          // 处理文件选择
showUploadedImagePreview(file)  // 显示上传图片即时预览（FileReader API）
startTask()                     // 创建任务并启动轮询
updateTaskStatus()              // 每 2 秒查询任务状态
updateAgentStatus(message)      // 根据消息高亮对应 Agent
showResults(task)               // 显示生成结果（根据任务状态动态更新标题和内容）
showGeneratedImageInUploadArea() // 在上传区下方显示生成的图片
openGeneratedImageModal()       // 打开生成图片的放大模态框
downloadGeneratedImage()        // 下载生成的 PNG 图片
loadTaskList()                  // 加载历史任务列表
viewOutputDetails(dirName)      // 查看 Python 代码文件
previewTaskImage(dirName)       // 预览任务生成的 PNG 图片
escapeHtml(text)                // HTML 转义工具函数
```

#### 技术特点
- ✅ 零依赖：无需构建工具，直接浏览器运行
- ✅ 响应式：适配移动端（@media 查询）
- ✅ 异步轮询：setInterval 定时查询后端 API
- ✅ 动态 DOM：通过 classList 切换实现状态可视化
- ✅ **状态预检**：下载前检查任务状态，避免无效请求和 404 错误
- ✅ **友好提示**：任务失败时显示错误信息，不尝试加载不存在的内容
- ✅ **手动控制**：图片预览模态框由用户主动关闭，无自动关闭逻辑
- ✅ **自动生成预览**：任务完成后在上传区下方自动显示生成的 PNG 图片
- ✅ **代码查看功能**：支持查看 Python 代码文件，带语法友好的展示界面
- ✅ **即时预览**：上传图片后立即显示缩略图，无需等待后端处理
- ⚠️ 局限性：无状态管理、无类型检查、无组件复用

---

## 3. 代码规范

### 3.1 通用编码规范

#### 3.1.1 文件头注释

所有 Python 文件必须在顶部包含 UTF-8 编码声明和模块说明：

```python
# -*- coding: utf-8 -*-
"""
模块简短描述（一行）。

详细说明（可选多行）：
- 功能概述
- 主要类/函数
- 使用示例
"""
```

#### 3.1.2 导入顺序

严格按照以下顺序组织导入语句：

```python
# 1. 标准库
from __future__ import annotations
import os
import sys
from typing import Optional, Tuple

# 2. 第三方库
import numpy as np
from PIL import Image
from flask import Flask, jsonify

# 3. 本地模块
from agent1_code_generation import agent1_generate_code
from utils.dashscope_api import call_vlm
```

#### 3.1.3 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块名 | `snake_case` | `agent_pipeline.py` |
| 类名 | `PascalCase` | `ColorConsistencyResult` |
| 函数/方法 | `snake_case` | `evaluate_color_consistency()` |
| 常量 | `UPPER_SNAKE_CASE` | `ECHARTS_CDN` |
| 变量 | `snake_case` | `chart_report` |
| 私有成员 | `_leading_underscore` | `_parse_validator_json()` |

#### 3.1.4 类型注解

所有公共函数必须添加类型注解：

```python
def multidimensional_validate(
    original_image_path: str,
    generated_image_path: str,
    threshold: float = 0.75,
    vlm_model: str = "qwen3.5-plus",
) -> Tuple[bool, float, str]:
    """返回 (是否通过, 分数 0~1, 简短说明)。"""
    pass
```

#### 3.1.5 文档字符串（Docstring）

使用 Google 风格或简洁的单行/多行 docstring：

```python
def agent1_generate_code(
    input_chart_image_path: str,
    extra_feedback: Optional[str] = None,
    vlm_model: str = "qwen3.5-plus",
) -> str:
    """
    根据输入图表生成 ECharts JavaScript 代码。
    
    Args:
        input_chart_image_path: 参考图表图片路径
        extra_feedback: 上一轮验证失败的补充说明（可选）
        vlm_model: 使用的 VLM 模型名称
    
    Returns:
        生成的 ECharts 内联 JS 代码字符串
    
    Raises:
        RuntimeError: 当 API 调用失败时
    """
    pass
```

### 3.2 智能体模块规范

#### 3.2.1 Agent 函数签名标准

所有 Agent 模块必须遵循统一的函数签名模式：

```python
def agent{N}_{function_name}(
    input_param1: Type1,
    input_param2: Type2,
    *,  # 关键字参数分隔符
    optional_param: Optional[Type] = None,
    model_name: str = "default_model",
) -> ReturnType:
    """
    Agent N - 功能描述
    
    输入：xxx
    输出：xxx
    模型：xxx
    """
    pass
```

**示例：**
```python
# Agent 1: 代码生成
def agent1_generate_code(
    input_chart_image_path: str,
    extra_feedback: Optional[str] = None,
    vlm_model: str = "qwen3.5-plus",
) -> str:
    pass

# Agent 2: 视觉评判
def agent2_chart_evaluation_report(
    original_image_path: str,
    generated_image_path: str,
    vlm_model: str = "qwen3.5-plus",
) -> str:
    pass

# Agent 3: 代码评估
def agent3_code_evaluation_report(
    echarts_inline_js: str,
    chart_evaluation_report: str,
    llm_model: str = "qwen-plus",
) -> str:
    pass

# Agent 4: 反馈修订
def agent4_feedback_optimize_code(
    echarts_inline_js: str,
    code_evaluation_report: str,
    chart_evaluation_report: str,
    llm_model: str = "qwen-plus",
) -> str:
    pass
```

#### 3.2.2 Prompt 设计规范

每个 Agent 必须定义清晰的 System Prompt 常量：

```python
SYSTEM_AGENT1 = """你是数据可视化专家...

硬性要求（必须遵守）：
1. ...
2. ...

示例输出结构：
```
// 代码示例
```"""
```

**Prompt 编写原则：**
- ✅ 明确角色定位（如"你是数据可视化专家"）
- ✅ 列出强制性规则（编号列表）
- ✅ 提供输出格式示例
- ✅ 指定边界条件（如"不要调用 plt.show()"）
- ❌ 避免模糊表述（如"尽量做到"）

#### 3.2.3 错误处理

所有外部 API 调用必须包裹异常处理：

```python
try:
    raw = call_vlm(messages, model=vlm_model)
except Exception as e:
    print(f"[Agent1] API 调用失败: {e}")
    raise RuntimeError(f"Agent1 生成代码失败: {e}") from e
```

### 3.3 验证器模块规范

#### 3.3.1 验证结果数据结构

所有验证器必须返回 `@dataclass` 定义的结果对象：

```python
@dataclass
class ColorConsistencyResult:
    """颜色一致性量化结果。"""
    score: float                      # 总分 0~1
    global_hist_score: float          # 全局直方图分数
    block_match_score: float          # 色块匹配分数
    hsv_score: float                  # HSV 距离分数
    hsv_distance: float               # HSV 原始距离
    grid_size: Tuple[int, int]        # 网格尺寸
    bins_per_channel: int             # 直方图 bin 数
    details: Dict[str, float]         # 详细参数
```

#### 3.3.2 验证函数签名

```python
def evaluate_{dimension}_consistency(
    original_image_path: str,
    generated_image_path: str,
    *,
    resize_to: Tuple[int, int] = (512, 512),
    weight_param1: float = 0.35,
    weight_param2: float = 0.45,
) -> DimensionConsistencyResult:
    """
    计算某维度一致性分数（0~1）。
    
    算法：
    1. xxx
    2. xxx
    """
    pass
```

#### 3.3.3 数值归一化

所有评分必须在 `[0.0, 1.0]` 范围内：

```python
def _clamp01(v: float) -> float:
    """将数值限制在 [0, 1] 区间。"""
    return max(0.0, min(1.0, float(v)))
```

### 3.4 渲染模块规范

#### 3.4.1 HTML 模板

ECharts HTML 模板必须包含：
- CDN 引入 ECharts 库
- 固定容器 `#main`
- 明确的宽高设置

```python
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <script src="{cdn}"></script>
  <style>html,body{{margin:0;padding:0;background:#fff;}}</style>
</head>
<body>
  <div id="main" style="width:{w}px;height:{h}px;"></div>
  <script>
{script}
  </script>
</body>
</html>
"""
```

#### 3.4.2 Playwright 截图配置

```python
def screenshot_html_to_png(
    html_path: str,
    out_png: str,
    viewport_width: int = 920,
    viewport_height: int = 640,
    wait_ms: int = 2500,  # 等待 ECharts 渲染完成
) -> Optional[str]:
    """
    使用 Playwright Chromium 对本地 HTML 截图。
    
    Returns:
        PNG 文件路径，失败返回 None
    """
    pass
```

### 3.5 Flask API 规范

#### 3.5.1 路由定义

所有 API 端点必须以 `/api/` 为前缀：

```python
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传参考图片并创建任务。"""
    pass

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态。"""
    pass
```

#### 3.5.2 响应格式

统一 JSON 响应结构：

**成功响应：**
```json
{
    "task_id": "uuid-string",
    "message": "任务已创建",
    "data": {
        "field1": "value1",
        "field2": "value2"
    }
}
```

**错误响应：**
```json
{
    "error": "错误描述信息",
    "code": 400
}
```

#### 3.5.3 状态码规范

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 任务创建成功 |
| 400 | Bad Request | 参数错误或文件格式不支持 |
| 404 | Not Found | 任务或文件不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

### 3.6 日志规范

#### 3.6.1 控制台日志

使用统一的日志格式：

```python
print(f"[Agent1] 代码生成(VLM)…")
print(f"[渲染] 生成预览 HTML / 截图 → {gen_png}")
print(f"[错误] {error_message}")
print(f"  → score={score:.4f} pass={ok} | {summary}")
```

**日志级别标识：**
- `[Agent1]`, `[Agent2]`... : 正常流程
- `[渲染]`, `[验证器]` : 子系统操作
- `[错误]` : 错误信息
- `[完成]`, `[结束]` : 流程终止

#### 3.6.2 文件日志

每轮迭代的报告必须保存到文件：

```python
Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
    chart_report, encoding="utf-8"
)
```

**文件命名规范：**
- Agent 报告：`report_agent{N}_round{M}.txt`
- 验证器报告：`validator_round{M}.txt`
- 代码备份：`current_echarts_after_agent4_r{M}.js`

### 3.7 环境变量管理规范

#### 3.7.1 配置加载机制

项目使用 `python-dotenv` 库自动加载 `.env` 文件中的环境变量：

```python
from dotenv import load_dotenv
import os

# 在模块顶部加载
load_dotenv()

# 读取配置
tesseract_cmd = os.getenv("TESSERACT_CMD")
if tesseract_cmd:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
```

**关键原则：**
- ✅ 所有敏感信息（API Key、路径配置）必须通过 `.env` 文件管理
- ✅ `.env` 文件已加入 `.gitignore`，不会提交到版本控制
- ✅ 提供 `.env.example` 作为配置模板（可选）
- ❌ 禁止在代码中硬编码绝对路径或密钥

#### 3.7.2 Anaconda 虚拟环境注意事项

**问题背景：**
Anaconda 虚拟环境激活时会创建独立的 PATH 环境变量，不会自动继承系统的所有 PATH 设置。这导致即使系统在 PowerShell/CMD 中能识别某个命令，虚拟环境中也可能找不到。

**解决方案对比：**

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| `.env` 文件配置 | 无需修改系统配置，项目可移植 | 仅限 Python 代码内使用 | ⭐⭐⭐⭐⭐ |
| 虚拟环境激活脚本 | 命令行也能使用 | 配置复杂，不易迁移 | ⭐⭐⭐ |
| 系统环境变量 | 全局生效 | 影响所有环境，不灵活 | ⭐⭐ |

**最佳实践：**
始终使用 `.env` 文件配置外部工具路径，确保代码在不同环境中的一致性。

---

## 4. 验证标准

### 4.1 多维验证体系

验证器采用 **VLM + 算法融合** 的混合评估策略，综合四个维度：

| 维度 | 权重（动态调整） | 评估方法 | 分值范围 |
|------|------------------|----------|----------|
| **VLM 视觉评分** | 0.30 ~ 0.40 | 多模态模型对比原图与复现图 | 0.0 ~ 1.0 |
| **颜色一致性** | 0.15 ~ 0.40 | 直方图 + 色块匹配 + HSV 距离 | 0.0 ~ 1.0 |
| **文本一致性** | 0.15 ~ 0.20 | OCR + BLEU + 空间布局偏差 | 0.0 ~ 1.0 |
| **结构一致性** | 0.15 ~ 0.30 | SSIM + 拓扑关系（距离/角度） | 0.0 ~ 1.0 |

### 4.2 图表类型自适应策略

系统自动识别图表类型并调整权重与阈值：

```python
policies = {
    "line": {
        "delta": 0.03,  # 阈值调整量
        "weights": {"vlm": 0.35, "color": 0.15, "text": 0.20, "struct": 0.30},
    },
    "bar": {
        "delta": 0.02,
        "weights": {"vlm": 0.35, "color": 0.20, "text": 0.20, "struct": 0.25},
    },
    "pie": {
        "delta": -0.01,  # 饼图降低阈值（颜色更重要）
        "weights": {"vlm": 0.30, "color": 0.35, "text": 0.20, "struct": 0.15},
    },
    "heatmap": {
        "delta": 0.00,
        "weights": {"vlm": 0.30, "color": 0.40, "text": 0.15, "struct": 0.15},
    },
    # ... 其他类型
}
```

**动态阈值计算：**
```python
dynamic_threshold = max(0.0, min(1.0, base_threshold + delta))
```

### 4.3 颜色一致性评估标准

#### 4.3.1 评估维度

| 子维度 | 权重 | 算法 | 说明 |
|--------|------|------|------|
| 全局直方图 | 0.35 | RGB 直方图交集相似度 | 整体色彩风格匹配度 |
| 色块匹配 | 0.45 | 8×8 网格分块直方图 | 局部区域颜色精度 |
| HSV 距离 | 0.20 | 加权 HSV 均方根误差 | 色调/饱和度/亮度差异 |

#### 4.3.2 评分公式

```python
final_score = (
    global_hist_score * 0.35 +
    block_match_score * 0.45 +
    hsv_score * 0.20
)
```

**HSV 距离公式：**
```
D_HSV = sqrt(WH*(ΔH)² + WS*(ΔS)² + WV*(ΔV)²) / sqrt(WH + WS + WV)
score = 1.0 - D_HSV
```

其中：
- `WH = 2.0`（色调权重更高）
- `WS = 1.0`（饱和度权重）
- `WV = 1.0`（亮度权重）

#### 4.3.3 合格标准

- **优秀**: `score >= 0.85`
- **良好**: `0.70 <= score < 0.85`
- **及格**: `0.60 <= score < 0.70`
- **不合格**: `score < 0.60`

### 4.4 文本一致性评估标准

#### 4.4.1 评估维度

| 子维度 | 权重 | 算法 | 说明 |
|--------|------|------|------|
| 内容一致性 | 0.55 | BLEU-4 + 序列匹配 | 文本内容准确性 |
| 布局一致性 | 0.30 | 中心点坐标偏差 + 尺寸偏差 | 文本位置还原度 |
| 覆盖率 | 0.15 | 匹配文本块比例 | 参考图文本覆盖程度 |

#### 4.4.2 BLEU 评分

使用字符级 BLEU-4（适合中英文混合）：

```python
BLEU = BP * exp(Σ w_n * log(Precision_n))

BP = {
    1.0,                          if hyp_len > ref_len
    exp(1 - ref_len/hyp_len),     otherwise
}
```

**参数配置：**
- `max_bleu_n = 4`（1-gram 到 4-gram）
- `min_match_similarity = 0.25`（最低匹配阈值）

#### 4.4.3 布局偏差计算

```python
center_dist = sqrt((cx_ref - cx_gen)² + (cy_ref - cy_gen)²) / sqrt(2)
area_diff = |area_ref - area_gen|
layout_error = 0.75 * center_dist + 0.25 * min(area_diff * 4.0, 1.0)
layout_score = 1.0 - layout_error
```

#### 4.4.4 合格标准

- **优秀**: `score >= 0.90`（文本完全一致且位置精准）
- **良好**: `0.75 <= score < 0.90`
- **及格**: `0.60 <= score < 0.75`
- **不合格**: `score < 0.60`

### 4.5 结构一致性评估标准

#### 4.5.1 评估维度

| 子维度 | 权重 | 算法 | 说明 |
|--------|------|------|------|
| SSIM | 0.45 | 结构相似性指数 | 亮度/对比度/结构综合 |
| 拓扑一致性 | 0.55 | 关键点距离 + 角度关系 | 几何布局还原度 |

#### 4.5.2 SSIM 公式

```
SSIM(x,y) = [l(x,y)]^α * [c(x,y)]^β * [s(x,y)]^γ

其中 α=β=γ=1 时：
SSIM = (2μ_xμ_y + C₁)(2σ_xy + C₂) / ((μ_x² + μ_y² + C₁)(σ_x² + σ_y² + C₂))

C₁ = (0.01)², C₂ = (0.03)²
```

#### 4.5.3 拓扑一致性

提取关键结构元素（边缘检测 + 连通域分析），计算：

**距离一致性：**
```python
dist_err = |d_ref - d_gen| / max(d_ref, d_gen)
distance_consistency = 1.0 - mean(dist_err)
```

**角度一致性：**
```python
angle_err = |θ_ref - θ_gen| / π
angle_consistency = 1.0 - mean(angle_err)
```

**拓扑总分：**
```python
topology_score = 0.6 * distance_consistency + 0.4 * angle_consistency
```

#### 4.5.4 合格标准

- **优秀**: `score >= 0.85`
- **良好**: `0.70 <= score < 0.85`
- **及格**: `0.55 <= score < 0.70`
- **不合格**: `score < 0.55`

### 4.6 综合评分与通过判定

#### 4.6.1 最终得分计算

```python
final_score = (
    weights["vlm"] * vlm_score +
    weights["color"] * color_score +
    weights["text"] * text_score +
    weights["struct"] * struct_score
)
```

#### 4.6.2 通过条件

```python
passed = final_score >= dynamic_threshold
```

**默认阈值：**
- 命令行参数：`--threshold 0.75`
- 动态调整后范围：`[0.74, 0.78]`（根据图表类型）

#### 4.6.3 迭代终止条件

满足以下任一条件即终止：
1. ✅ **验证通过**: `final_score >= dynamic_threshold`
2. ⚠️ **达到最大轮数**: `loop >= max_loops`（默认 5 轮）
3. ❌ **致命错误**: 渲染失败或 API 调用异常

### 4.7 验证报告格式

每轮验证生成标准化报告文件 `validator_round{N}.txt`：

```
pass=True
score=0.8234
type=line, thr=0.780, w(vlm=0.35,color=0.15,text=0.20,struct=0.30) | 
复现图与参考图在趋势和整体观感上高度一致 | 
color=0.789(global=0.812, block=0.756, hsv=0.801) | 
text=0.845(bleu=0.823, layout=0.867, cov=0.900) | 
struct=0.812(ssim=0.798, topo=0.825, dist=0.834, ang=0.816) | 
final=0.823
```

**字段说明：**
- `pass`: 布尔值，是否通过验证
- `score`: 最终综合得分
- `type`: 识别的图表类型
- `thr`: 动态阈值
- `w(...)`: 各维度权重
- `color/text/struct`: 各维度详细得分
- `final`: 最终得分（与 score 相同）

---

## 5. API 接口规范

### 5.1 文件上传接口

#### 5.1.1 创建任务

**端点：** `POST /api/upload`

**请求：**
- Content-Type: `multipart/form-data`
- 参数：
  - `file`: 图片文件（PNG/JPG，最大 16MB）
  - `max_loops`: 最大迭代轮数（可选，默认 5）
  - `threshold`: 验证阈值（可选，默认 0.75）

**响应：**
```json
{
    "task_id": "a215fee9-df52-3334-0252-adb631ac9872",
    "message": "任务已创建"
}
```

**错误响应：**
```json
{
    "error": "不支持的文件格式，请上传 PNG 或 JPG 图片"
}
```

### 5.2 任务状态查询

#### 5.2.1 获取单个任务状态

**端点：** `GET /api/tasks/{task_id}`

**响应：**
```json
{
    "id": "a215fee9-df52-3334-0252-adb631ac9872",
    "status": "running",
    "progress": 65,
    "message": "[Agent4] 反馈优化中...",
    "input_file": "/path/to/uploads/20260419_120000_input.png",
    "created_at": "2026-04-19T12:00:00",
    "updated_at": "2026-04-19T12:03:45",
    "params": {
        "max_loops": 5,
        "threshold": 0.75
    },
    "data": {}
}
```

**状态枚举：**
- `pending`: 等待启动
- `running`: 执行中
- `completed`: 成功完成
- `failed`: 验证未通过（达到最大轮数）
- `error`: 执行出错

**进度说明：**
- 0-5%: 初始化
- 5-15%: Agent1 代码生成
- 15-30%: 首次渲染
- 30-50%: Agent2 视觉评判
- 50-65%: Agent3 代码评估
- 65-80%: Agent4 反馈修订
- 80-90%: Agent4 后再渲染
- 90-100%: 多维验证器

#### 5.2.2 列出所有任务

**端点：** `GET /api/tasks`

**响应：**
```json
[
    {
        "id": "task-uuid-1",
        "status": "completed",
        "progress": 100,
        "message": "验证通过！",
        "created_at": "2026-04-19T11:00:00",
        ...
    },
    {
        "id": "task-uuid-2",
        "status": "running",
        "progress": 45,
        ...
    }
]
```

### 5.3 结果下载接口

#### 5.3.1 下载生成的代码

**端点：** `GET /api/download/code/{task_id}`

**响应：**
- Content-Type: `application/javascript`
- 文件名: `echarts_code.js`

#### 5.3.2 下载生成的图表

**端点：** `GET /api/download/image/{task_id}`

**响应：**
- Content-Type: `image/png`
- 文件名: `generated_chart.png`

**端点：** `GET /api/download/image/dir/{dir_name}`

**说明：** 通过输出目录名直接获取图片（用于历史任务预览）

**响应：**
- Content-Type: `image/png`
- 优先返回 `generated_chart.png`，如不存在则返回第一个 PNG 文件
- 错误响应：`{ "error": "图片文件不存在" }` (404)

#### 5.3.3 在线预览 HTML

**端点：** `GET /api/preview/{task_id}`

**响应：**
- Content-Type: `text/html`
- 直接在浏览器中渲染 ECharts 图表

**端点：** `GET /api/preview/dir/{dir_name}`

**说明：** 通过输出目录名直接预览（用于历史记录查看）

### 5.4 Python 代码查看接口

**端点：** `GET /api/code/dir/{dir_name}`

**说明：** 通过输出目录名获取 Python 代码文件内容

**响应：**
```json
{
    "success": true,
    "filename": "agent1_generated_matplotlib.py",
    "content": "# Python 代码内容..."
}
```

**错误响应：**
```json
{
    "error": "代码文件不存在"
}
```

**实现逻辑：**
1. 安全检查：防止路径遍历攻击
2. 优先查找 `agent1_generated_matplotlib.py` 文件
3. 如果不存在，返回第一个 `.py` 文件
4. 以 JSON 格式返回文件内容

### 5.5 历史记录接口

**端点：** `GET /api/outputs`

**响应：**
```json
[
    {
        "name": "20260419_120000",
        "path": "/path/to/outputs/20260419_120000",
        "created_time": "2026-04-19T12:00:00",
        "modified_time": "2026-04-19T12:05:30",
        "size": 1234567
    }
]
```

### 5.6 健康检查接口

**端点：** `GET /health`

**响应：**
```json
{
    "status": "ok",
    "timestamp": "2026-04-19T12:00:00",
    "active_tasks": 3
}
```

---

## 6. 数据流与状态管理

### 6.1 任务生命周期

```
stateDiagram-v2
    [*] --> pending: 创建任务
    pending --> running: 后台线程启动
    running --> completed: 验证通过
    running --> failed: 达到最大轮数
    running --> error: 发生异常
    completed --> [*]
    failed --> [*]
    error --> [*]
```

### 6.2 任务状态数据结构

```python
task = {
    'id': str,                  # UUID
    'status': str,              # pending/running/completed/failed/error
    'progress': int,            # 0-100
    'message': str,             # 当前步骤描述
    'input_file': str,          # 上传文件路径
    'created_at': str,          # ISO 8601 时间戳
    'updated_at': str,          # 最后更新时间
    'params': {
        'max_loops': int,
        'threshold': float
    },
    'data': {
        'code_path': str,       # 最终代码路径
        'png_path': str,        # 最终渲染图路径
        'summary': str,         # 验证摘要
        'html_preview': str     # 预览 HTML 路径
    }
}
```

### 6.3 并发控制

**当前实现：**
- 任务状态存储在内存字典 `tasks: Dict[str, dict]`
- 每个任务在独立后台线程中执行
- 无任务数量限制（生产环境需添加队列）

**注意事项：**
- ⚠️ 重启服务会丢失所有任务状态
- ⚠️ 大量并发任务可能导致内存溢出
- ⚠️ 无用户隔离，所有任务公开可见

### 6.4 文件管理规范

#### 6.4.1 上传文件

- 存储路径：`uploads/{timestamp}_{filename}`
- 命名规则：时间戳 + 原始文件名（防止冲突）
- 清理策略：手动清理（生产环境建议定期清理）

#### 6.4.2 输出文件

- 存储路径：`outputs/{timestamp}/`
- 目录命名：任务启动时的时间戳（格式：`YYYYMMDD_HHMMSS`）
- 文件保留：永久保留（生产环境建议归档或删除旧任务）

---

## 7. 部署与运维

### 7.1 环境配置

#### 7.1.1 环境变量

创建 `.env` 文件（不提交到 Git）：

```bash
# DashScope API Key（必需）
DASHSCOPE_API_KEY=sk-your-api-key-here

# Tesseract OCR 路径（Windows 需要，Linux/Mac 可选）
# ⚠️ 重要：Anaconda 虚拟环境不会自动继承系统 PATH，必须在此配置
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

**为什么需要配置 `TESSERACT_CMD`？**

在 Windows 系统中，即使已在系统环境变量中添加了 Tesseract 路径，Anaconda 虚拟环境激活时会创建独立的 PATH 环境变量，导致 Python 代码无法找到 tesseract.exe。

**解决方案：**
- ✅ **推荐**：在项目根目录的 `.env` 文件中配置 `TESSERACT_CMD`（如上所示）
- 代码会自动通过 `python-dotenv` 加载该配置（见 `Authenticator/text_consistency_validator.py` 第 26-28 行）
- 此方案无需修改系统或虚拟环境变量，项目可移植性强

#### 7.1.2 依赖安装

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器内核
playwright install chromium

# 3. 安装 Tesseract OCR（用于文本一致性验证）
# Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki
#   - 建议安装路径: C:\Program Files\Tesseract-OCR
#   - ⚠️ 必须在 .env 文件中配置 TESSERACT_CMD（见 7.1.1 节）
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 4. 验证 Tesseract 配置
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Tesseract:', os.getenv('TESSERACT_CMD'))"
```

### 7.2 启动服务

#### 7.2.1 开发模式

```bash
python main.py
```

- 默认端口：5000
- 访问地址：http://localhost:5000
- 调试模式：启用（自动重载）

#### 7.2.2 生产模式

使用 Gunicorn：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

**参数说明：**
- `-w 4`: 4 个工作进程
- `-b 0.0.0.0:5000`: 绑定所有网卡

### 7.3 性能优化建议

#### 7.3.1 短期优化

1. **任务持久化**
   - 使用 Redis 缓存任务状态
   - 使用 PostgreSQL/MySQL 存储历史记录

2. **实时推送**
   - 替换轮询为 WebSocket（Flask-SocketIO）
   - 降低前端查询频率

3. **异步任务队列**
   - 使用 Celery + Redis/RabbitMQ
   - 支持任务优先级和重试机制

#### 7.3.2 长期规划

1. **负载均衡**
   - 使用 Nginx 反向代理
   - 多实例部署 + 会话保持

2. **监控告警**
   - 集成 Prometheus + Grafana
   - API 响应时间、错误率监控

3. **安全加固**
   - 添加用户认证（JWT/OAuth2）
   - 启用 HTTPS
   - 速率限制（Flask-Limiter）
   - 文件上传病毒扫描

### 7.4 常见问题排查

#### 7.4.1 API 调用失败

**症状：** `DASHSCOPE_API_KEY not found`

**解决：**
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY = "sk-xxx"

# Linux/Mac
export DASHSCOPE_API_KEY="sk-xxx"
```

#### 7.4.2 截图失败

**症状：** `无法生成复现图 PNG`

**解决：**
```bash
# 确认 Playwright 已安装
pip install playwright
playwright install chromium

# 测试截图功能
python -c "from echarts_render import render_echarts_js_to_png; print('OK')"
```

#### 7.4.3 OCR 识别率低或找不到 Tesseract

**症状 1：** `tesseract is not installed or it's not in your PATH`

**原因：** Anaconda 虚拟环境未正确配置 Tesseract 路径

**解决：**
1. 确认项目根目录存在 `.env` 文件
2. 检查 `.env` 中是否包含：
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
   ```
3. 验证配置是否生效：
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   tesseract_cmd = os.getenv("TESSERACT_CMD")
   print(f"Tesseract 路径: {tesseract_cmd}")
   
   if tesseract_cmd and os.path.exists(tesseract_cmd):
       print("✅ 配置正确")
   else:
       print("❌ 配置错误")
   ```

**症状 2：** 文本一致性分数偏低

**解决：**
1. 确认 Tesseract 已正确安装且版本 >= 5.0
2. 检查 `.env` 中 `TESSERACT_CMD` 路径是否正确
3. 安装中文语言包：下载 `chi_sim.traineddata` 放到 `tessdata` 目录
4. 调整图像预处理参数（对比度、二值化阈值）
5. 确保参考图清晰度足够（建议分辨率 >= 300 DPI）

#### 7.4.4 验证分数不稳定

**原因：** 多模态模型输出存在随机性

**解决：**
- 提高 `--threshold` 阈值（如 0.80）
- 增加 `--max-loops` 迭代轮数（如 8）
- 多次运行取最佳结果

### 7.5 日志与监控

#### 7.5.1 控制台日志

服务运行时实时输出：
```
==================== 第 1/5 轮 ====================
[Agent1] 代码生成(VLM)…
[渲染] 生成预览 HTML / 截图 → outputs/generated_chart.png
[Agent2] 视觉评判(双图 VLM)…
[Agent3] 代码评判(LLM)…
[Agent4] 反馈优化修订(LLM)…
[渲染] Agent4 输出再截图…
[多维验证器] 对比原图与复现图…
  → score=0.8234 pass=True | type=line, thr=0.780, ...
[完成] 验证通过，最终代码已写入: outputs/current_echarts.js
```

#### 7.5.2 文件日志

每轮迭代生成详细报告：
- `outputs/report_agent2_round1.txt`
- `outputs/report_agent3_round1.txt`
- `outputs/validator_round1.txt`

#### 7.5.3 健康检查

```bash
curl http://localhost:5000/health
```

响应示例：
```json
{
    "status": "ok",
    "timestamp": "2026-04-19T12:00:00",
    "active_tasks": 3
}
```

---

## 附录 A：版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.1 | 2026-04-25 | **新增功能**：<br>1. 上传图片即时预览：用户选择参考图片后，立即在上传区域容器内显示缩略图预览（基于 FileReader API，无需等待后端上传完成）<br>2. 自动生成图片预览：任务完成后在上传区下方自动显示生成的 PNG 图片，支持放大查看和下载<br>3. Python 代码查看功能：支持查看 `agent1_generated_matplotlib.py` 文件内容，带语法友好的展示界面<br>4. 新增 API 接口 `/api/code/dir/{dir_name}` 用于获取 Python 代码<br>**优化**：<br>- 模态框标题动态更新，区分不同预览类型<br>- HTML 转义工具函数防止 XSS 攻击<br>- 淡入动画提升用户体验<br>- 修复生成图片预览的 URL 拼接问题 |
| v2.1 | 2026-04-25 | 添加 PNG 图片预览功能、优化前端错误处理与状态管理、添加 scipy 依赖、改进任务失败时的用户提示 |
| v2.1 | 2026-04-25 | 添加 Tesseract OCR 在 Anaconda 虚拟环境中的配置说明、环境变量管理规范 |
| v2.1 | 2026-04-09 | 添加 Flask Web 服务、前端界面、历史记录查看、在线预览 |
| v2.0 | 2026-04-01 | 重构为 ECharts + Playwright 方案，替换 Matplotlib |
| v1.0 | - | 初始版本（Matplotlib 方案） |

## 附录 B：参考文献

1. [DashScope API 文档](https://help.aliyun.com/zh/dashscope/)
2. [ECharts 官方文档](https://echarts.apache.org/)
3. [Playwright Python API](https://playwright.dev/python/)
4. [BLEU 评分算法](https://aclanthology.org/P02-1040/)
5. [SSIM 结构相似性](https://ece.uwaterloo.ca/~z70wang/publications/ssim.pdf)

## 附录 C：贡献指南

### 代码提交规范

```bash
git commit -m "feat: 添加新的验证维度"
git commit -m "fix: 修复 Agent2 视觉评判 bug"
git commit -m "docs: 更新 API 文档"
git commit -m "refactor: 重构验证器模块"
```

**提交类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### Pull Request 流程

1. Fork 仓库
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交更改：`git commit -am 'feat: add xxx'`
4. 推送分支：`git push origin feature/xxx`
5. 提交 PR

---

**文档版本**: v2.1  
**最后更新**: 2026-04-25  
**维护者**: 多智能体图表复现系统开发团队
