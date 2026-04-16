# -*- coding: utf-8 -*-
"""
<<<<<<< HEAD
Flask 后端服务：提供多智能体图表复现的 REST API
支持实时状态推送和任务管理
"""
from __future__ import annotations

import os
import sys
import uuid
import threading
import time
from datetime import datetime
from typing import Dict, Optional
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
=======
多智能体图表复现主入口：Agent1→2→3→4 + 多维验证器（见 agent_pipeline.py）。

使用前请设置环境变量 DASHSCOPE_API_KEY，并安装依赖：
  pip install -r requirements.txt
  playwright install chromium
"""
from __future__ import annotations

import argparse
import os
import sys
>>>>>>> 2ac731af3f1338ccdc6d8b06e9a74d82350364e0

# 保证从项目根目录可导入本地模块
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from agent_pipeline import run_full_pipeline

<<<<<<< HEAD
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 任务状态存储
tasks: Dict[str, dict] = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def update_task_status(task_id: str, status: str, progress: int = 0, message: str = "", data: dict = None):
    """更新任务状态"""
    if task_id in tasks:
        tasks[task_id].update({
            'status': status,
            'progress': progress,
            'message': message,
            'updated_at': datetime.now().isoformat()
        })
        if data:
            tasks[task_id]['data'].update(data)


def run_pipeline_task(task_id: str, input_path: str, max_loops: int, threshold: float):
    """在后台运行完整的 Agent 流水线"""
    try:
        update_task_status(task_id, 'running', 5, '正在初始化任务...')
        
        # 使用当前时间作为输出目录名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(OUTPUT_FOLDER, timestamp)
        os.makedirs(out_dir, exist_ok=True)
        
        # 导入必要的模块以监控进度
        import sys
        _ROOT = os.path.dirname(os.path.abspath(__file__))
        if _ROOT not in sys.path:
            sys.path.insert(0, _ROOT)
        
        from agent1_code_generation import agent1_generate_code
        from agent2_visual_judgment import agent2_chart_evaluation_report
        from agent3_code_evaluation import agent3_code_evaluation_report
        from agent4_feedback_revision import agent4_feedback_optimize_code
        from echarts_render import render_echarts_js_to_png
        from multidim_validator import multidimensional_validate
        from pathlib import Path
        from datetime import datetime as dt
        
        code_path = None
        html_path = os.path.join(out_dir, "preview.html")
        gen_png = os.path.join(out_dir, "generated_chart.png")
        last_summary = ""
        code = None
        
        for loop in range(max_loops):
            loop_progress_base = (loop / max_loops) * 100
            
            if loop == 0:
                update_task_status(task_id, 'running', int(loop_progress_base + 5), '[Agent1] 代码生成中...')
                print(f"\n{'='*20} 第 {loop + 1}/{max_loops} 轮 {'='*20}")
                print("[Agent1] 代码生成(VLM)…")
                code = agent1_generate_code(input_path)
            else:
                update_task_status(task_id, 'running', int(loop_progress_base + 5), f'[迭代] 第{loop+1}轮优化中...')
                print(f"\n{'='*20} 第 {loop + 1}/{max_loops} 轮 {'='*20}")
                print("[迭代] 在上一轮 Agent4 输出上继续优化…")
            
            timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
            code_path = os.path.join(out_dir, f"echarts_{timestamp}.js")
            Path(code_path).write_text(code, encoding="utf-8")
            
            update_task_status(task_id, 'running', int(loop_progress_base + 15), '[渲染] 生成预览图中...')
            print(f"[渲染] 生成预览 HTML / 截图 → {gen_png}")
            png = render_echarts_js_to_png(code, gen_png, html_path)
            if not png:
                msg = "无法生成复现图 PNG。请执行: pip install playwright && playwright install chromium"
                print("[错误]", msg)
                update_task_status(task_id, 'error', 0, msg)
                return
            
            update_task_status(task_id, 'running', int(loop_progress_base + 30), '[Agent2] 视觉评判中...')
            print("[Agent2] 视觉评判(双图 VLM)…")
            chart_report = agent2_chart_evaluation_report(input_path, png)
            Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
                chart_report, encoding="utf-8"
            )
            
            update_task_status(task_id, 'running', int(loop_progress_base + 50), '[Agent3] 代码评估中...')
            print("[Agent3] 代码评判(LLM)…")
            code_report = agent3_code_evaluation_report(code, chart_report)
            Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
                code_report, encoding="utf-8"
            )
            
            update_task_status(task_id, 'running', int(loop_progress_base + 65), '[Agent4] 反馈优化中...')
            print("[Agent4] 反馈优化修订(LLM)…")
            code_new = agent4_feedback_optimize_code(code, code_report, chart_report)
            Path(os.path.join(out_dir, f"current_echarts_after_agent4_r{loop+1}.js")).write_text(
                code_new, encoding="utf-8"
            )
            
            update_task_status(task_id, 'running', int(loop_progress_base + 80), '[渲染] Agent4输出再截图...')
            print("[渲染] Agent4 输出再截图…")
            png_final = render_echarts_js_to_png(code_new, gen_png, html_path)
            if not png_final:
                last_summary = "Agent4 后截图失败"
                update_task_status(task_id, 'error', 0, last_summary)
                return
            
            update_task_status(task_id, 'running', int(loop_progress_base + 90), '[验证器] 多维验证中...')
            print("[多维验证器] 对比原图与复现图…")
            ok, score, last_summary = multidimensional_validate(
                input_path, png_final, threshold=threshold
            )
            print(f"  → score={score:.4f} pass={ok} | {last_summary}")

            Path(os.path.join(out_dir, f"validator_round{loop+1}.txt")).write_text(
                f"pass={ok}\nscore={score}\n{last_summary}",
                encoding="utf-8",
            )

            if ok:
                Path(code_path).write_text(code_new, encoding="utf-8")
                update_task_status(task_id, 'completed', 100, '验证通过！', {
                    'code_path': code_path,
                    'png_path': png_final,
                    'summary': last_summary,
                    'html_preview': html_path
                })
                print("[完成] 验证通过，最终代码已写入:", code_path)
                return

            code = code_new
        
        # 未能在限定轮数内通过
        update_task_status(task_id, 'failed', 100, f'未能在限定轮数内通过验证: {last_summary}', {
            'code_path': code_path,
            'png_path': gen_png,
            'summary': last_summary,
            'html_preview': html_path
        })
        print("[结束] 未能在限定轮数内通过验证，返回最后一版 Agent4 代码。")
            
    except Exception as e:
        import traceback
        error_msg = f'任务执行出错: {str(e)}\n{traceback.format_exc()}'
        print(error_msg)
        update_task_status(task_id, 'error', 0, error_msg)


@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory('frontend', 'index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传参考图片并创建任务"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传 PNG 或 JPG 图片'}), 400
    
    # 保存上传的文件
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    # 获取参数
    max_loops = int(request.form.get('max_loops', 5))
    threshold = float(request.form.get('threshold', 0.75))
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        'id': task_id,
        'status': 'pending',
        'progress': 0,
        'message': '任务已创建，等待启动...',
        'input_file': filepath,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'params': {
            'max_loops': max_loops,
            'threshold': threshold
        },
        'data': {}
    }
    
    # 在后台线程中运行任务
    thread = threading.Thread(
        target=run_pipeline_task,
        args=(task_id, filepath, max_loops, threshold)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'message': '任务已创建'
    }), 201


@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(tasks[task_id])


@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """列出所有任务"""
    return jsonify(list(tasks.values()))


@app.route('/api/outputs', methods=['GET'])
def list_outputs():
    """列出 outputs 目录下的所有任务文件夹"""
    try:
        if not os.path.exists(OUTPUT_FOLDER):
            return jsonify([])
        
        # 获取所有子目录
        directories = []
        for item in sorted(os.listdir(OUTPUT_FOLDER), reverse=True):  # 按时间倒序
            item_path = os.path.join(OUTPUT_FOLDER, item)
            if os.path.isdir(item_path):
                # 获取目录信息
                stat = os.stat(item_path)
                directories.append({
                    'name': item,
                    'path': item_path,
                    'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size': sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(item_path)
                        for filename in filenames
                    )
                })
        
        return jsonify(directories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/code/<task_id>')
def download_code(task_id):
    """下载生成的代码文件"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    code_path = tasks[task_id]['data'].get('code_path')
    if not code_path or not os.path.exists(code_path):
        return jsonify({'error': '代码文件不存在'}), 404
    
    return send_file(code_path, as_attachment=True, download_name='echarts_code.js')


