# 多智能体图表复现系统

基于多模态大模型的智能图表复现系统，通过多智能体协作自动生成高质量的 Matplotlib 代码。

## 核心特性

- 多智能体协作流水线：代码生成 → 视觉评估 → 代码分析 → 反馈修订
- 多维度验证系统：颜色、文本、结构一致性和视觉感知综合评分
- 多模型支持：通义千问、OpenAI GPT、Google Gemini、字节豆包
- Web 可视化界面：实时查看流水线进度和对比结果
- 命令行工具：支持批量处理和自动化集成

## 快速部署

### 环境要求

- Python 3.9+
- Node.js 16+（Web 界面需要）
- Tesseract OCR
- 至少一个大模型 API Key

### 1. 克隆项目

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. 安装 Python 依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装后端依赖（Web 界面需要）
pip install -r backend/requirements.txt
```

### 3. 安装 Tesseract OCR

**Windows**:
- 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
- 记录安装路径（如 `C:\Program Files\Tesseract-OCR\tesseract.exe`）

**Linux**:
```bash
sudo apt-get install tesseract-ocr
```

**macOS**:
```bash
brew install tesseract
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# 选择模型提供商 (qwen, openai, gemini, doubao)
MODEL_PROVIDER=qwen

# 配置对应的 API Key（至少配置一个）
QWEN_API_KEY=your_qwen_api_key
# OPENAI_API_KEY=your_openai_api_key
# GEMINI_API_KEY=your_gemini_api_key
# DOUBAO_API_KEY=your_doubao_api_key

# Tesseract 路径
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows
# TESSERACT_CMD=/usr/bin/tesseract  # Linux/macOS

# 服务器配置（可选）
SERVER_HOST=localhost
SERVER_PORT=8001
```

### 5. 安装前端依赖（Web 界面）

```bash
cd frontend
npm install
cd ..
```

## 使用方式

### 方式一：Web 界面（推荐）

启动服务：

```bash
python scripts/start_service.py
```

服务启动后：
- 后端 API：http://localhost:8001
- 前端界面：http://localhost:5174
- API 文档：http://localhost:8001/docs

使用步骤：
1. 打开浏览器访问前端地址
2. 上传参考图表图片
3. 配置参数（最大迭代轮数、验证阈值）
4. 启动流水线并实时查看进度
5. 查看结果对比和下载生成的代码

### 方式二：命令行工具

适合批量处理和自动化场景：

```bash
python scripts/cli.py -i input.png -o outputs --max-loops 5 --threshold 0.75
```

参数说明：
- `-i, --input`：输入参考图路径
- `-o, --out`：输出目录
- `--max-loops`：最大迭代轮数（默认 5）
- `--threshold`：验证通过阈值 0-1（默认 0.75）

输出文件：
- `current_matplotlib.py`：生成的代码
- `generated_chart.png`：渲染结果
- `report_agent2_*.txt`：视觉评估报告
- `report_agent3_*.txt`：代码分析报告
- `validator_round*.json`：验证结果

## 工作原理

```
参考图 → Agent1(代码生成) → 渲染 → Agent2(视觉评估)
       → Agent3(代码分析) → Agent4(反馈修订) → 多维验证
       → 未通过则迭代（最多 max_loops 轮）
```

多维验证器融合四个维度：
1. 颜色一致性：RGB 直方图和色块匹配
2. 文本一致性：OCR + BLEU 评分
3. 结构一致性：SSIM + 空间拓扑
4. VLM 感知：语义和整体观感

## 项目结构

```
.
├── src/                    # 核心源代码
│   ├── agents/             # 四个智能体
│   ├── validators/         # 多维验证器
│   └── utils/              # 工具函数
├── backend/                # FastAPI 后端
│   ├── api/                # API 路由
│   ├── services/           # 业务逻辑
│   └── websocket/          # WebSocket 管理
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── components/     # UI 组件
│       ├── services/       # API 服务
│       └── stores/         # 状态管理
├── scripts/                # 脚本工具
│   ├── start_service.py    # 启动服务
│   └── cli.py              # 命令行工具
├── storage/                # 运行时存储
│   ├── uploads/            # 上传文件
│   └── outputs/            # 输出结果
└── docs/                   # 文档
```

## 常见问题

**Tesseract 找不到**
- 确保已安装并在 `.env` 中配置正确路径

**API Key 无效**
- 检查 `.env` 中的配置是否正确
- 确认 API Key 有足够配额

**前端无法连接后端**
- 确认后端服务已启动（http://localhost:8001/health）
- 检查防火墙设置

**生成结果不理想**
- 增加 `max_loops` 参数
- 降低 `threshold` 阈值
- 尝试切换不同的模型提供商

## 技术栈

**后端**: FastAPI, Matplotlib, Pytesseract  
**前端**: Vue 3, Vite, Pinia, Chart.js  
**AI**: 通义千问/OpenAI/Gemini/豆包

## 更多文档

- [API 文档](docs/API.md) - 后端 API 接口说明
- [架构设计](docs/ARCHITECTURE.md) - 系统架构和设计思路
- [开发指南](docs/DEVELOPMENT.md) - 开发环境配置和贡献指南

## 许可证

MIT License
