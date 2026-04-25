# -*- coding: utf-8 -*-
"""
Flask Web 应用：多智能体图表复现系统的前端界面
"""
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import os
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional

# 保证从项目根目录可导入本地模块
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from Agents.agent_pipeline import run_full_pipeline

app = Flask(__name__, static_folder='static', template_folder='frontend')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大 16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局任务状态
task_status: Dict[str, Any] = {
    'running': False,
    'progress': 0,
    'current_step': '',
    'logs': [],
    'result': None
}


def add_log(message: str) -> None:
    """添加日志"""
    timestamp: str = time.strftime('%H:%M:%S')
    logs_list: list = task_status.get('logs', [])
    if isinstance(logs_list, list):
        logs_list.append({'time': timestamp, 'message': message})
        task_status['logs'] = logs_list
    print(f"[{timestamp}] {message}")


def _execute_pipeline_task(input_image: str, out_dir: str, max_loops: int, threshold: float) -> None:
    """
    执行流水线任务的核心逻辑
    
    Args:
        input_image: 输入图片路径
        out_dir: 输出目录
        max_loops: 最大迭代次数
        threshold: 验证阈值
    """
    try:
        add_log("🚀 开始多智能体图表复现流程")
        add_log(f"📁 输入文件: {input_image}")
        add_log(f"📂 输出目录: {out_dir}")
        add_log(f"⚙️  参数: 最大迭代={max_loops}, 阈值={threshold}")
        
        task_status['progress'] = 5
        task_status['current_step'] = 'Agent1: 代码生成...'
        
        ok: bool
        code_path: Optional[str]
        png_path: Optional[str]
        summary: Optional[str]
        
        # 定义进度回调函数
        def progress_callback(step: str, progress: int):
            """更新任务进度"""
            task_status['current_step'] = step
            task_status['progress'] = progress
            add_log(f"📊 进度: {step} ({progress}%)")
        
        ok, code_path, png_path, summary = run_full_pipeline(
            input_chart_image=input_image,
            out_dir=out_dir,
            max_loops=max_loops,
            threshold=threshold,
            progress_callback=progress_callback,
        )
        
        task_status['progress'] = 100
        task_status['current_step'] = '完成'
        task_status['result'] = {
            'success': ok,
            'code_path': code_path,
            'png_path': png_path,
            'summary': summary,
            'out_dir': out_dir
        }
        
        add_log("✅ 任务完成!" if ok else "❌ 任务未完成")
        add_log(f"📊 验证通过: {ok}")
        add_log(f"📝 摘要: {summary}")
        
    except Exception as e:
        add_log(f"❌ 错误: {str(e)}")
        task_status['result'] = {'success': False, 'error': str(e)}
    finally:
        task_status['running'] = False


