import asyncio
import json
from typing import Any

from astrbot.api import AstrBotConfig, star
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.core import logger
from astrbot.core.provider.register import llm_tools

DANGEROUS_APIS = {
    "set_group_ban", "set_group_kick", "set_group_whole_ban",
    "set_group_admin", "set_group_name", "set_group_leave",
    "set_group_card", "set_group_special_title", "delete_friend",
    "send_group_sign", "set_essence_msg", "delete_essence_msg",
    "_send_group_notice", "set_qq_avatar", "set_self_longnick",
    "send_poke", "group_poke", "friend_poke",
    "send_group_forward_msg", "send_private_forward_msg",
    "send_forward_msg", "send_group_ai_record",
    "send_like", "send_private_msg", "send_group_msg", "send_msg",
    "delete_msg", "set_friend_add_request", "set_group_add_request",
    "upload_group_file", "delete_group_file", "create_group_file_folder",
    "delete_group_folder", "set_qq_profile", "_set_model_show",
    "_del_group_notice", "mark_msg_as_read", "_mark_all_as_read",
    "set_input_status", "set_msg_emoji_like",
}

NAPCAT_APIS: list[dict[str, Any]] = [
    # ==================== OneBot V11 消息 ====================
    {"name": "send_private_msg", "desc": "发送私聊消息", "params": {"user_id": 0, "message": []}, "danger": True},
    {"name": "send_group_msg", "desc": "发送群消息", "params": {"group_id": 0, "message": []}, "danger": True},
    {"name": "send_msg", "desc": "发送消息（自动判断私聊/群聊）", "params": {"user_id": 0, "group_id": 0, "message": []}, "danger": True},
    {"name": "delete_msg", "desc": "撤回消息", "params": {"message_id": 0}, "danger": True},
    {"name": "get_msg", "desc": "获取历史消息详情", "params": {"message_id": 0}, "danger": False},
    {"name": "get_forward_msg", "desc": "获取合并转发消息内容", "params": {"id": ""}, "danger": False},
    {"name": "send_like", "desc": "给好友点赞", "params": {"user_id": 0, "times": 1}, "danger": True},
    {"name": "get_record", "desc": "获取语音文件", "params": {"file": "", "out_format": "mp3"}, "danger": False},
    {"name": "get_image", "desc": "获取图片文件", "params": {"file": ""}, "danger": False},

    # ==================== OneBot V11 群管 ====================
    {"name": "set_group_kick", "desc": "群聊踢出成员", "params": {"group_id": 0, "user_id": 0, "reject_add_request": False}, "danger": True},
    {"name": "set_group_ban", "desc": "禁言/解禁群成员（duration秒，0解禁）", "params": {"group_id": 0, "user_id": 0, "duration": 60}, "danger": True},
    {"name": "set_group_whole_ban", "desc": "开启/关闭全员禁言", "params": {"group_id": 0, "enable": True}, "danger": True},
    {"name": "set_group_admin", "desc": "设置/取消群管理员", "params": {"group_id": 0, "user_id": 0, "enable": True}, "danger": True},
    {"name": "set_group_card", "desc": "修改成员的群名片/群昵称", "params": {"group_id": 0, "user_id": 0, "card": ""}, "danger": True},
    {"name": "set_group_name", "desc": "修改群名称", "params": {"group_id": 0, "group_name": ""}, "danger": True},
    {"name": "set_group_leave", "desc": "退出/解散群聊", "params": {"group_id": 0, "is_dismiss": False}, "danger": True},
    {"name": "set_group_special_title", "desc": "设置群专属头衔", "params": {"group_id": 0, "user_id": 0, "special_title": "", "duration": -1}, "danger": True},
    {"name": "set_group_add_request", "desc": "处理加群请求/邀请", "params": {"flag": "", "sub_type": "add", "approve": True, "reason": ""}, "danger": True},
    {"name": "get_group_info", "desc": "获取群聊基本信息（群名、人数、群主等）", "params": {"group_id": 0, "no_cache": False}, "danger": False},
    {"name": "get_group_list", "desc": "获取机器人加入的所有群列表", "params": {}, "danger": False},
    {"name": "get_group_member_info", "desc": "获取群内某成员信息（群名片、QQ号等）", "params": {"group_id": 0, "user_id": 0, "no_cache": False}, "danger": False},
    {"name": "get_group_member_list", "desc": "获取群全部成员列表", "params": {"group_id": 0}, "danger": False},
    {"name": "get_group_honor_info", "desc": "获取群荣誉信息（龙王、群聊之火等）", "params": {"group_id": 0, "type": "talkative"}, "danger": False},

    # ==================== OneBot V11 好友 & 账号 ====================
    {"name": "get_stranger_info", "desc": "获取陌生人QQ信息（昵称等）", "params": {"user_id": 0, "no_cache": False}, "danger": False},
    {"name": "get_friend_list", "desc": "获取好友列表", "params": {}, "danger": False},
    {"name": "get_login_info", "desc": "获取当前登录账号信息（QQ号、昵称）", "params": {}, "danger": False},
    {"name": "set_friend_add_request", "desc": "处理加好友请求", "params": {"flag": "", "approve": True, "remark": ""}, "danger": True},
    {"name": "can_send_image", "desc": "检查是否能发送图片", "params": {}, "danger": False},
    {"name": "can_send_record", "desc": "检查是否能发送语音", "params": {}, "danger": False},
    {"name": "get_status", "desc": "获取机器人运行状态", "params": {}, "danger": False},
    {"name": "get_version_info", "desc": "获取机器人/协议端版本信息", "params": {}, "danger": False},
    {"name": "get_cookies", "desc": "获取 Cookies", "params": {"domain": "qq.com"}, "danger": False},
    {"name": "get_csrf_token", "desc": "获取 CSRF Token", "params": {}, "danger": False},
    {"name": "get_credentials", "desc": "获取 QQ 相关凭证", "params": {"domain": "qq.com"}, "danger": False},
    {"name": "clean_cache", "desc": "清理缓存", "params": {}, "danger": False},

    # ==================== go-cqhttp 扩展 - 账号 ====================
    {"name": "set_qq_profile", "desc": "设置QQ个人资料（昵称、公司等）", "params": {"nickname": "", "company": "", "email": "", "college": "", "personal_note": ""}, "danger": True},
    {"name": "_get_model_show", "desc": "获取在线机型展示", "params": {"model": ""}, "danger": False},
    {"name": "_set_model_show", "desc": "设置在线机型展示", "params": {"model": "", "model_show": ""}, "danger": True},
    {"name": "get_online_clients", "desc": "获取当前在线设备列表", "params": {"no_cache": False}, "danger": False},
    {"name": "delete_friend", "desc": "删除好友", "params": {"user_id": 0}, "danger": True},

    # ==================== go-cqhttp 扩展 - 消息 ====================
    {"name": "mark_msg_as_read", "desc": "标记消息已读", "params": {}, "danger": True},
    {"name": "send_group_forward_msg", "desc": "发送群聊合并转发消息", "params": {"group_id": 0, "messages": []}, "danger": True},
    {"name": "send_private_forward_msg", "desc": "发送私聊合并转发消息", "params": {"user_id": 0, "messages": []}, "danger": True},
    {"name": "get_group_msg_history", "desc": "获取群聊消息历史记录", "params": {"group_id": 0, "message_seq": 0, "count": 20}, "danger": False},

    # ==================== go-cqhttp 扩展 - 群管 ====================
    {"name": "get_group_system_msg", "desc": "获取群系统消息", "params": {}, "danger": False},
    {"name": "get_essence_msg_list", "desc": "获取群精华消息列表", "params": {"group_id": 0}, "danger": False},
    {"name": "get_group_at_all_remain", "desc": "获取群 @全体成员 剩余次数", "params": {"group_id": 0}, "danger": False},
    {"name": "set_group_portrait", "desc": "设置群头像", "params": {"group_id": 0, "file": "", "cache": 1}, "danger": True},
    {"name": "set_essence_msg", "desc": "设为精华消息", "params": {"message_id": 0}, "danger": True},
    {"name": "delete_essence_msg", "desc": "取消精华消息", "params": {"message_id": 0}, "danger": True},
    {"name": "send_group_sign", "desc": "群打卡", "params": {"group_id": 0}, "danger": True},
    {"name": "_send_group_notice", "desc": "发送群公告", "params": {"group_id": 0, "content": ""}, "danger": True},
    {"name": "_get_group_notice", "desc": "获取群公告列表", "params": {"group_id": 0}, "danger": False},

    # ==================== go-cqhttp 扩展 - 文件 ====================
    {"name": "upload_group_file", "desc": "上传文件到群聊", "params": {"group_id": 0, "file": "", "name": "", "folder": ""}, "danger": True},
    {"name": "delete_group_file", "desc": "删除群文件", "params": {"group_id": 0, "file_id": "", "busid": 0}, "danger": True},
    {"name": "create_group_file_folder", "desc": "创建群文件夹", "params": {"group_id": 0, "name": "", "parent_id": "/"}, "danger": True},
    {"name": "delete_group_folder", "desc": "删除群文件夹", "params": {"group_id": 0, "folder_id": ""}, "danger": True},
    {"name": "get_group_file_system_info", "desc": "获取群文件系统信息", "params": {"group_id": 0}, "danger": False},
    {"name": "get_group_root_files", "desc": "获取群根目录文件列表", "params": {"group_id": 0}, "danger": False},
    {"name": "get_group_files_by_folder", "desc": "获取群子目录文件列表", "params": {"group_id": 0, "folder_id": ""}, "danger": False},
    {"name": "get_group_file_url", "desc": "获取群文件下载链接", "params": {"group_id": 0, "file_id": "", "busid": 0}, "danger": False},
    {"name": "upload_private_file", "desc": "上传私聊文件", "params": {"user_id": 0, "file": "", "name": ""}, "danger": True},
    {"name": "download_file", "desc": "下载文件到缓存", "params": {"url": "", "thread_count": 3, "headers": []}, "danger": False},

    # ==================== go-cqhttp 扩展 - 工具 ====================
    {"name": "ocr_image", "desc": "OCR 识别图片中的文字", "params": {"image": ""}, "danger": False},
    {"name": "check_url_safely", "desc": "检查链接安全性", "params": {"url": ""}, "danger": False},

    # ==================== NapCat 扩展 - 签到 & 互动 ====================
    {"name": "set_group_sign", "desc": "群签到", "params": {"group_id": ""}, "danger": True},
    {"name": "group_poke", "desc": "群聊戳一戳某个成员", "params": {"group_id": 0, "user_id": 0}, "danger": True},
    {"name": "friend_poke", "desc": "私聊戳一戳好友", "params": {"user_id": 0}, "danger": True},
    {"name": "send_poke", "desc": "通用戳一戳（群聊/私聊）", "params": {"user_id": 0, "group_id": 0}, "danger": True},

    # ==================== NapCat 扩展 - 推荐 ====================
    {"name": "ArkSharePeer", "desc": "推荐好友/群聊卡片", "params": {"user_id": "", "phoneNumber": "", "group_id": ""}, "danger": True},
    {"name": "ArkShareGroup", "desc": "推荐群聊卡片", "params": {"group_id": ""}, "danger": True},

    # ==================== NapCat 扩展 - 账号 ====================
    {"name": "get_robot_uin_range", "desc": "获取机器人QQ号区间范围", "params": {}, "danger": False},
    {"name": "set_online_status", "desc": "设置在线状态（在线/隐身/离开等）", "params": {"status": 11, "ext_status": 0, "battery_status": 0}, "danger": True},
    {"name": "get_friends_with_category", "desc": "获取按分类整理的好友列表", "params": {}, "danger": False},
    {"name": "set_qq_avatar", "desc": "设置QQ头像", "params": {"file": ""}, "danger": True},
    {"name": "set_self_longnick", "desc": "设置个性签名", "params": {"longNick": ""}, "danger": True},

    # ==================== NapCat 扩展 - 文件 ====================
    {"name": "get_file", "desc": "获取文件信息（路径、URL、大小等）", "params": {"file_id": ""}, "danger": False},

    # ==================== NapCat 扩展 - 消息 ====================
    {"name": "forward_friend_single_msg", "desc": "转发单条消息到私聊", "params": {"message_id": 0, "user_id": 0}, "danger": True},
    {"name": "forward_group_single_msg", "desc": "转发单条消息到群聊", "params": {"message_id": 0, "group_id": 0}, "danger": True},
    {"name": "send_forward_msg", "desc": "发送合并转发消息", "params": {"message_type": "group", "user_id": 0, "group_id": 0, "messages": []}, "danger": True},
    {"name": "mark_private_msg_as_read", "desc": "标记私聊消息已读", "params": {"user_id": 0}, "danger": True},
    {"name": "mark_group_msg_as_read", "desc": "标记群聊消息已读", "params": {"group_id": 0}, "danger": True},
    {"name": "get_friend_msg_history", "desc": "获取私聊消息历史记录", "params": {"user_id": "", "message_seq": "0", "count": 20, "reverseOrder": False}, "danger": False},

    # ==================== NapCat 扩展 - 工具 ====================
    {"name": "translate_en2zh", "desc": "英文翻译成中文", "params": {"words": ["hello"]}, "danger": False},
    {"name": "set_msg_emoji_like", "desc": "给消息设置表情回应/点赞", "params": {"message_id": 0, "emoji_id": ""}, "danger": True},

    # ==================== NapCat 扩展 - 收藏 ====================
    {"name": "create_collection", "desc": "创建文本收藏", "params": {"rawData": "", "brief": ""}, "danger": True},
    {"name": "get_collection_list", "desc": "获取收藏列表", "params": {"count": 10}, "danger": False},

    # ==================== NapCat 扩展 - 联系人 ====================
    {"name": "get_recent_contact", "desc": "获取最近聊天联系人列表", "params": {"count": 10}, "danger": False},
    {"name": "_mark_all_as_read", "desc": "标记所有消息为已读", "params": {}, "danger": True},
    {"name": "get_profile_like", "desc": "获取被点赞列表", "params": {}, "danger": False},

    # ==================== NapCat 扩展 - 表情 ====================
    {"name": "fetch_custom_face", "desc": "获取收藏表情列表", "params": {"count": 10}, "danger": False},
    {"name": "fetch_emoji_like", "desc": "获取表情回应列表", "params": {"message_id": 0, "emoji_id": ""}, "danger": False},

    # ==================== NapCat 扩展 - 状态 ====================
    {"name": "set_input_status", "desc": "设置输入状态（正在输入等）", "params": {"user_id": 0, "group_id": 0, "eventType": 1}, "danger": True},

    # ==================== NapCat 扩展 - 群增强 ====================
    {"name": "get_group_info_ex", "desc": "获取群额外详细信息", "params": {"group_id": 0}, "danger": False},
    {"name": "get_group_ignore_add_request", "desc": "获取群忽略的加群请求", "params": {"group_id": 0}, "danger": False},
    {"name": "_del_group_notice", "desc": "删除群公告", "params": {"group_id": 0, "notice_id": ""}, "danger": True},
    {"name": "get_group_shut_list", "desc": "获取群被禁言成员列表", "params": {"group_id": 0}, "danger": False},

    # ==================== NapCat 扩展 - 网络 & 系统 ====================
    {"name": "nc_get_packet_status", "desc": "获取 PacketServer 连接状态", "params": {}, "danger": False},
    {"name": "nc_get_user_status", "desc": "获取用户在线状态", "params": {"user_id": 0}, "danger": False},
    {"name": "nc_get_rkey", "desc": "获取 Rkey 密钥", "params": {}, "danger": False},

    # ==================== NapCat 扩展 - 小程序 ====================
    {"name": "get_mini_app_ark", "desc": "签名小程序/ARK卡片（如B站分享卡片）", "params": {"app_json": ""}, "danger": False},

    # ==================== NapCat 扩展 - AI 语音 ====================
    {"name": "get_ai_record", "desc": "AI 文字转语音", "params": {"character": "", "text": ""}, "danger": False},
    {"name": "get_ai_characters", "desc": "获取可用的 AI 语音角色列表", "params": {}, "danger": False},
    {"name": "send_group_ai_record", "desc": "群聊发送 AI 语音消息", "params": {"group_id": 0, "character": "", "text": ""}, "danger": True},
]


