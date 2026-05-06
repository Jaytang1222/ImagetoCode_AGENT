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
    
    解决方案：移除这些参数
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


def _fix_histogram_shape_mismatch(code: str) -> str:
    """
    修复直方图中常见的形状不匹配问题。
    
    问题：ax.bar(bins[:-1], heights, ...) 中 bins[:-1] 和 heights 长度不匹配
    
    解决方案：
    1. 检测 ax.bar() 调用中使用 bins[:-1] 的情况
    2. 将其替换为使用区间中心点的正确方法
    3. 检测并修复 width 参数
    """
    lines = code.split('\n')
    fixed_lines = []
    bin_centers_added = False
    
    for i, line in enumerate(lines):
        # 检测 ax.bar() 调用中使用 bins[:-1] 的情况
        if 'ax.bar' in line and 'bins[:-1]' in line:
            # 提取变量名
            # 模式：ax.bar(bins[:-1], heights_var, ...)
            match = re.search(r'ax\.bar\s*\(\s*bins\s*\[\s*:-1\s*\]\s*,\s*(\w+)', line)
            if match:
                heights_var = match.group(1)
                
                # 如果还没有添加 bin_centers 计算，在这行之前添加
                if not bin_centers_added:
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent
                    
                    # 添加 bin_centers 和 bin_width 计算
                    fixed_lines.append(f"{indent_str}# 计算区间中心点和宽度（避免形状不匹配）")
                    fixed_lines.append(f"{indent_str}bin_centers = (bins[:-1] + bins[1:]) / 2")
                    fixed_lines.append(f"{indent_str}bin_width = bins[1] - bins[0] if len(bins) > 1 else 1")
                    bin_centers_added = True
                
                # 替换 bins[:-1] 为 bin_centers
                fixed_line = line.replace('bins[:-1]', 'bin_centers')
                
                # 如果 width 参数使用了固定值，替换为 bin_width
                # 模式：width=数字 或 width = 数字
                if re.search(r'width\s*=\s*\d+', fixed_line):
                    fixed_line = re.sub(r'width\s*=\s*\d+', 'width=bin_width', fixed_line)
                elif 'width' not in fixed_line:
                    # 如果没有 width 参数，添加它
                    # 在最后一个参数后、右括号前添加
                    fixed_line = fixed_line.rstrip()
                    if fixed_line.endswith(')'):
                        fixed_line = fixed_line[:-1] + ', width=bin_width)'
                    elif fixed_line.endswith(','):
                        fixed_line = fixed_line + ' width=bin_width'
                
                fixed_lines.append(fixed_line)
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def _validate_and_fix_code(code: str) -> Tuple[str, list]:
    """
    验证代码并自动修复常见问题。
    
    返回：
        (修复后的代码, 修复说明列表)
    """
    fixes_applied = []
    fixed_code = code
    
    # 修复1：检查并修复 bins[:-1] 问题
    if 'bins[:-1]' in fixed_code and 'ax.bar' in fixed_code:
        fixed_code = _fix_histogram_shape_mismatch(fixed_code)
        if fixed_code != code:
            fixes_applied.append("修复直方图 bins[:-1] 形状不匹配问题")
    
    # 修复2：检查并修复 np.histogram 错误解包
    if re.search(r'\w+\s*,\s*\w+\s*,\s*_\s*=\s*np\.histogram\s*\(', fixed_code):
        fixed_code = re.sub(
            r'(\w+)\s*,\s*(\w+)\s*,\s*_\s*=\s*np\.histogram\s*\(',
            r'\1, \2 = np.histogram(',
            fixed_code
        )
        fixes_applied.append("修复 np.histogram() 错误解包（只返回2个值）")
    
    # 修复3：移除无效的 rcParams 参数
    invalid_rcparams = [
        'font.kerning',
        'text.latex.unicode',
        'savefig.frameon',
    ]
    for param in invalid_rcparams:
        pattern = rf"plt\.rcParams\s*\[\s*['\"]" + re.escape(param) + rf"['\"]\s*\]\s*=\s*[^\n]+"
        if re.search(pattern, fixed_code):
            fixed_code = re.sub(
                pattern,
                f"# plt.rcParams['{param}'] = ...  # 已移除：无效参数",
                fixed_code
            )
            fixes_applied.append(f"移除无效的 rcParams 参数: {param}")
    
    # 修复4：检查是否缺少必要的 import
    if 'plt.' in fixed_code and 'import matplotlib.pyplot' not in fixed_code:
        fixed_code = 'import matplotlib.pyplot as plt\n' + fixed_code
        fixes_applied.append("添加缺失的 matplotlib.pyplot 导入")
    
    if 'np.' in fixed_code and 'import numpy' not in fixed_code:
        # 在第一个 import 后添加
        lines = fixed_code.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import '):
                lines.insert(i + 1, 'import numpy as np')
                break
        else:
            lines.insert(0, 'import numpy as np')
        fixed_code = '\n'.join(lines)
        fixes_applied.append("添加缺失的 numpy 导入")
    
    # 修复5：检查是否有 plt.show()（应该移除）
    if 'plt.show()' in fixed_code:
        fixed_code = fixed_code.replace('plt.show()', '# plt.show()  # 已注释：非交互环境')
        fixes_applied.append("注释掉 plt.show() 调用")
    
    # 修复6：检查是否缺少 savefig
    if 'savefig' not in fixed_code.lower():
        # 在代码末尾添加 savefig
        fixed_code = fixed_code.rstrip() + '\n\nplt.savefig(output_path, dpi=100, bbox_inches=\'tight\')\n'
        fixes_applied.append("添加缺失的 plt.savefig() 调用")
    
    return fixed_code, fixes_applied


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
    # 验证并自动修复代码中的常见问题
    python_code, fixes_applied = _validate_and_fix_code(python_code)
    
    # 如果应用了修复，记录日志（可选）
    if fixes_applied:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"自动修复了 {len(fixes_applied)} 个问题: {', '.join(fixes_applied)}")
    
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
