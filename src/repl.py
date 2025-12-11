#
# repl.py
#
# @author n1ghts4kura
# @date 2025/10/1
#

import asyncio
from typing import Deque
from collections import deque
from datetime import datetime

# *n1ghts4kura*: 这里爆红应该没事，只要依赖装了就行。2025/10/1
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.layout.controls import FormattedTextControl
import shutil
from time import monotonic

from src import logger
from src.uart import conn
from src.uart.conn import (open_serial, writeline, start_rx_thread, readline,)

class TUILogger:
    """维护上方滚动缓冲，触发界面重绘，并提供彩色渲染。"""
    def __init__(self, buffer_lines: int = 8, text_area: TextArea | None = None, show_timestamp: bool = True):
        # buffer_lines: 在无法获取渲染高度时的备用可见行数
        self.buffer_lines = buffer_lines
        # 存储更长历史，渲染时按照当前窗口高度截取可见部分
        self.lines: Deque[str] = deque(maxlen=10000)
        # 兼容旧实现：可能是 TextArea 或新的 Window + Control
        self.text_area = text_area
        self.window: Window | None = None
        self.control: FormattedTextControl | None = None
        self.show_timestamp = show_timestamp
        self.max_view_lines = 500  # 输出窗口最多显示的历史行数（避免文本过长卡顿）
        # 终端尺寸回退：用于首次渲染前估算输出区高度（约80%）
        try:
            rows = shutil.get_terminal_size().lines
        except Exception:
            rows = 24
        self._fallback_window_lines = max(1, int(rows * 0.8) - 1)
        self._last_invalidate = 0.0  # 节流重绘，缓解输入卡顿

    def attach(self, text_area: TextArea):
        # 仍保留以便兼容，但彩色渲染将使用 attach_window
        self.text_area = text_area

    def attach_window(self, window: Window, control: FormattedTextControl):
        self.window = window
        self.control = control

    def append(self, text: str, with_ts: bool | None = None):
        # 统一加时间戳（可切换）
        if with_ts is None:
            with_ts = self.show_timestamp
        if with_ts:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 毫秒精度，含日期、24h
            text = f"[{ts}] {text}"
        self.lines.append(text)

        # 通知应用重绘（节流）
        try:
            now = monotonic()
            if (now - self._last_invalidate) >= 0.016:  # ~60 FPS
                self._last_invalidate = now
                get_app().invalidate()
        except Exception:
            pass

    def _window_height(self) -> int:
        try:
            w = self.window
            if w is not None and w.render_info is not None:
                info = w.render_info
                if info is not None and getattr(info, "window_height", None) is not None:
                    return int(info.window_height)
        except Exception:
            pass
        return 0

    def _split_parts(self, line: str):
        """解析一行，拆分为 (ts, label, body)。若无则返回 None 的位置。"""
        ts = None
        label = None
        body = line
        # 解析时间戳 [....]
        if body.startswith("["):
            i = body.find("]")
            if i != -1:
                ts = body[1:i]
                body = body[i+1:].lstrip()
        # 解析标签 [发送]/[接收]/[WARN] ...
        if body.startswith("["):
            j = body.find("]")
            if j != -1:
                label = body[1:j]
                body = body[j+1:].lstrip()
        return ts, label, body

    def render_fragments(self):
        """根据当前内容和视口高度生成带样式的片段列表。"""
        content = list(self.lines)[-self.max_view_lines:]
        viewport = self._window_height() or self._fallback_window_lines
        tail = content[-viewport:]
        pad = max(0, viewport - len(tail))
        fragments = []
        # 顶部补空行以实现底部贴合
        if pad > 0:
            fragments.append(("", "\n" * pad))
        # 每行渲染
        for line in tail:
            ts, label, body = self._split_parts(line)
            if ts:
                fragments.append(("class:ts", f"[{ts}] "))
            if label:
                style = {
                    "发送": "class:label-send",
                    "接收": "class:label-recv",
                    "WARN": "class:label-warn",
                }.get(label, "class:label-other")
                fragments.append((style, f"[{label}] "))
            fragments.append(("class:body", body))
            fragments.append(("", "\n"))
        # 去掉最后一个多余换行（可选，保持一致性）
        if fragments and fragments[-1][1].endswith("\n"):
            pass
        return fragments

    def refresh(self):
        """强制重绘（用于首次渲染后矫正底对齐）。"""
        try:
            get_app().invalidate()
        except Exception:
            pass