@app.route('/api/download/image/<task_id>')
def download_image(task_id):
    """下载生成的图表图片"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    png_path = tasks[task_id]['data'].get('png_path')
    if not png_path or not os.path.exists(png_path):
        return jsonify({'error': '图片文件不存在'}), 404
    
    return send_file(png_path, as_attachment=True, download_name='generated_chart.png')


@app.route('/api/preview/<task_id>')
def preview_html(task_id):
    """预览 HTML 页面"""
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    html_path = tasks[task_id]['data'].get('html_preview')
    if not html_path or not os.path.exists(html_path):
        return jsonify({'error': '预览文件不存在'}), 404
    
    return send_file(html_path)


@app.route('/api/preview/dir/<dir_name>')
def preview_html_by_dir(dir_name):
    """通过目录名预览 HTML 页面"""
    html_path = os.path.join(OUTPUT_FOLDER, dir_name, 'preview.html')
    if not os.path.exists(html_path):
        return jsonify({'error': '预览文件不存在'}), 404
    
    return send_file(html_path)


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'active_tasks': len([t for t in tasks.values() if t['status'] in ['pending', 'running']])
    })


if __name__ == "__main__":
    print("="*60)
    print("多智能体图表复现系统 - Web 服务")
    print("="*60)
    print("请在浏览器中访问: http://localhost:5000")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)
=======

def main() -> None:
    parser = argparse.ArgumentParser(description="多智能体 ECharts 图表复现流水线")
    parser.add_argument(
        "-i",
        "--input",
        default="input.png",
        help="输入参考图表图片路径",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="outputs",
        help="输出目录（代码、HTML、截图、报告）",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=5,
        help="最大迭代轮数",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="验证器通过分数阈值（0~1）",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"未找到输入图片: {args.input}")
        print("请将参考图放在该路径，或使用 -i 指定。")
        sys.exit(1)

    ok, code_path, png_path, summary = run_full_pipeline(
        input_chart_image=args.input,
        out_dir=args.out,
        max_loops=args.max_loops,
        threshold=args.threshold,
    )
    print("\n--- 结果 ---")
    print("验证通过:", ok)
    print("代码文件:", code_path)
    print("渲染图:", png_path)
    print("摘要:", summary)


if __name__ == "__main__":
    main()
>>>>>>> 2ac731af3f1338ccdc6d8b06e9a74d82350364e0
