# 开发指南

## 开发环境配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Python 环境

推荐使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 3. Node.js 环境

```bash
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```env
MODEL_PROVIDER=qwen
QWEN_API_KEY=your_api_key
TESSERACT_CMD=path_to_tesseract
```

## 项目结构说明

```
.
├── src/                      # 核心源代码
│   ├── agents/               # 智能体实现
│   │   ├── agent1_code_generation.py
│   │   ├── agent2_visual_judgment.py
│   │   ├── agent3_code_evaluation.py
│   │   ├── agent4_feedback_revision.py
│   │   └── pipeline.py       # 流水线编排
│   ├── validators/           # 验证器
│   │   ├── color_consistency_validator.py
│   │   ├── text_consistency_validator.py
│   │   ├── structural_consistency_validator.py
│   │   └── multidim_validator.py
│   └── utils/                # 工具函数
│       ├── model_providers.py
│       ├── dashscope_api.py
│       └── matplotlib_render.py
├── backend/                  # 后端服务
│   ├── api/                  # API 路由
│   ├── services/             # 业务逻辑
│   ├── websocket/            # WebSocket
│   ├── models/               # 数据模型
│   ├── utils/                # 工具函数
│   ├── config.py             # 配置
│   └── main.py               # 入口
├── frontend/                 # 前端应用
│   └── src/
│       ├── components/       # Vue 组件
│       ├── services/         # API 服务
│       ├── stores/           # 状态管理
│       ├── views/            # 页面视图
│       └── styles/           # 样式文件
├── scripts/                  # 脚本工具
├── storage/                  # 运行时存储
├── logs/                     # 日志文件
└── docs/                     # 文档
```

## 开发流程

### 启动开发服务器

**方式一：一键启动（推荐）**

```bash
python scripts/start_service.py
```

**方式二：分别启动**

终端 1 - 后端：
```bash
cd backend
uvicorn main:app --reload --port 8001
```

终端 2 - 前端：
```bash
cd frontend
npm run dev
```

### 访问地址

- 前端：http://localhost:5174
- 后端：http://localhost:8001
- API 文档：http://localhost:8001/docs

## 代码规范

### Python 代码规范

遵循 PEP 8 规范：

```python
# 导入顺序：标准库 → 第三方库 → 本地模块
import os
from pathlib import Path

from fastapi import FastAPI
import numpy as np

from backend.config import BASE_DIR

# 函数命名：小写+下划线
def process_image(image_path: str) -> dict:
    """
    处理图片
    
    Args:
        image_path: 图片路径
        
    Returns:
        处理结果字典
    """
    pass

# 类命名：大驼峰
class ImageProcessor:
    def __init__(self):
        pass
```

### JavaScript 代码规范

遵循 Vue 3 风格指南：

```javascript
// 组合式 API
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ComponentName',
  setup() {
    // 响应式数据
    const count = ref(0)
    
    // 计算属性
    const doubleCount = computed(() => count.value * 2)
    
    // 方法
    const increment = () => {
      count.value++
    }
    
    // 生命周期
    onMounted(() => {
      console.log('Component mounted')
    })
    
    return {
      count,
      doubleCount,
      increment
    }
  }
}
```

### 提交规范

使用语义化提交信息：

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具链更新
```

示例：
```bash
git commit -m "feat: 添加多模型支持"
git commit -m "fix: 修复 WebSocket 断线重连问题"
git commit -m "docs: 更新 API 文档"
```

## 调试技巧

### 后端调试

**日志输出**

```python
from backend.utils.logger import app_logger

app_logger.debug("调试信息")
app_logger.info("普通信息")
app_logger.warning("警告信息")
app_logger.error("错误信息")
```

**断点调试**

使用 VS Code 调试配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "backend.main:app",
        "--reload",
        "--port",
        "8001"
      ],
      "jinja": true
    }
  ]
}
```

### 前端调试

**Vue DevTools**

安装浏览器扩展：
- Chrome: Vue.js devtools
- Firefox: Vue.js devtools

**控制台调试**

```javascript
// 查看响应式数据
console.log('Current state:', store.state)

