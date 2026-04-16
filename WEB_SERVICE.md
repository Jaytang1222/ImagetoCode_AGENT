# Web 服务使用说明

## 启动服务

```bash
python main.py
```

服务将在 `http://localhost:5000` 启动。

## 功能特性

### 1. 文件上传
- 支持拖拽上传或点击选择文件
- 支持 PNG、JPG 格式
- 可配置最大迭代轮数和验证阈值

### 2. 实时状态监控
- 进度条显示整体进度
- 实时显示当前执行的 Agent 阶段
- 动态高亮正在工作的智能体

### 3. Agent 工作流程可视化
- **Agent 1**: 代码生成 (VLM)
- **Agent 2**: 视觉评判
- **Agent 3**: 代码评估
- **Agent 4**: 反馈修订
- **验证器**: 多维验证

### 4. 结果展示
- 生成的图表预览
- 代码预览（前500字符）
- 一键下载代码和图片
- 在线预览 HTML

### 5. 任务管理
- 查看所有历史任务
- 切换查看不同任务的结果
- 任务状态追踪

## API 接口

### 上传文件并创建任务
```
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: 图片文件
- max_loops: 最大迭代轮数 (默认: 5)
- threshold: 验证阈值 (默认: 0.75)

Response:
{
  "task_id": "uuid",
  "message": "任务已创建"
}
```

### 获取任务状态
```
GET /api/tasks/<task_id>

Response:
{
  "id": "uuid",
  "status": "pending|running|completed|failed|error",
  "progress": 0-100,
  "message": "当前状态描述",
  "data": {
    "code_path": "...",
    "png_path": "...",
    "summary": "..."
  }
}
```

### 列出所有任务
```
GET /api/tasks

Response:
[
  { task_object },
  ...
]
```

### 下载生成的代码
```
GET /api/download/code/<task_id>
```

### 下载生成的图片
```
GET /api/download/image/<task_id>
```

### 在线预览 HTML
```
GET /api/preview/<task_id>
```

### 健康检查
```
GET /health

Response:
{
  "status": "ok",
  "timestamp": "ISO时间",
  "active_tasks": 活跃任务数
}
```

## 注意事项

1. 确保已设置环境变量 `DASHSCOPE_API_KEY`
2. 确保已安装 Playwright 和 Chromium: `playwright install chromium`
3. 任务在后台线程中运行，不会阻塞界面
4. 每2秒自动刷新任务状态
5. 支持同时运行多个任务