class Main(star.Star):
    def __init__(self, context: star.Context, config: AstrBotConfig = None):
        super().__init__(context, config)
        self.cfg = config or AstrBotConfig("")
        self._registered = False

    async def _register_tools(self):
        if self._registered:
            return
        self._registered = True

        from astrbot.core.star.star_handler import EventType
        from astrbot.core.star.register.star_handler import get_handler_or_create

        for api in NAPCAT_APIS:
            name = api["name"]
            full_name = f"{self.cfg.get('tool_naming_prefix', 'napcat')}__{name}"
            desc = api["desc"]
            params = api["params"]
            danger = api.get("danger", False)

            async def make_handler(
                event: AstrMessageEvent,
                _n=name,
                _p=params,
                _d=danger,
                **kwargs,
            ) -> str:
                actual = dict(_p)
                for k, v in kwargs.items():
                    if k in actual:
                        if isinstance(actual[k], bool) and isinstance(v, str):
                            actual[k] = v.lower() in ("true", "1", "yes")
                        elif isinstance(actual[k], int) and isinstance(v, str):
                            try:
                                actual[k] = int(v)
                            except ValueError:
                                actual[k] = v
                        else:
                            actual[k] = v
                return await self._call_api(event, _n, actual, _d)

            make_handler.__name__ = f"_handler_{name}"
            make_handler.__qualname__ = f"Main._handler_{name}"
            make_handler.__module__ = self.__class__.__module__

            param_specs = []
            for k, v in params.items():
                param_specs.append(f"            {k}(string): {desc}")

            param_doc = "\n" + "\n".join(param_specs) + "\n        " if param_specs else ""
            make_handler.__doc__ = f"""{desc}。{'(高危操作)' if danger else ''}
        Args:{param_doc}"""

            args_schema = []
            for k in params.keys():
                args_schema.append({"type": "string", "name": k, "description": desc})

            md = get_handler_or_create(make_handler, EventType.OnCallingFuncToolEvent)
            llm_tools.add_func(full_name, args_schema, make_handler.__doc__.strip(), md.handler)
            logger.debug(f"[napcat] Registered tool: {full_name}")

        logger.info(f"[napcat] Registered {len(NAPCAT_APIS)} LLM tools.")

    async def initialize(self):
        await self._register_tools()

    def _get_bot(self, event: AstrMessageEvent):
        return getattr(event, "bot", None)

    def _truncate(self, text: str) -> str:
        limit = int(self.cfg.get("result_max_chars", 800) or 0)
        if limit > 0 and len(text) > limit:
            return text[:limit] + f"\n...[截断, 共{len(text)}字符]"
        return text

    def _check_danger(self, event: AstrMessageEvent, api_name: str) -> str | None:
        if api_name not in DANGEROUS_APIS:
            return None
        if not self.cfg.get("enable_dangerous_ops", False):
            return "高危操作被禁用。请在插件配置中启用 enable_dangerous_ops。"
        allowed_groups = (self.cfg.get("allowed_groups", "") or "").strip()
        if allowed_groups:
            gid = str(event.get_group_id())
            allowed = [g.strip() for g in allowed_groups.split(",")]
            if gid and gid not in allowed:
                return f"群 {gid} 不在高危操作白名单中。"
        allowed_admins = (self.cfg.get("allowed_admins", "") or "").strip()
        if allowed_admins:
            sid = str(event.get_sender_id())
            allowed = [a.strip() for a in allowed_admins.split(",")]
            if sid not in allowed:
                return f"用户 {sid} 不在高危操作白名单中。"
        return None

    async def _call_api(
        self, event: AstrMessageEvent, action: str, params_def: dict, danger: bool
    ) -> str:
        bot = self._get_bot(event)
        if not bot:
            return "错误: 未连接 NapCat/aiocqhttp 平台。"
        if danger:
            err = self._check_danger(event, action)
            if err:
                return err

        actual = {}
        for k, v in params_def.items():
            if isinstance(v, bool):
                actual[k] = v
            elif isinstance(v, int):
                actual[k] = v
            elif isinstance(v, list):
                actual[k] = v
            else:
                actual[k] = v

        try:
            result = await bot.call_action(action=action, **actual)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"调用 {action} 失败: {e}"

    # ==================== 管理员命令 ====================

    @filter.command_group("napcat")
    def napcat(self):
        pass

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("napcat_list", alias=["nc_list"])
    async def nc_list(self, event: AstrMessageEvent):
        lines = [f"NapCat API 列表（共 {len(NAPCAT_APIS)} 个 LLM Tool）:"]
        danger_count = 0
        for a in NAPCAT_APIS:
            tag = "🔴" if a.get("danger") else "🟢"
            if a.get("danger"):
                danger_count += 1
            lines.append(f"  {tag} {a['name']}: {a['desc']}")
        lines.append(f"\n高危: {danger_count}, 安全: {len(NAPCAT_APIS) - danger_count}")
        for chunk in [lines[i:i+25] for i in range(0, len(lines), 25)]:
            yield event.plain_result("\n".join(chunk))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("napcat_search", alias=["nc_search"])
    async def nc_search(self, event: AstrMessageEvent, keyword: str):
        matched = [a for a in NAPCAT_APIS if keyword.lower() in a["name"].lower() or keyword.lower() in a["desc"].lower()]
        if not matched:
            yield event.plain_result(f"未找到含 '{keyword}' 的API")
            return
        lines = [f"搜索结果 ({len(matched)}):"]
        for a in matched:
            tag = "🔴" if a.get("danger") else "🟢"
            lines.append(f"  {tag} {a['name']}: {a['desc']}")
        yield event.plain_result("\n".join(lines))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("napcat_config", alias=["nc_config"])
    async def nc_config(self, event: AstrMessageEvent):
        yield event.plain_result(json.dumps({
            "enable_dangerous_ops": self.cfg.get("enable_dangerous_ops", False),
            "allowed_groups": self.cfg.get("allowed_groups", ""),
            "allowed_admins": self.cfg.get("allowed_admins", ""),
            "result_max_chars": self.cfg.get("result_max_chars", 800),
            "tool_naming_prefix": self.cfg.get("tool_naming_prefix", "napcat"),
            "total_tools": len(NAPCAT_APIS),
            "dangerous_tools": len([a for a in NAPCAT_APIS if a.get("danger")]),
        }, ensure_ascii=False, indent=2))
