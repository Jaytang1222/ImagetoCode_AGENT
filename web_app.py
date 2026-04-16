# -*- coding: utf-8 -*-
"""
Flask Web 应用：多智能体图表复现系统的前端界面
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import threading
import time
from pathlib import Path

# 保证从项目根目录可导入本地模块
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from agent_pipeline import run_full_pipeline

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大 16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局任务状态
task_status = {
    'running': False,
    'progress': 0,
    'current_step': '',
    'logs': [],
    'result': None
}


def add_log(message):
    """添加日志"""
    timestamp = time.strftime('%H:%M:%S')
    task_status['logs'].append({'time': timestamp, 'message': message})
    print(f"[{timestamp}] {message}")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传并启动任务"""
    if task_status['running']:
        return jsonify({'error': '已有任务正在运行'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'error': '仅支持 PNG/JPG 格式'}), 400
    
    # 保存上传的文件
    filename = f"input_{int(time.time())}{Path(file.filename).suffix}"
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
    def run_task():
        try:
            add_log("🚀 开始多智能体图表复现流程")
            add_log(f"📁 输入文件: {filename}")
            add_log(f"⚙️  参数: 最大迭代={max_loops}, 阈值={threshold}")
            
            task_status['progress'] = 5
            task_status['current_step'] = 'Agent1: 代码生成...'
            
            ok, code_path, png_path, summary = run_full_pipeline(
                input_chart_image=filepath,
                out_dir=out_dir,
                max_loops=max_loops,
                threshold=threshold,
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
    
    thread = threading.Thread(target=run_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': '任务已启动',
        'out_dir': out_dir
    })


@app.route('/api/run', methods=['POST'])
def run_pipeline_api():
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
    def run_task():
        try:
            add_log("🚀 开始多智能体图表复现流程")
            add_log(f"📁 输入文件: {input_image}")
            add_log(f"📂 输出目录: {out_dir}")
            add_log(f"⚙️  参数: 最大迭代={max_loops}, 阈值={threshold}")
            
            task_status['progress'] = 5
            task_status['current_step'] = 'Agent1: 代码生成...'
            
            ok, code_path, png_path, summary = run_full_pipeline(
                input_chart_image=input_image,
                out_dir=out_dir,
                max_loops=max_loops,
                threshold=threshold,
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
    
    thread = threading.Thread(target=run_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': '任务已启动',
        'input': input_image,
        'out_dir': out_dir,
        'parameters': {
            'max_loops': max_loops,
            'threshold': threshold
        }
    })


@app.route('/status')
def get_status():
    """获取任务状态"""
    return jsonify(task_status)


@app.route('/results/<path:filename>')
def serve_result(filename):
    """提供结果文件"""
    # 安全检查：防止路径遍历攻击
    base_dir = os.path.abspath('outputs')
    file_path = os.path.abspath(os.path.join(base_dir, filename))
    
    if not file_path.startswith(base_dir):
        return jsonify({'error': '非法访问'}), 403
    
    if os.path.exists(file_path):
        return send_from_directory(base_dir, filename)
    return jsonify({'error': '文件不存在'}), 404


@app.route('/code/<path:filename>')
def serve_code(filename):
    """提供代码文件"""
    base_dir = os.path.abspath('outputs')
    file_path = os.path.abspath(os.path.join(base_dir, filename))
    
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
