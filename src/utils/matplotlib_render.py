# -*- coding: utf-8 -*-
"""将 Matplotlib Python 代码执行并生成静态图片供 Agent2 / 验证器使用。"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback
import re
from pathlib import Path
from typing import Optional, Tuple


def _clean_incompatible_params(code: str) -> str:
    """
    清理代码中不兼容的matplotlib参数。
    
    已知问题：
    1. legend() 不支持 fontfamily 参数（某些matplotlib版本）
    2. 其他可能的不兼容参数
    
    解决方案：移除这些参数，保留其他参数
    """
    # 移除 legend() 中的 fontfamily 参数
    # 处理多种情况：
    # 1. fontfamily='...'
    # 2. fontfamily="..."
    # 3. 参数在中间或末尾
    
    # 方法1: 移除 fontfamily 参数及其前面的逗号
    code = re.sub(
        r',\s*fontfamily\s*=\s*["\'][^"\']*["\']',
        '',
        code
    )
    
    # 方法2: 如果 fontfamily 是第一个参数（罕见但可能）
    code = re.sub(
        r'(\()\s*fontfamily\s*=\s*["\'][^"\']*["\']\s*,\s*',
        r'\1',
        code
    )
    
    # 方法3: 如果 fontfamily 是唯一参数（极罕见）
    code = re.sub(
        r'(\()\s*fontfamily\s*=\s*["\'][^"\']*["\']\s*(\))',
        r'\1\2',
        code
    )
    
    return code


def render_matplotlib_code_to_png(
    python_code: str,
    out_png: str,
    timeout_seconds: int = 30,
) -> Tuple[Optional[str], Optional[str]]:
    """
    执行 Matplotlib Python 代码并生成 PNG 图片。
    
    参数:
        python_code: Matplotlib 绘图的 Python 代码
        out_png: 输出 PNG 文件路径
        timeout_seconds: 执行超时时间（秒）
    
    返回:
        (图片路径, 错误信息)
        - 成功: (out_png, None)
        - 失败: (None, error_message)
    
    代码要求:
        1. 必须包含 plt.savefig(output_path) 调用
        2. 不要包含 plt.show() 调用
        3. output_path 变量会由本函数注入
    """
    # 清理代码中的不兼容参数
    python_code = _clean_incompatible_params(python_code)
    
    # 确保输出目录存在
    out_png = str(Path(out_png).resolve())
    out_dir = os.path.dirname(out_png)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    # 预检查：代码中是否包含危险操作
    dangerous_patterns = [
        'os.system',
        'subprocess.',
        'eval(',
        'exec(',
        '__import__',
        'open(',  # 除了 plt.savefig 需要的文件操作
    ]
    
    code_lower = python_code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower and pattern != 'open(':
            return None, f"代码包含潜在危险操作: {pattern}"
    
    # 检查是否包含 savefig 调用
    if 'savefig' not in code_lower and 'output_path' not in code_lower:
        return None, "代码缺少 plt.savefig(output_path) 调用"
    
    # 使用子进程执行代码（隔离环境，支持超时）
    return _execute_in_subprocess(python_code, out_png, timeout_seconds)


def _execute_in_subprocess(
    python_code: str,
    out_png: str,
    timeout_seconds: int,
) -> Tuple[Optional[str], Optional[str]]:
    """
    在子进程中执行代码，支持超时控制。
    """
    import subprocess
    
    # 创建临时 Python 脚本
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as tmp_file:
        tmp_script = tmp_file.name
        
        # 构建完整的执行脚本
        full_script = _build_execution_script(python_code, out_png)
        tmp_file.write(full_script)
    
    try:
        # 执行子进程
        result = subprocess.run(
            [sys.executable, tmp_script],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=os.path.dirname(out_png) or '.',
        )
        
        # 检查执行结果
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return None, f"代码执行失败:\n{error_msg}"
        
        # 检查文件是否生成
        if not os.path.isfile(out_png):
            return None, f"代码执行成功但未生成图片文件: {out_png}"
        
        return out_png, None
    
    except subprocess.TimeoutExpired:
        return None, f"代码执行超时（{timeout_seconds}秒）"
    
    except Exception as e:
        return None, f"执行过程异常: {str(e)}"
    
    finally:
        # 清理临时文件
        try:
            os.unlink(tmp_script)
        except Exception:
            pass


def _build_execution_script(user_code: str, output_path: str) -> str:
    """
    构建完整的执行脚本，包含环境设置和错误处理。
    """
    script = f'''# -*- coding: utf-8 -*-
"""自动生成的 Matplotlib 执行脚本"""
import sys
import os
import warnings

# 抑制警告
warnings.filterwarnings('ignore')

# 设置 Matplotlib 后端为非交互式
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np

# 尝试导入 pandas（可选）
try:
    import pandas as pd
except ImportError:
    pd = None

# 设置中文字体支持
try:
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial']
    matplotlib.rcParams['axes.unicode_minus'] = False
except Exception:
    pass

# 注入 output_path 变量
output_path = r"{output_path}"

# 确保输出目录存在
output_dir = os.path.dirname(output_path)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)

try:
    # 执行用户代码
{_indent_code(user_code, 4)}
    
    # 确保所有图形都已保存
    plt.close('all')
    
except Exception as e:
    import traceback
    print(f"执行错误: {{e}}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
'''
    return script


def _indent_code(code: str, spaces: int) -> str:
    """
    为代码添加缩进。
    """
    indent = ' ' * spaces
    lines = code.splitlines()
    return '\n'.join(indent + line if line.strip() else '' for line in lines)


def _execute_in_namespace(
    python_code: str,
    out_png: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    在当前进程的隔离命名空间中执行代码（备用方案，不支持超时）。
    
    注意: 此方法不支持超时控制，建议使用 _execute_in_subprocess。
    """
    # 设置 Matplotlib 后端
    import matplotlib
    matplotlib.use('Agg')
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    # 设置中文字体
    try:
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
    except Exception:
        pass
    
    # 尝试导入 pandas
    try:
        import pandas as pd
    except ImportError:
        pd = None
    
    # 构建执行命名空间
    namespace = {
        '__builtins__': __builtins__,
        'output_path': out_png,
        'plt': plt,
        'np': np,
        'pd': pd,
        'os': os,  # 允许基本的 os 操作
    }
    
    try:
        # 执行代码
        exec(python_code, namespace)
        
        # 关闭所有图形
        plt.close('all')
        
        # 检查文件是否生成
        if not os.path.isfile(out_png):
            return None, f"代码执行成功但未生成图片文件: {out_png}"
        
        return out_png, None
    
    except SyntaxError as e:
        return None, f"语法错误: {e}\n位置: 第 {e.lineno} 行"
    
    except Exception as e:
        error_trace = traceback.format_exc()
        return None, f"运行时错误: {e}\n\n{error_trace}"
    
    finally:
        # 确保清理
        try:
            plt.close('all')
        except Exception:
            pass
