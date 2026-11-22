"""
Fmpostor bridge for AstrBot.

把群里的 Fmpostor 命令(#在线状态 / #订阅 / #退订 / #帮助, 以及服主在面板里加的其它状态命令)
转发给 Fmpostor 服务端, 再把服务端给出的回复发回原会话。

· 只转发命令: 命令列表从服务端拉取(每 60 秒刷新), 其它聊天内容一律不外发;
· 回复是"被动回复"(回应用户刚发的消息), QQ 官方机器人不需要群主额外开启主动发言;
· 服务端用桥接口令校验请求, 口令在 Fmpostor 面板「QQ 群房间广播」里查看。
"""

import time

import aiohttp

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

COMMANDS_TTL_SECONDS = 60
REQUEST_TIMEOUT_SECONDS = 8


@register(
    "astrbot_plugin_fmpostor",
    "SailingBoat-ovo",
    "Fmpostor 服务端桥接：群内 #在线状态 / #订阅 / #退订 / #帮助",
    "1.0.0",
)
class FmpostorBridge(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self._commands: list[str] = []
        self._prefix_commands: list[str] = ["#订阅", "#退订"]
        self._commands_at = 0.0

    # ---------- helpers ----------

    def _base_url(self) -> str:
        return str(self.config.get("server_url", "") or "").strip().rstrip("/")

    def _headers(self) -> dict:
        return {"X-Bridge-Token": str(self.config.get("bridge_token", "") or "").strip()}

    async def _refresh_commands(self) -> None:
        if time.monotonic() - self._commands_at < COMMANDS_TTL_SECONDS and self._commands:
            return

        base = self._base_url()
        if not base:
            return

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{base}/api/bot/commands", headers=self._headers()) as resp:
                    if resp.status != 200:
                        logger.warning(f"[Fmpostor] 拉取命令列表失败: HTTP {resp.status}")
                        return
                    data = await resp.json(content_type=None)
            self._commands = [c for c in data.get("commands", []) if isinstance(c, str) and c]
            prefixes = [c for c in data.get("prefixCommands", []) if isinstance(c, str) and c]
            if prefixes:
                self._prefix_commands = prefixes
            self._commands_at = time.monotonic()
        except Exception as e:  # noqa: BLE001 - 网络问题不能影响机器人的其它功能
            logger.warning(f"[Fmpostor] 拉取命令列表失败: {e}")

    def _is_our_command(self, text: str) -> bool:
        if text in self._commands:
            return True
        return any(text.startswith(p) for p in self._prefix_commands)

    # ---------- handler ----------

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        text = (event.message_str or "").strip()
        if not text or len(text) > 200:
            return

        await self._refresh_commands()
        if not self._is_our_command(text):
            return

        base = self._base_url()
        if not base:
            return

        payload = {
            "session": event.unified_msg_origin,
            "senderId": str(event.get_sender_id() or ""),
            "senderName": str(event.get_sender_name() or ""),
            "text": text,
        }

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{base}/api/bot/command", json=payload, headers=self._headers()) as resp:
                    if resp.status == 401:
                        logger.warning("[Fmpostor] 桥接口令不正确，请在插件配置里填写面板上显示的口令。")
                        return
                    if resp.status != 200:
                        logger.warning(f"[Fmpostor] 转发命令失败: HTTP {resp.status}")
                        return
                    data = await resp.json(content_type=None)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"[Fmpostor] 转发命令失败: {e}")
            return

        if not isinstance(data, dict):
            return

        reply = data.get("reply")
        if data.get("handled") and isinstance(reply, str) and reply:
            event.stop_event()
            yield event.plain_result(reply)
