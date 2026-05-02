# 多智能体图表复现系统

基于阿里云 DashScope API 的多智能体流水线，从参考图表自动生成 Matplotlib 代码，通过多轮迭代优化实现高质量图表复现。支持命令行和 Web 界面两种使用方式。

## 系统特性

- **多智能体协作**：Agent1（代码生成）→ Agent2（视觉评估）→ Agent3（代码分析）→ Agent4（反馈修订）
- **多维验证器**：融合颜色、文本、结构一致性和 VLM 感知的综合评分系统
- **Web 可视化界面**：实时查看流水线进度、历史记录和对比结果
- **命令行工具**：支持批量处理和自动化集成

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+（仅 Web 界面需要）
- 阿里云 DashScope API Key
- Tesseract OCR

### 安装步骤

#### 1. 安装 Python 依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装后端依赖（仅 Web 界面需要）
pip install -r backend/requirements.txt
```

#### 2. 安装 Tesseract OCR

下载并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)，记录安装路径备用。

#### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_api_key_here
TESSERACT_CMD=your_tesseract_path_here
```

**Windows 示例**：
```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Linux/Mac 示例**：
```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
TESSERACT_CMD=/usr/bin/tesseract
```

#### 4. 安装前端依赖（仅 Web 界面需要）

```bash
cd frontend
npm install
cd ..
```

## 使用方式

### 方式一：命令行工具

适合批量处理和自动化集成。

```bash
python scripts/cli.py -i data/test.png -o storage/outputs --max-loops 5 --threshold 0.75
```

**命令行参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i` / `--input` | 输入参考图路径 | `input.png` |
| `-o` / `--out` | 输出目录 | `outputs` |
| `--max-loops` | 最大迭代轮数 | `5` |
| `--threshold` | 验证通过阈值（0~1） | `0.75` |

**输出文件**：
- `current_matplotlib.py`：生成的 Matplotlib 代码
- `generated_chart.png`：渲染截图
- `report_agent2_*.txt`：视觉评估报告
- `report_agent3_*.txt`：代码分析报告
- `validator_round*.txt`：验证结果

### 方式二：Web 界面

提供可视化操作界面，实时查看流水线进度。

#### 启动后端服务

```bash
python scripts/start_service.py
```

后端服务将在 `http://localhost:8000` 启动，同时前端界面将在 `http://localhost:5173` 启动。

API 文档访问 `http://localhost:8000/docs`。

#### 使用 Web 界面

1. 打开浏览器访问 `http://localhost:5173`
2. 上传参考图表图片
3. 配置流水线参数（最大轮数、阈值等）
4. 点击"开始生成"启动流水线
5. 实时查看各 Agent 执行状态和进度
6. 查看生成结果和对比效果
7. 下载生成的代码和图表

## 工作流程

```
参考图 → Agent1(生成代码) → 渲染截图 → Agent2(视觉评估) 
       → Agent3(代码分析) → Agent4(修订代码) → 多维验证器
       → 未通过则进入下一轮迭代（最多 max_loops 轮）
```

## 多维验证器

融合四个维度评估图表一致性：

1. **颜色一致性**：RGB 直方图 + 网格色块匹配 + HSV 距离
2. **文本一致性**：OCR + BLEU 评分 + 布局偏差
3. **结构一致性**：SSIM + 空间拓扑关系
4. **VLM 感知**：语义和整体观感补充

支持图表类型自适应，动态调整权重和阈值。

## 项目结构

```
.
├── src/                     # 核心源代码
│   ├── agents/              # 四个智能体实现
│   │   ├── agent1_code_generation.py
│   │   ├── agent2_visual_judgment.py
│   │   ├── agent3_code_evaluation.py
│   │   ├── agent4_feedback_revision.py
│   │   └── pipeline.py      # 流水线编排
│   ├── validators/          # 多维验证器
│   │   ├── color_consistency_validator.py
│   │   ├── text_consistency_validator.py
│   │   ├── structural_consistency_validator.py
│   │   └── multidim_validator.py
│   └── utils/               # 工具函数
│       ├── dashscope_api.py
│       └── matplotlib_render.py
├── backend/                 # FastAPI 后端服务
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   ├── websocket/           # WebSocket 管理
│   └── main.py              # 后端入口
├── frontend/                # Vue 3 前端界面
│   ├── src/
│   │   ├── components/      # UI 组件
│   │   ├── services/        # API 服务
│   │   └── stores/          # 状态管理
│   └── package.json
├── scripts/                 # 脚本工具
│   ├── start_service.py     # 启动服务
│   ├── restart_service.py   # 重启服务
│   └── cli.py               # 命令行工具
├── storage/                 # 运行时存储
│   ├── uploads/             # 上传文件
│   └── outputs/             # 输出结果
├── logs/                    # 日志文件
├── data/                    # 测试数据
├── requirements.txt         # Python 依赖
└── .env                     # 环境变量配置
```

## 常见问题

### 1. Tesseract OCR 找不到

确保已正确安装 Tesseract 并在 `.env` 文件中配置了正确的路径。

### 2. API Key 无效

检查 `.env` 文件中的 `DASHSCOPE_API_KEY` 是否正确，确保有足够的配额。

### 3. 前端无法连接后端

确保后端服务已启动（`http://localhost:8000`），检查防火墙设置。

### 4. 生成的图表不准确

尝试增加 `--max-loops` 参数值，或降低 `--threshold` 阈值。

## 技术栈

**后端**：
- FastAPI - Web 框架
- DashScope - 阿里云多模态 AI 服务
- Matplotlib - 图表渲染
- Pytesseract - OCR 文本识别

**前端**：
- Vue 3 - 前端框架
- Vite - 构建工具
- Pinia - 状态管理
- WebSocket - 实时通信