# 移除 logger 注入：按需求只展示 TX/RX 两类数据

async def serial_reader_task(stop_event: asyncio.Event, log: TUILogger):
    """持续读取串口并更新界面顶部日志。"""
    try:
        # 使用后台队列无阻塞获取，提高高频场景性能
        while not stop_event.is_set():
            line = readline()
            if line:
                log.append(f"[接收] {line}")
            else:
                await asyncio.sleep(0.003)
    except asyncio.CancelledError:
        logger.debug("serial_reader_task 被取消。")
        raise


def build_app(stop_event: asyncio.Event, logger_view: TUILogger) -> Application:
    # 顶部 UART 输出区域（占总高度约 80%），使用可着色的 FormattedTextControl
    output_control = FormattedTextControl(text=lambda: logger_view.render_fragments(), focusable=False, show_cursor=False)
    output_area = Window(
        content=output_control,
        height=Dimension(weight=4, min=1),
        style="class:output",
        wrap_lines=True,
    )
    logger_view.attach_window(output_area, output_control)

    # 分隔符（第9行）
    separator = Window(height=1, char="─", style="class:separator")

    # 底部输入行（占总高度约 20% 的容器内，输入框靠容器底部）
    input_area = TextArea(
        prompt=HTML('<skyblue>>>> </skyblue>'),
        multiline=False,
        style="class:input",
        wrap_lines=False,
    )

    # 输入容器用权重分配高度，内部用一个空窗口把输入框“顶”到最底部
    input_container = HSplit([
        Window(),  # 占位，把输入框推到底部
        input_area,
    ], height=Dimension(weight=1, min=1))

    kb = KeyBindings()

    @kb.add("c-c")
    def _(event):
        # Ctrl+C 退出
        stop_event.set()
        event.app.exit()

    # 发送行结尾配置（仅用于显示；串口发送不再额外拼行尾，避免与 conn.writeline 自带的 ";"+EOL 重复）
    eol_mode = {"value": "none"}  # crlf | lf | cr | none

    @kb.add("enter")
    def _(event):
        # 回车发送
        text = input_area.text
        # 先复制当前文本，再清空输入框，避免 race 导致残留
        input_area.buffer.set_document(Document("", 0))
        text = text.strip()
        if not text:
            return
        # 内置命令
        if text in {":q", ":quit", ":exit", "exit", "quit"}:
            stop_event.set()
            event.app.exit()
            return
        if text in {":help", ":h", "?"}:
            logger_view.append("内置命令: :q | :quit | :exit 退出; :help 显示帮助; :eol [crlf|lf|cr|none] 设置/查看发送行结尾")
            return
        if text.startswith(":eol"):
            parts = text.split()
            if len(parts) == 1:
                logger_view.append(f"当前 EOL(仅显示用，不影响串口发送): {eol_mode['value']} (可选: crlf, lf, cr, none)")
            else:
                val = parts[1].lower()
                if val in {"crlf", "lf", "cr", "none"}:
                    eol_mode["value"] = val
                    logger_view.append(f"已设置显示用 EOL: {val}")
                else:
                    logger_view.append("无效 EOL，使用: :eol [crlf|lf|cr|none]")
            return
        # 异步写串口（立即在视图里记录 TX）
        async def _send(cmd: str):
            # 规范化：若用户已输入尾部分号，则去掉后再由 writeline 追加单个 ";"+EOL，避免出现 "cmd;;\n"。
            payload = cmd[:-1] if cmd.endswith(";") else cmd
            ok = await asyncio.to_thread(writeline, payload)
            if not ok:
                logger_view.append("[WARN] 发送失败，串口可能未连接或已断开。")
            else:
                # 即时显示已发送的数据（不等待设备回显）
                view_text = cmd
                logger_view.append(f"[发送] {view_text}")
        asyncio.create_task(_send(text))

    root = HSplit([
        output_area,    # ~90%
        separator,      # 固定 1 行
        input_container # ~10%
    ])

    style = Style.from_dict({
        # 输出区：暗背景，高对比度字体
        "output": "bg:#1e1e1e #dcdcdc",
        # 片段样式
        "ts": "#8a8a8a",  # 时间戳偏灰
        "label-send": "#00d75f bold",  # 发送：亮绿
        "label-recv": "#00afff bold",  # 接收：湖蓝
        "label-warn": "#ffd75f bold",  # 警告：琥珀
        "label-other": "#dcdcdc bold",
        "body": "#dcdcdc",
        # 分隔线：亮蓝色线条
        "separator": "bg:#1e1e1e #00afff",
        # 输入区：稍深背景，醒目提示色
        "input": "bg:#121212 #ffffff",
        # Prompt 颜色
        "prompt": "#00afff bold",
    })

    app = Application(
        layout=Layout(root, focused_element=input_area),
        key_bindings=kb,
        full_screen=True,
        mouse_support=False,
        color_depth=ColorDepth.TRUE_COLOR,
        style=style,
    )
    return app


