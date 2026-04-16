# 多智能体图表复现系统 - Web 版改造说明

## 📋 改造概述

将原有的命令行程序改造为前后端分离的 Web 应用，提供图形化界面和实时状态监控。

## 🎯 主要改动

### 1. 后端改造 (main.py)

**原功能**: 命令行入口，同步执行完整流程
**新功能**: Flask REST API 服务

#### 核心特性：
- ✅ RESTful API 设计
- ✅ 异步任务处理（后台线程）
- ✅ 任务状态管理（内存存储）
- ✅ 文件上传与管理
- ✅ CORS 跨域支持
- ✅ 健康检查接口

#### 主要 API 端点：
```
GET  /                          # 前端页面
POST /api/upload                # 上传文件并创建任务
GET  /api/tasks/<task_id>       # 获取任务状态
GET  /api/tasks                 # 列出所有任务
GET  /api/download/code/<id>    # 下载生成的代码
GET  /api/download/image/<id>   # 下载生成的图片
GET  /api/preview/<id>          # 在线预览 HTML
GET  /health                    # 健康检查
```

### 2. 前端开发 (frontend/index.html)

**技术栈**: 纯 HTML + CSS + JavaScript（无框架依赖）

#### 界面特性：
- 🎨 现代化渐变背景设计
- 📱 响应式布局，支持移动端
- 🖱️ 拖拽上传文件
- 📊 实时进度条显示
- 🔔 动态状态更新
- 💫 流畅动画效果

#### 功能模块：

1. **上传区域**
   - 拖拽/点击上传
   - 文件类型验证
   - 参数配置（迭代轮数、阈值）

2. **状态监控**
   - 整体进度条（0-100%）
   - 实时状态消息
   - 5个智能体卡片动态高亮
   - 颜色编码的状态指示

3. **结果展示**
   - 生成的图表预览
   - 代码片段预览
   - 一键下载按钮
   - 在线预览功能

4. **任务管理**
   - 历史任务列表
   - 任务状态标签
   - 快速切换查看

### 3. 新增文件

```
├── main.py                     # 改造为 Flask 后端
├── frontend/
│   └── index.html             # 前端单页应用
├── requirements.txt            # Python 依赖（新增 flask, flask-cors）
├── WEB_SERVICE.md             # Web 服务使用说明
└── PROJECT_SUMMARY.md         # 本文件
```

## 🔄 工作流程

### 用户操作流程：
```
1. 打开浏览器访问 http://localhost:5000
2. 拖拽或选择参考图表图片
3. 配置参数（可选）
4. 点击"开始任务"
5. 实时观察进度和状态
6. 查看结果并下载
```

### 后端处理流程：
```
1. 接收文件上传 → 保存至 uploads/
2. 创建任务记录 → 生成唯一 task_id
3. 启动后台线程 → 执行 run_full_pipeline()
4. 定期更新任务状态 → 供前端查询
5. 完成后保存结果 → outputs/{task_id}/
```

### 状态流转：
```
pending → running → completed/failed/error
   ↓         ↓
等待中    执行中    终态
```

## 🎨 界面设计亮点

### 1. 视觉设计
- 紫色渐变主题色 (#667eea → #764ba2)
- 圆角卡片式布局
- 阴影和悬停效果
- 响应式网格系统

### 2. 交互体验
- 拖拽上传视觉反馈
- 进度条平滑动画
- Agent 卡片脉冲动画
- 按钮悬停提升效果

### 3. 状态可视化
- 当前活跃 Agent 高亮显示
- 已完成 Agent 绿色标记
- 状态消息颜色编码
- 进度百分比实时更新

## 📊 技术架构

### 后端架构
```
Flask Server
├── File Upload Handler
├── Task Manager (in-memory dict)
├── Background Worker (threading)
├── REST API Endpoints
└── Static File Server
```

### 前端架构
```
Single Page Application
├── File Upload Component
├── Status Monitor (polling every 2s)
├── Progress Tracker
├── Result Viewer
└── Task List Manager
```

### 数据流
```
User Action → Frontend JS → API Call → Backend Handler
                                      ↓
                              Background Thread
                                      ↓
                              Task State Update
                                      ↓
Frontend Display ← Polling ← In-Memory Storage
```

## ⚙️ 配置说明

### 环境变量
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY = "your_api_key"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key"
```

### 依赖安装
```bash
pip install -r requirements.txt
playwright install chromium
```

### 启动服务
```bash
python main.py
```

默认端口: 5000  
访问地址: http://localhost:5000

## 🔧 扩展建议

### 短期优化
1. 添加任务持久化（数据库存储）
2. 实现 WebSocket 实时推送（替代轮询）
3. 添加用户认证系统
4. 增加任务队列管理（Celery）

### 长期规划
1. 支持批量任务处理
2. 添加结果对比功能
3. 实现历史记录搜索
4. 部署到云服务器
5. 添加性能监控

## 📝 注意事项

### 当前限制
1. 任务状态存储在内存中，重启服务会丢失
2. 使用轮询而非 WebSocket，有一定延迟
3. 不支持并发大流量（开发服务器）
4. 无用户隔离，所有任务公开可见

### 生产环境建议
1. 使用 Gunicorn/uWSGI 替代 Flask 开发服务器
2. 添加 Redis 进行任务状态缓存
3. 使用 PostgreSQL/MySQL 持久化数据
4. 配置 Nginx 反向代理
5. 启用 HTTPS
6. 添加速率限制和认证

## 🎉 使用示例

### 场景 1: 单次图表复现
1. 上传 `input.png`
2. 保持默认参数
3. 等待 2-5 分钟
4. 下载生成的代码和图片

### 场景 2: 参数调优
1. 第一次: threshold=0.75, max_loops=5
2. 查看结果不满意
3. 第二次: threshold=0.85, max_loops=8
4. 对比两次结果

### 场景 3: 批量测试
1. 同时上传多个图片（创建多个任务）
2. 在任务列表中切换查看
3. 分别下载各任务结果

## 📞 技术支持

遇到问题请检查：
1. ✅ 环境变量 `DASHSCOPE_API_KEY` 已设置
2. ✅ Playwright 和 Chromium 已安装
3. ✅ 端口 5000 未被占用
4. ✅ 浏览器支持现代 JavaScript

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install flask flask-cors dashscope playwright
playwright install chromium

# 2. 设置 API Key
$env:DASHSCOPE_API_KEY = "sk-xxx"  # Windows
export DASHSCOPE_API_KEY="sk-xxx"  # Linux/Mac

# 3. 启动服务
python main.py

# 4. 打开浏览器
# 访问 http://localhost:5000
```

---

**改造完成时间**: 2026-04-09  
**版本**: v2.1 Web Edition  
**作者**: AI Assistant
