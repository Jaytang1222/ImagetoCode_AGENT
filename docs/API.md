# API 文档

## 基础信息

- 基础 URL: `http://localhost:8001`
- API 文档: `http://localhost:8001/docs`
- 健康检查: `http://localhost:8001/health`

## 认证

当前版本无需认证。

## 接口列表

### 1. 上传图片

上传参考图表图片。

**请求**

```
POST /api/upload
Content-Type: multipart/form-data
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图片文件（PNG/JPG/JPEG，最大 10MB） |

**响应**

```json
{
  "file_id": "uuid-string",
  "filename": "original-filename.png",
  "url": "/uploads/uuid-string.png"
}
```

### 2. 启动流水线

启动图表复现流水线。

**请求**

```
POST /api/pipeline/start
Content-Type: application/json
```

**参数**

```json
{
  "file_id": "uuid-string",
  "max_loops": 5,
  "threshold": 0.75
}
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| file_id | string | 是 | - | 上传文件的 ID |
| max_loops | integer | 否 | 5 | 最大迭代轮数 |
| threshold | float | 否 | 0.75 | 验证通过阈值（0-1） |

**响应**

```json
{
  "pipeline_id": "uuid-string",
  "status": "running",
  "message": "流水线已启动"
}
```

### 3. 查询流水线状态

查询流水线执行状态。

**请求**

```
GET /api/pipeline/{pipeline_id}/status
```

**响应**

```json
{
  "pipeline_id": "uuid-string",
  "status": "running",
  "current_round": 2,
  "max_loops": 5,
  "current_agent": "agent2",
  "progress": 40
}
```

状态值：
- `pending`: 等待中
- `running`: 运行中
- `completed`: 已完成
- `failed`: 失败

### 4. 获取流水线结果

获取流水线执行结果。

**请求**

```
GET /api/results/{pipeline_id}
```

**响应**

```json
{
  "pipeline_id": "uuid-string",
  "status": "completed",
  "passed": true,
  "final_score": 0.82,
  "rounds": 3,
  "code_url": "/outputs/uuid/current_matplotlib.py",
  "image_url": "/outputs/uuid/generated_chart.png",
  "reports": {
    "agent2": ["/outputs/uuid/report_agent2_round1.txt"],
    "agent3": ["/outputs/uuid/report_agent3_round1.txt"],
    "validator": ["/outputs/uuid/validator_round1.json"]
  }
}
```

### 5. 下载文件

下载生成的代码或图片。

**请求**

```
GET /api/download/{pipeline_id}/{file_type}
```

**参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| pipeline_id | string | 流水线 ID |
| file_type | string | 文件类型：`code` 或 `image` |

**响应**

返回文件流，浏览器自动下载。

### 6. 获取历史记录

获取所有流水线执行历史。

**请求**

```
GET /api/history?limit=20&offset=0
```

**参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | integer | 否 | 20 | 返回数量 |
| offset | integer | 否 | 0 | 偏移量 |

**响应**

```json
{
  "total": 100,
  "items": [
    {
      "pipeline_id": "uuid-string",
      "status": "completed",
      "created_at": "2026-05-05T10:30:00Z",
      "completed_at": "2026-05-05T10:35:00Z",
      "passed": true,
      "final_score": 0.82
    }
  ]
}
```

### 7. 删除历史记录

删除指定的流水线记录。

**请求**

```
DELETE /api/history/{pipeline_id}
```

**响应**

```json
{
  "message": "记录已删除"
}
```

## WebSocket

实时接收流水线执行进度。

**连接**

```
ws://localhost:8001/ws/{pipeline_id}
```

**消息格式**

```json
{
  "type": "progress",
  "data": {
    "current_round": 2,
    "current_agent": "agent2",
    "progress": 40,
    "message": "正在执行视觉评估..."
  }
}
```

消息类型：
- `progress`: 进度更新
- `completed`: 执行完成
- `error`: 执行错误

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |

**错误响应格式**

```json
{
  "detail": "错误描述信息"
}
```

## 使用示例

### Python

```python
import requests

# 上传图片
with open('chart.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/upload',
        files={'file': f}
    )
file_id = response.json()['file_id']

# 启动流水线
response = requests.post(
    'http://localhost:8001/api/pipeline/start',
    json={
        'file_id': file_id,
        'max_loops': 5,
        'threshold': 0.75
    }
)
pipeline_id = response.json()['pipeline_id']

# 查询结果
response = requests.get(
    f'http://localhost:8001/api/results/{pipeline_id}'
)
result = response.json()
```

### JavaScript

```javascript
// 上传图片
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadRes = await fetch('http://localhost:8001/api/upload', {
  method: 'POST',
  body: formData
});
const { file_id } = await uploadRes.json();

// 启动流水线
const startRes = await fetch('http://localhost:8001/api/pipeline/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id,
    max_loops: 5,
    threshold: 0.75
  })
});
const { pipeline_id } = await startRes.json();

// WebSocket 监听进度
const ws = new WebSocket(`ws://localhost:8001/ws/${pipeline_id}`);
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
};
```

## 限制说明

- 单个文件最大 10MB
- 支持格式：PNG, JPG, JPEG
- 并发流水线数量：建议不超过 5 个
- WebSocket 连接超时：30 分钟