async def amain():
    result = open_serial()
    if not result:
        # 启动失败时仅在控制台日志输出，不在 TUI 区域显示
        logger.error("无法连接到UART设备，程序退出。")
        return

    port_name = getattr(conn.serial_conn, "port", "<unknown>")
    logger.info(f"串口已打开: {port_name}")
    try:
        conn.clear_rx_queue()
    except Exception:
        pass

    start_rx_thread()
    logger.info("串口接收线程已启动")

    hs_ok: bool | None = None
    try:
        hs_ok = conn.handshake_serial()
        if hs_ok:
            logger.info("串口握手成功")
        else:
            logger.error("串口握手失败")
    except Exception as e:  # noqa: BLE001
        logger.error(f"串口握手异常: {e}")
        hs_ok = False

    stop_event = asyncio.Event()

    tui_log = TUILogger(buffer_lines=8)
    app = build_app(stop_event, tui_log)

    # 在界面顶部先提示当前串口状态
    tui_log.append(f"[INFO] 串口已打开: {port_name}")
    tui_log.append("[INFO] 串口接收线程已启动")
    if hs_ok is True:
        tui_log.append("[INFO] 串口握手成功")
    elif hs_ok is False:
        tui_log.append("[WARN] 串口握手失败，可能无法通信")

    # 首次渲染后对齐：探测输出区视口高度，修正底部对齐
    async def _probe_viewport_and_align():
        for _ in range(100):  # 最多约 2 秒
            await asyncio.sleep(0.02)
            try:
                if tui_log.window and tui_log.window.render_info:
                    h = getattr(tui_log.window.render_info, "window_height", None)
                    if h:
                        tui_log._fallback_window_lines = int(h)
                        tui_log.refresh()
                        break
            except Exception:
                pass

    asyncio.create_task(_probe_viewport_and_align())

    # 启动后台接收协程（串口线程已提前启动）
    reader = asyncio.create_task(serial_reader_task(stop_event, tui_log))

    try:
        await app.run_async()
    except KeyboardInterrupt:
        pass
        stop_event.set()
    finally:
        if not reader.done():
            reader.cancel()
        await asyncio.gather(reader, return_exceptions=True)
        try:
            conn.stop_rx_thread()
            logger.info("串口接收线程已停止")
            tui_log.append("[INFO] 串口接收线程已停止")
        except Exception:
            pass
        try:
            conn.close_serial()
            logger.info("串口已关闭")
            tui_log.append("[INFO] 串口已关闭")
        except Exception:
            pass



def main():
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        # 兜底处理
        logger.info("收到 Ctrl+C，退出。")


if __name__ == "__main__":
    main()