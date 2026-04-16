# -*- coding: utf-8 -*-
"""将 ECharts 内联 JS 写入 HTML，并用 Playwright 截图生成「生成图表」供 Agent2 / 验证器使用。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


ECHARTS_CDN = "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <script src="{cdn}"></script>
  <style>html,body{{margin:0;padding:0;background:#fff;}}</style>
</head>
<body>
  <div id="main" style="width:{w}px;height:{h}px;"></div>
  <script>
{script}
  </script>
</body>
</html>
"""


def build_html_file(
    inline_js: str,
    out_html: str,
    width: int = 900,
    height: int = 600,
) -> str:
    """写入完整 HTML 文件，返回绝对路径。"""
    ap = os.path.abspath(out_html)
    d = os.path.dirname(ap)
    if d:
        os.makedirs(d, exist_ok=True)
    body = HTML_TEMPLATE.format(cdn=ECHARTS_CDN, w=width, h=height, script=inline_js)
    path = Path(out_html).resolve()
    path.write_text(body, encoding="utf-8")
    return str(path)


def screenshot_html_to_png(
    html_path: str,
    out_png: str,
    viewport_width: int = 920,
    viewport_height: int = 640,
    wait_ms: int = 2500,
) -> Optional[str]:
    """
    使用 Playwright Chromium 对本地 HTML 截图。
    未安装 playwright 或截图失败时返回 None。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    html_path = str(Path(html_path).resolve())
    out_png = str(Path(out_png).resolve())
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": viewport_width, "height": viewport_height}
            )
            page.goto(Path(html_path).as_uri(), wait_until="networkidle", timeout=120000)
            page.wait_for_timeout(wait_ms)
            page.screenshot(path=out_png, full_page=True)
            browser.close()
        return out_png if os.path.isfile(out_png) else None
    except Exception:
        return None


def render_echarts_js_to_png(
    inline_js: str,
    out_png: str,
    out_html: str,
    width: int = 900,
    height: int = 600,
) -> Optional[str]:
    """内联 JS → HTML → PNG。"""
    html = build_html_file(inline_js, out_html, width=width, height=height)
    return screenshot_html_to_png(html, out_png)