@app.route('/')
def index() -> str:
    """主页"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file() -> tuple[Response, int] | Response:
    """处理文件上传并启动任务"""
    if task_status['running']:
        return jsonify({'error': '已有任务正在运行'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    filename_value: str = file.filename if file.filename is not None else ''
    if filename_value == '':
        return jsonify({'error': '未选择文件'}), 400
    
    filename_lower: str = filename_value.lower()
    if not filename_lower.endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'error': '仅支持 PNG/JPG 格式'}), 400
    
    # 保存上传的文件
    filename = f"input_{int(time.time())}{Path(filename_value).suffix}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # 获取参数
    max_loops = int(request.form.get('max_loops', 5))
    threshold = float(request.form.get('threshold', 0.75))
    out_dir = f"outputs/run_{int(time.time())}"
    
    # 重置任务状态
    task_status.update({
        'running': True,
        'progress': 0,
        'current_step': '准备中...',
        'logs': [],
        'result': None
    })
    
    # 在后台线程中运行任务
    thread = threading.Thread(target=_execute_pipeline_task, args=(filepath, out_dir, max_loops, threshold))
    thread.daemon = True
    thread.start()
    
    # 使用时间戳作为任务ID
    task_id = str(int(time.time()))
    
    return jsonify({
        'message': '任务已启动',
        'task_id': task_id,
        'out_dir': out_dir
    })


@app.route('/api/run', methods=['POST'])
def run_pipeline_api() -> tuple[Response, int] | Response:
    """
    API 接口：直接运行流水线（类似 main.py 的功能）
    请求体 JSON 格式：
    {
        "input": "input.png",           # 输入图片路径
        "out": "outputs",               # 输出目录（可选）
        "max_loops": 5,                 # 最大迭代次数（可选）
        "threshold": 0.75               # 验证阈值（可选）
    }
    """
    if task_status['running']:
        return jsonify({'error': '已有任务正在运行'}), 400
    
    # 获取请求参数
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供 JSON 格式的请求体'}), 400
    
    input_image = data.get('input', 'input.png')
    out_dir = data.get('out', 'outputs')
    max_loops = int(data.get('max_loops', 5))
    threshold = float(data.get('threshold', 0.75))
    
    # 验证输入文件是否存在
    if not os.path.isfile(input_image):
        return jsonify({
            'error': f'未找到输入图片: {input_image}',
            'message': '请将参考图放在该路径，或使用 upload 接口上传图片'
        }), 404
    
    # 重置任务状态
    task_status.update({
        'running': True,
        'progress': 0,
        'current_step': '准备中...',
        'logs': [],
        'result': None
    })
    
    # 在后台线程中运行任务
    thread = threading.Thread(target=_execute_pipeline_task, args=(input_image, out_dir, max_loops, threshold))
    thread.daemon = True
    thread.start()
    
    # 使用时间戳作为任务ID
    task_id = str(int(time.time()))
    
    return jsonify({
        'message': '任务已启动',
        'task_id': task_id,
        'input': input_image,
        'out_dir': out_dir,
        'parameters': {
            'max_loops': max_loops,
            'threshold': threshold
        }
    })


@app.route('/api/tasks/<task_id>')
def get_task_status(task_id: str) -> Response:
    """获取指定任务的状态"""
    # 简化处理：返回当前任务状态
    status = task_status.copy()
    status['task_id'] = task_id
    
    # 根据运行状态和结果确定状态
    if status.get('result'):
        if status['result'].get('success'):
            status['status'] = 'completed'
        else:
            status['status'] = 'failed'
            # 添加错误信息到 message
            if not status.get('message') or status['message'] == '完成':
                status['message'] = f"任务失败: {status['result'].get('error', '未知错误')}"
    elif status['running']:
        status['status'] = 'running'
    else:
        status['status'] = 'pending'
    
    status['message'] = status.get('current_step', '等待开始...')
    return jsonify(status)


@app.route('/api/outputs')
def list_outputs() -> Response:
    """列出所有输出目录"""
    outputs_dir = os.path.abspath('outputs')
    if not os.path.exists(outputs_dir):
        return jsonify([])
    
    output_list = []
    for item in os.listdir(outputs_dir):
        item_path = os.path.join(outputs_dir, item)
        if os.path.isdir(item_path):
            # 计算目录大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(item_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            
            output_list.append({
                'name': item,
                'path': item_path,
                'size': total_size,
                'modified': os.path.getmtime(item_path)
            })
    
    # 按修改时间排序
    output_list.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(output_list)


@app.route('/api/download/code/<task_id>')
def download_code(task_id: str) -> tuple[Response, int] | Response:
    """下载代码文件"""
    outputs_dir = os.path.abspath('outputs')
    
    # 查找匹配目录（支持 run_{task_id} 格式）
    if os.path.exists(outputs_dir):
        for item in os.listdir(outputs_dir):
            # 匹配 task_id 或 run_{task_id} 格式
            if item == task_id or item == f'run_{task_id}' or item.endswith(f'_{task_id}'):
                item_path = os.path.join(outputs_dir, item)
                if os.path.isdir(item_path):
                    # 查找 JS 文件
                    for f in os.listdir(item_path):
                        if f.endswith('.js'):
                            return send_from_directory(item_path, f)
    
    return jsonify({'error': '代码文件不存在'}), 404


@app.route('/api/download/image/<task_id>')
def download_image(task_id: str) -> tuple[Response, int] | Response:
    """下载图片文件"""
    outputs_dir = os.path.abspath('outputs')
    
    # 查找匹配目录（支持 run_{task_id} 格式）
    if os.path.exists(outputs_dir):
        for item in os.listdir(outputs_dir):
            # 匹配 task_id 或 run_{task_id} 格式
            if item == task_id or item == f'run_{task_id}' or item.endswith(f'_{task_id}'):
                item_path = os.path.join(outputs_dir, item)
                if os.path.isdir(item_path):
                    # 查找 PNG 文件
                    for f in os.listdir(item_path):
                        if f.endswith('.png'):
                            return send_from_directory(item_path, f)
    
    return jsonify({'error': '图片文件不存在'}), 404


@app.route('/api/download/image/dir/<dir_name>')
def download_image_by_dir(dir_name: str) -> tuple[Response, int] | Response:
    """通过目录名下载图片文件（用于历史任务预览）"""
    outputs_dir = os.path.abspath('outputs')
    item_path = os.path.join(outputs_dir, dir_name)
    
    # 安全检查：防止路径遍历攻击
    if not os.path.abspath(item_path).startswith(outputs_dir):
        return jsonify({'error': '非法访问'}), 403
    
    if os.path.isdir(item_path):
        # 查找 PNG 文件（优先使用 generated_chart.png）
        png_files = [f for f in os.listdir(item_path) if f.endswith('.png')]
        
        # 优先返回 generated_chart.png，否则返回第一个 PNG 文件
        if 'generated_chart.png' in png_files:
            return send_from_directory(item_path, 'generated_chart.png')
        elif png_files:
            return send_from_directory(item_path, png_files[0])
    
    return jsonify({'error': '图片文件不存在'}), 404


@app.route('/api/preview/<task_id>')
def preview_html(task_id: str) -> tuple[Response, int] | Response:
    """预览 HTML 文件"""
    outputs_dir = os.path.abspath('outputs')
    
    # 查找匹配目录（支持 run_{task_id} 格式）
    if os.path.exists(outputs_dir):
        for item in os.listdir(outputs_dir):
            # 匹配 task_id 或 run_{task_id} 格式
            if item == task_id or item == f'run_{task_id}' or item.endswith(f'_{task_id}'):
                item_path = os.path.join(outputs_dir, item)
                if os.path.isdir(item_path):
                    preview_path = os.path.join(item_path, 'preview.html')
                    if os.path.exists(preview_path):
                        # 读取 HTML 并将 CDN 替换为本地路径
                        with open(preview_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # 替换 CDN 链接为本地路径
                        content = content.replace(
                            'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js',
                            '/static/js/echarts.min.js'
                        )
                        return Response(content, mimetype='text/html')
    
    return jsonify({'error': '预览文件不存在'}), 404


@app.route('/api/preview/dir/<dir_name>')
def preview_dir_html(dir_name: str) -> tuple[Response, int] | Response:
    """预览指定目录的 HTML 文件"""
    outputs_dir = os.path.abspath('outputs')
    item_path = os.path.join(outputs_dir, dir_name)
    
    # 安全检查
    if not os.path.abspath(item_path).startswith(outputs_dir):
        return jsonify({'error': '非法访问'}), 403
    
    if os.path.isdir(item_path):
        preview_path = os.path.join(item_path, 'preview.html')
        if os.path.exists(preview_path):
            # 读取 HTML 并将 CDN 替换为本地路径
            with open(preview_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 替换 CDN 链接为本地路径
            content = content.replace(
                'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js',
                '/static/js/echarts.min.js'
            )
            return Response(content, mimetype='text/html')
    
    return jsonify({'error': '预览文件不存在'}), 404


@app.route('/api/code/dir/<dir_name>')
def get_code_by_dir(dir_name: str) -> tuple[Response, int] | Response:
    """通过目录名获取 Python 代码文件内容（用于查看代码功能）"""
    outputs_dir = os.path.abspath('outputs')
    item_path = os.path.join(outputs_dir, dir_name)
    
    # 安全检查：防止路径遍历攻击
    if not os.path.abspath(item_path).startswith(outputs_dir):
        return jsonify({'error': '非法访问'}), 403
    
    if os.path.isdir(item_path):
        # 优先查找 agent1_generated_matplotlib.py，其次查找其他 .py 文件
        code_files = [f for f in os.listdir(item_path) if f.endswith('.py')]
        
        # 优先返回 agent1_generated_matplotlib.py
        target_file = None
        if 'agent1_generated_matplotlib.py' in code_files:
            target_file = 'agent1_generated_matplotlib.py'
        elif code_files:
            # 如果没有 matplotlib 文件，返回第一个 .py 文件
            target_file = code_files[0]
        
        if target_file:
            file_path = os.path.join(item_path, target_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return jsonify({
                    'success': True,
                    'filename': target_file,
                    'content': content
                })
            except Exception as e:
                return jsonify({'error': f'读取文件失败: {str(e)}'}), 500
    
    return jsonify({'error': '代码文件不存在'}), 404


@app.route('/status')
def get_status() -> Response:
    """获取任务状态（旧版兼容）"""
    return jsonify(task_status)


@app.route('/results/<path:filename>')
def serve_result(filename: str) -> tuple[Response, int] | Response:
    """提供结果文件"""
    # 安全检查：防止路径遍历攻击
    base_dir: str = os.path.abspath('outputs')
    file_path: str = os.path.abspath(os.path.join(base_dir, filename))
    
    if not file_path.startswith(base_dir):
        return jsonify({'error': '非法访问'}), 403
    
    if os.path.exists(file_path):
        return send_from_directory(base_dir, filename)
    return jsonify({'error': '文件不存在'}), 404


@app.route('/code/<path:filename>')
def serve_code(filename: str) -> tuple[Response, int] | Response:
    """提供代码文件"""
    base_dir: str = os.path.abspath('outputs')
    file_path: str = os.path.abspath(os.path.join(base_dir, filename))
    
    if not file_path.startswith(base_dir):
        return jsonify({'error': '非法访问'}), 403
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content, 'filename': filename})
    return jsonify({'error': '文件不存在'}), 404


if __name__ == '__main__':
    print("="*60)
    print("🎨 多智能体图表复现系统 - Web 界面")
    print("="*60)
    print("🌐 访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
