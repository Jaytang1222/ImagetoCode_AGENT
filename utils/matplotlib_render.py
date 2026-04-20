# -*- coding: utf-8 -*-
"""将 Matplotlib Python 代码执行并生成静态图片供 Agent2 / 验证器使用。"""
from __future__ import annotations

import os
import re
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Optional, Tuple


def _convert_rgba_strings(python_code: str) -> str:
    """
    将生成的 Python 代码中 CSS 格式的 'rgba(R,G,B,A)' 字符串
    转换为 Matplotlib 支持的元组 (R/255, G/255, B/255, A)。

    Matplotlib 不支持 'rgba(255,255,255,0.5)' 这种字符串写法，
    但接受 (1.0, 1.0, 1.0, 0.5) 的元组格式。
    """
    # 匹配带引号的 rgba() 字符串，整体替换为元组（不带引号）
    pattern = r"""(['"])(?:rgba|RGBA)\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?|\.?\d+)\s*\)\1"""
    def _replace_rgba(match: re.Match) -> str:
        r, g, b, a = match.group(2), match.group(3), match.group(4), match.group(5)
        return f'({float(r)/255:.4f}, {float(g)/255:.4f}, {float(b)/255:.4f}, {a})'
    converted = re.sub(pattern, _replace_rgba, python_code, flags=re.IGNORECASE)
    return converted


def _fix_pie_unpacking(python_code: str) -> str:
    """
    修复常见的饼图解包错误：当 pie() 没有提供 autopct 参数时，
    它只返回两个值 (wedges, texts)，但 LLM 经常错误地解包三个变量。
    """
    # 匹配 wedges, texts, autotexts = ax.pie(...) 模式，且 pie 调用中没有 autopct 参数
    lines = python_code.splitlines()
    fixed_lines = []
    for line in lines:
        # 检查是否包含 .pie( 并且有三个变量解包
        if '.pie(' in line and '=' in line:
            # 简单的模式匹配：变量1, 变量2, 变量3 = ... .pie(...)
            # 更稳健的做法：检查等号左边是否有三个逗号分隔的变量
            left, right = line.split('=', 1)
            left_vars = [v.strip() for v in left.split(',')]
            if len(left_vars) == 3 and 'autopct' not in right.lower():
                # 替换为两个变量解包
                new_left = ', '.join(left_vars[:2])
                fixed_line = f'{new_left} = {right}'
                fixed_lines.append(fixed_line)
                continue
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)


def _sanitize_matplotlib_code(python_code: str) -> str:
    """
    对生成的 Matplotlib 代码进行清理和修复，处理常见错误。
    """
    code = python_code
    code = _convert_rgba_strings(code)
    code = _fix_pie_unpacking(code)
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
    # 预清理：修复常见 Matplotlib 代码问题
    safe_code = _sanitize_matplotlib_code(user_code)
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
{_indent_code(safe_code, 4)}

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
        # 预清理：修复常见 Matplotlib 代码问题
        safe_code = _sanitize_matplotlib_code(python_code)
        # 执行代码
        exec(safe_code, namespace)
        
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
