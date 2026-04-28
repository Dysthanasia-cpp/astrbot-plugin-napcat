# astrbot_plugin_napcat 全接口暴露插件

> 版本: 2.0.0 | 收录 96 个 LLM Tool | OneBot V11 + go-cqhttp + NapCat 扩展

## 功能

- ✅ **全接口暴露**：收录 OneBot11 全部 action + go-cqhttp 扩展 + NapCat 扩展，共 96 个 API
- ✅ **AI 直接调用**：每个 API 注册为独立的 LLM function-calling Tool，Bot 可通过自然语言直接调用
- ✅ **高危操作可控**：禁言、踢人、改群名、发公告、戳一戳等操作默认关闭，需手动开启
- ✅ **白名单机制**：可配置允许执行高危操作的群号和用户QQ
- ✅ **结果截断**：自动截断过长返回值，避免 token 浪费
- ✅ **管理员命令**：`/napcat_list`, `/napcat_search`, `/napcat_config` 手动管理

## 配置

在 WebUI 插件管理面板中配置以下选项：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| enable_dangerous_ops | bool | false | 是否允许 LLM 调用高危操作 |
| allowed_groups | string | "" | 高危操作白名单群号（逗号分隔，空=全部） |
| allowed_admins | string | "" | 高危操作白名单用户QQ（逗号分隔，空=全部） |
| result_max_chars | int | 800 | API 返回结果最大字符数（0=不限制） |
| tool_naming_prefix | string | "napcat" | LLM Tool 名称前缀 |

## 高危操作列表

以下操作默认被拦截，需在配置中启用：

- 🔴 `set_group_ban` — 禁言群成员
- 🔴 `set_group_kick` — 踢出群成员  
- 🔴 `set_group_whole_ban` — 全员禁言
- 🔴 `set_group_admin` — 设置管理员
- 🔴 `set_group_name` — 修改群名
- 🔴 `set_group_leave` — 退出/解散群
- 🔴 `set_group_card` — 修改群名片
- 🔴 `_send_group_notice` — 发送群公告
- 🔴 `send_private_msg` / `send_group_msg` — 发送消息
- 🔴 `group_poke` / `friend_poke` — 戳一戳
- 🔴 `delete_msg` — 撤回消息
- 🔴 `send_like` — 好友点赞
- 🔴 `delete_friend` — 删除好友
- 🔴 `set_qq_profile` — 修改QQ资料
- 🔴 `set_qq_avatar` — 修改QQ头像
- 🔴 `set_online_status` — 修改在线状态
- … 更多见 `main.py` 中的 `DANGEROUS_APIS`

## 使用示例

Bot 连接 NapCat 后，直接通过自然语言对话即可触发：

| 用户输入 | Bot 自动调用的 Tool |
|----------|---------------------|
| "把张三禁言10分钟" | `napcat__set_group_ban` |
| "修改群名片为管理员" | `napcat__set_group_card` |
| "看看这个群有哪些人" | `napcat__get_group_member_list` |
| "发一个群公告" | `napcat___send_group_notice` |
| "帮我戳一下李四" | `napcat__group_poke` |
| "给王五点个赞" | `napcat__send_like` |
| "看看我的好友列表" | `napcat__get_friend_list` |
| "这个群的基本信息" | `napcat__get_group_info` |
| "识别这张图片里的文字" | `napcat__ocr_image` |
| "AI语音说句话" | `napcat__get_ai_record` |

## 完整 API 清单

### OneBot V11 标准（26 个）
消息: send_private_msg, send_group_msg, send_msg, delete_msg, get_msg, get_forward_msg, send_like, get_record, get_image
群管: set_group_kick, set_group_ban, set_group_whole_ban, set_group_admin, set_group_card, set_group_name, set_group_leave, set_group_special_title, set_group_add_request, get_group_info, get_group_list, get_group_member_info, get_group_member_list, get_group_honor_info
好友/账号: get_stranger_info, get_friend_list, get_login_info, set_friend_add_request, can_send_image, can_send_record, get_status, get_version_info, get_cookies, get_csrf_token, get_credentials, clean_cache

### go-cqhttp 扩展（23 个）
账号: set_qq_profile, _get_model_show, _set_model_show, get_online_clients, delete_friend
消息: mark_msg_as_read, send_group_forward_msg, send_private_forward_msg, get_group_msg_history
群管: get_group_system_msg, get_essence_msg_list, get_group_at_all_remain, set_group_portrait, set_essence_msg, delete_essence_msg, send_group_sign, _send_group_notice, _get_group_notice
文件: upload_group_file, delete_group_file, create_group_file_folder, delete_group_folder, get_group_file_system_info, get_group_root_files, get_group_files_by_folder, get_group_file_url, upload_private_file, download_file
工具: ocr_image, check_url_safely

### NapCat 扩展（36 个）
互动: set_group_sign, group_poke, friend_poke, send_poke
推荐: ArkSharePeer, ArkShareGroup
账号: get_robot_uin_range, set_online_status, get_friends_with_category, set_qq_avatar, set_self_longnick
消息: forward_friend_single_msg, forward_group_single_msg, send_forward_msg, mark_private_msg_as_read, mark_group_msg_as_read, get_friend_msg_history
工具: translate_en2zh, set_msg_emoji_like
收藏: create_collection, get_collection_list
联系人: get_recent_contact, _mark_all_as_read, get_profile_like
表情: fetch_custom_face, fetch_emoji_like
状态: set_input_status
群增强: get_group_info_ex, get_group_ignore_add_request, _del_group_notice, get_group_shut_list
系统: nc_get_packet_status, nc_get_user_status, nc_get_rkey
小程序: get_mini_app_ark
AI语音: get_ai_record, get_ai_characters, send_group_ai_record

## 安全注意事项

⚠️ **高危操作默认关闭**。如需启用，请在 WebUI 插件配置中开启 `enable_dangerous_ops`，并建议配置 `allowed_groups` 白名单，防止 Bot 在不相关的群中执行危险操作。

## 技术细节

- 每个 API 通过 `astrbot.core.provider.register.llm_tools.add_func()` 动态注册
- 通过 `event.bot.call_action()` 调用 OneBot 协议
- 插件自动检测是否连接 aiocqhttp/NapCat 平台
- 配置使用 AstrBot 标准 `_conf_schema.json` 机制
- 所有代码均由ai编写
