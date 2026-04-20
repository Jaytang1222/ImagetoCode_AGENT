# -*- coding: utf-8 -*-
"""将 ECharts JS 代码执行并生成截图供验证器使用。"""
from __future__ import annotations

import os
import asyncio
from pathlib import Path
from typing import Optional, Tuple

from playwright.async_api import async_playwright


async def render_echarts_code_to_png(
    echarts_js: str,
    out_png: str,
    width: int = 800,
    height: int = 600,
    timeout_ms: int = 30000,
) -> Tuple[Optional[str], Optional[str]]:
    """
    使用 Playwright 渲染 ECharts 代码并生成 PNG。

    参数:
        echarts_js: ECharts option 配置代码
        out_png: 输出 PNG 路径
        width: 画布宽度（像素）
        height: 画布高度（像素）
        timeout_ms: 超时时间（毫秒）

    返回:
        (图片路径，错误信息)
    """
    out_png = str(Path(out_png).resolve())
    out_dir = os.path.dirname(out_png)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    try:
        async with async_playwright() as p:
            # 启动 Chromium
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": width, "height": height},
            )
            page = await context.new_page()

            # 构建 HTML 页面
            html_content = _build_echarts_html(echarts_js, width, height)

            # 设置页面内容
            await page.set_content(html_content, wait_until="networkidle")

            # 等待图表渲染完成
            await page.wait_for_function(
                "() => document.querySelector('#main') !== null",
                timeout=5000,
            )

            # 额外等待动画完成（如果有）
            await page.wait_for_timeout(1000)

            # 截图
            await page.screenshot(
                path=out_png,
                full_page=False,
                type="png",
            )

            await browser.close()

            if os.path.isfile(out_png):
                return out_png, None
            else:
                return None, "截图文件未生成"

    except asyncio.TimeoutError:
        return None, f"渲染超时（{timeout_ms}ms）"
    except Exception as e:
        return None, f"渲染失败：{str(e)}"


def _build_echarts_html(echarts_js: str, width: int, height: int) -> str:
    """
    构建包含 ECharts 的完整 HTML 页面
    """
    # 处理 JS 代码 - 确保是有效的 option 对象
    js_content = echarts_js.strip()

    # 如果代码包含 var option = ... 或 const option = ...，提取 option 值
    import re
    match = re.search(r'(?:var|let|const)\s+option\s*=\s*([\s\S]+);?$', js_content)
    if match:
        js_content = match.group(1).strip()
        if js_content.endswith(';'):
            js_content = js_content[:-1]

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECharts 渲染</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: {width}px;
            height: {height}px;
            overflow: hidden;
        }}
        #main {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script>
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);

        var option;

        try {{
            option = {js_content};
            myChart.setOption(option);
        }} catch (e) {{
            console.error('ECharts 渲染错误：', e);
            document.body.innerHTML = '<div style="color:red;padding:20px;">渲染错误：' + e.message + '</div>';
        }}
    </script>
</body>
</html>"""


def render_echarts_sync(
    echarts_js: str,
    out_png: str,
    **kwargs
) -> Tuple[Optional[str], Optional[str]]:
    """
    同步包装器 - 在同步代码中调用异步渲染函数
    """
    import asyncio

    try:
        # 尝试获取或创建事件循环
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # 在 Jupyter 等已有事件循环环境中
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                render_echarts_code_to_png(echarts_js, out_png, **kwargs)
            )
            return future.result()
    else:
        return loop.run_until_complete(
            render_echarts_code_to_png(echarts_js, out_png, **kwargs)
        )