// 性能分析
console.time('API Call')
await api.uploadFile(file)
console.timeEnd('API Call')
```

## 测试

### 后端测试

创建测试文件 `tests/test_api.py`：

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_upload_file():
    with open("test_image.png", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.png", f, "image/png")}
        )
    assert response.status_code == 200
    assert "file_id" in response.json()
```

运行测试：

```bash
pytest tests/
```

### 前端测试

使用 Vitest（可选）：

```bash
npm install -D vitest @vue/test-utils
```

创建测试文件 `tests/components/ImageUploader.test.js`：

```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ImageUploader from '@/components/ImageUploader.vue'

describe('ImageUploader', () => {
  it('renders properly', () => {
    const wrapper = mount(ImageUploader)
    expect(wrapper.find('input[type="file"]').exists()).toBe(true)
  })
})
```

## 常见开发任务

### 添加新的 API 接口

1. 在 `backend/api/` 创建路由文件
2. 定义请求/响应模型
3. 实现业务逻辑
4. 在 `backend/main.py` 注册路由

示例：

```python
# backend/api/custom.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CustomRequest(BaseModel):
    param: str

class CustomResponse(BaseModel):
    result: str

@router.post("/custom", response_model=CustomResponse)
async def custom_endpoint(request: CustomRequest):
    return CustomResponse(result=f"Processed: {request.param}")
```

### 添加新的前端页面

1. 在 `frontend/src/views/` 创建页面组件
2. 在 `frontend/src/router/` 配置路由
3. 在导航菜单添加链接

示例：

```javascript
// frontend/src/views/NewPage.vue
<template>
  <div class="new-page">
    <h1>新页面</h1>
  </div>
</template>

<script>
export default {
  name: 'NewPage'
}
</script>
```

### 扩展验证器

1. 在 `src/validators/` 创建新验证器
2. 实现 `validate` 方法
3. 在 `multidim_validator.py` 中集成

示例：

```python
# src/validators/custom_validator.py
from typing import Tuple

def custom_validate(ref_img: str, gen_img: str) -> Tuple[float, str]:
    """
    自定义验证逻辑
    
    Returns:
        (分数 0-1, 说明文本)
    """
    score = 0.8
    explanation = "自定义验证通过"
    return score, explanation
```

## 性能优化建议

### 后端优化

1. 使用异步操作避免阻塞
2. 添加缓存减少重复计算
3. 优化图片处理算法
4. 限制并发流水线数量

### 前端优化

1. 组件懒加载
2. 图片压缩和懒加载
3. 防抖和节流
4. 虚拟滚动（大列表）

## 故障排查

### 常见问题

**问题：后端启动失败**

检查：
- Python 版本是否 3.9+
- 依赖是否完整安装
- 端口 8001 是否被占用
- 环境变量是否正确配置

**问题：前端无法连接后端**

检查：
- 后端是否正常运行
- CORS 配置是否正确
- 网络防火墙设置
- 浏览器控制台错误信息

**问题：流水线执行失败**

检查：
- API Key 是否有效
- Tesseract 是否正确安装
- 日志文件 `logs/error.log`
- 输入图片是否符合要求

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看后端实时日志
cd backend
uvicorn main:app --reload --log-level debug
```

## 贡献指南

### 提交 Pull Request

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -m "feat: 添加新特性"`
4. 推送分支：`git push origin feature/new-feature`
5. 创建 Pull Request

### 代码审查要点

- 代码符合规范
- 添加必要的注释
- 通过所有测试
- 更新相关文档
- 无明显性能问题

## 资源链接

**框架文档**
- FastAPI: https://fastapi.tiangolo.com/
- Vue 3: https://vuejs.org/
- Pinia: https://pinia.vuejs.org/

**工具文档**
- Matplotlib: https://matplotlib.org/
- Tesseract: https://github.com/tesseract-ocr/tesseract

**模型文档**
- 通义千问: https://help.aliyun.com/zh/dashscope/
- OpenAI: https://platform.openai.com/docs
- Gemini: https://ai.google.dev/docs
