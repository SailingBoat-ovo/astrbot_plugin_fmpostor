# astrbot_plugin_fmpostor

[中文](#中文) · [English](#english)

**Fmpostor 服务端桥接插件** —— 让 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 机器人在 QQ 群里查询 [Fmpostor](https://github.com/SailingBoat-ovo/Fmpostor)（Among Us 私服服务端）的房间状态、订阅游戏结束提醒。AstrBot 可以直接接入 **QQ 官方机器人**。

License: GPL-3.0

---

## 中文

### 能做什么

| 群命令 | 作用 |
|---|---|
| `#在线状态`（或面板里配置的其它状态命令） | 查看服务器当前的房间列表 |
| `#订阅 房间号` | 该房间游戏结束时在本群提醒 |
| `#退订 房间号` | 取消订阅 |
| `#帮助` | 命令帮助 |

另外，服务端会通过 AstrBot 主动往群里发消息：房主在游戏里发 `/m` 推送房间报告、面板里的定时公告、订阅提醒。

### 准备

| 项目 | 要求 |
|---|---|
| AstrBot | v4.18 或更新（需要 OpenAPI） |
| Fmpostor | Max-800.0 或更新（Turbo-700 之后的版本才有 AstrBot 桥接） |
| 机器人 | AstrBot 已接入 QQ（QQ 官方机器人或其它适配器均可），并且已加入目标群 |

### 安装教程

整个过程分两半：**AstrBot 这边装插件**（让群命令能传到服务端），**Fmpostor 面板那边填 AstrBot 信息**（让服务端能主动发消息）。

#### 第 1 步：安装插件

任选一种：

- **从仓库安装**：AstrBot 管理面板 → 插件 → 安装插件 → 填入
  `https://github.com/SailingBoat-ovo/astrbot_plugin_fmpostor`
- **手动安装**：下载本仓库，把整个文件夹放到 AstrBot 的
  `data/plugins/astrbot_plugin_fmpostor/`，然后在插件页点「重载插件」或重启 AstrBot。

装好后插件列表里会出现「Fmpostor 服务端桥接」。

#### 第 2 步：拿到桥接口令

1. 打开 Fmpostor 的 Web 面板并登录。
2. 进入「服务器选项」，找到 **📡 QQ 群房间广播（AstrBot）** 卡片。
3. 「桥接口令」一栏点 **复制**。（口令泄露了可以点「重新生成」，然后把新口令再填一次到插件里。）

#### 第 3 步：配置插件

AstrBot 管理面板 → 插件 → Fmpostor 服务端桥接 → 配置：

| 配置项 | 填什么 | 例子 |
|---|---|---|
| `server_url` | Fmpostor 地址 + 面板路径（默认 `/webadmin`） | AstrBot 和服务端在同一台机器：`http://127.0.0.1:22023/webadmin`<br>不在同一台：`https://你的域名/webadmin` |
| `bridge_token` | 第 2 步复制的桥接口令 | |

保存。到群里发 `#在线状态`，机器人回复房间列表就说明 **接收方向** 通了。

#### 第 4 步：让服务端能主动发消息（可选，但推荐）

`/m` 推送、定时公告、订阅提醒是服务端主动发出的，需要 AstrBot 的 OpenAPI：

1. AstrBot 管理面板 → 设置 → **OpenAPI** → 创建 API Key，勾选 **`im`** 权限，复制 Key（形如 `abk_…`）。
2. 在要推送的群里发 `/sid`，机器人会回复这个群的会话 ID（UMO），形如 `qq_official:GroupMessage:xxxx`。
3. 回到 Fmpostor 面板的 **QQ 群房间广播（AstrBot）** 卡片，填写：
   - **启用**：开启
   - **AstrBot 地址**：如 `http://127.0.0.1:6185`
   - **AstrBot API Key**：上一步的 Key
   - **推送会话**：第 2 步得到的 UMO，一行一个
4. 点 **保存**，再点 **发送测试消息**。群里收到测试消息就全部完成了。

> QQ 官方机器人在群里**主动**发言，需要群主在群设置里打开「机器人主动在群聊内发言」。群命令的回复属于被动回复，不受这个限制。

### 自定义

在 Fmpostor 面板同一张卡片里还可以：

- 修改 **状态命令**（多个用逗号分隔，默认 `#在线状态`）。插件每 60 秒从服务端拉取一次命令列表，改完不用动插件。
- 修改两条 **QQ 消息模板**（`/m` 房间报告、`#在线状态` 回复），占位符：`{server}` 服务器名、`{count}` 房间数、`{rooms}` 房间列表、`{time}` 时间。
- 修改 **服务器名称**（显示在消息里）。

### 常见问题

| 现象 | 原因 / 解决 |
|---|---|
| 发 `#在线状态` 没反应，AstrBot 日志里有 `桥接口令不正确` | 插件里的 `bridge_token` 和面板上的不一致（或面板里点过「重新生成」），重新复制填入 |
| 日志里有 `拉取命令列表失败` / `转发命令失败` | `server_url` 写错或网络不通。在 AstrBot 所在机器上用浏览器打开 `server_url`，确认能访问；记得带上 `/webadmin` |
| 群命令有回复，但 `/m` 推送、订阅提醒收不到 | 第 4 步没配，或 API Key 没勾 `im` 权限，或推送会话填错；QQ 官方机器人还要检查群里是否开启了「机器人主动在群聊内发言」 |
| 订阅提醒发到了哪里 | 发回你订阅时所在的群（QQ 官方机器人不能私聊只在群里出现过的成员） |

### 隐私

插件只转发上面列出的命令（列表由服务端下发），其它聊天内容一律不发送给服务端。转发时附带会话 ID、发送者 ID 和昵称，用于订阅提醒和日志。

---

## English

### What it does

| Group command | What it does |
|---|---|
| `#在线状态` (or any other status command configured in the panel) | Show the server's current room list |
| `#订阅 <room code>` | Get a reminder in this group when that room's game ends |
| `#退订 <room code>` | Cancel the subscription |
| `#帮助` | Command help |

The server also sends messages to groups on its own through AstrBot: room reports when a host types `/m` in game, scheduled announcements from the panel, and subscription reminders.

### Requirements

| Item | Requirement |
|---|---|
| AstrBot | v4.18 or newer (OpenAPI) |
| Fmpostor | Max-800.0 or newer (the AstrBot bridge arrived after Turbo-700) |
| Bot | AstrBot connected to QQ (official QQ bot or any other adapter) and already in the target group |

### Setup

There are two halves: **install the plugin in AstrBot** (so group commands reach the server) and **enter the AstrBot details in the Fmpostor panel** (so the server can post on its own).

#### Step 1: install the plugin

Either:

- **From the repository**: AstrBot dashboard → Plugins → Install → enter
  `https://github.com/SailingBoat-ovo/astrbot_plugin_fmpostor`
- **Manually**: download this repository and put the folder at AstrBot's
  `data/plugins/astrbot_plugin_fmpostor/`, then click "Reload plugins" or restart AstrBot.

The plugin list will then show "Fmpostor 服务端桥接".

#### Step 2: get the bridge token

1. Open the Fmpostor web panel and log in.
2. Go to "Server options" and find the **📡 QQ 群房间广播（AstrBot）** card.
3. Click **Copy** next to the bridge token. (If it leaks, click "Regenerate" and enter the new token in the plugin again.)

#### Step 3: configure the plugin

AstrBot dashboard → Plugins → Fmpostor 服务端桥接 → Settings:

| Setting | Value | Example |
|---|---|---|
| `server_url` | Fmpostor address + panel path (default `/webadmin`) | Same machine as AstrBot: `http://127.0.0.1:22023/webadmin`<br>Different machine: `https://your-domain/webadmin` |
| `bridge_token` | The token from step 2 | |

Save. Send `#在线状态` in the group; if the bot answers with the room list, the **receiving** side works.

#### Step 4: let the server post on its own (optional, recommended)

`/m` pushes, scheduled announcements and subscription reminders are sent by the server and need AstrBot's OpenAPI:

1. AstrBot dashboard → Settings → **OpenAPI** → create an API key with the **`im`** scope and copy it (it looks like `abk_…`).
2. Send `/sid` in the group you want to push to; the bot replies with that group's session ID (UMO), e.g. `qq_official:GroupMessage:xxxx`.
3. Back in the Fmpostor panel's **QQ 群房间广播（AstrBot）** card, fill in:
   - **Enabled**: on
   - **AstrBot address**: e.g. `http://127.0.0.1:6185`
   - **AstrBot API key**: the key from step 1
   - **Target sessions**: the UMOs from step 2, one per line
4. Click **Save**, then **Send test message**. Once the test message shows up in the group, you are done.

> For the official QQ bot to post **on its own** in a group, the group owner must enable "allow the bot to speak proactively in group chat". Replies to group commands are passive and not affected.

### Customising

On the same panel card you can also:

- Change the **status commands** (comma-separated, default `#在线状态`). The plugin fetches the command list from the server every 60 seconds, so nothing needs to change on the plugin side.
- Edit the two **QQ message templates** (`/m` room report, `#在线状态` reply). Placeholders: `{server}` server name, `{count}` room count, `{rooms}` room list, `{time}` time.
- Change the **server name** shown in messages.

### Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `#在线状态` gets no reply and the AstrBot log says `桥接口令不正确` | The plugin's `bridge_token` doesn't match the panel (or it was regenerated). Copy it again |
| The log says `拉取命令列表失败` / `转发命令失败` | `server_url` is wrong or unreachable. Open `server_url` in a browser on the AstrBot machine to check, and remember the `/webadmin` part |
| Group commands work but `/m` pushes and reminders never arrive | Step 4 is missing, the API key lacks the `im` scope, or the target session is wrong. For the official QQ bot, also check the group's "speak proactively" setting |
| Where do subscription reminders go? | Back to the group you subscribed from (the official QQ bot cannot DM members it only knows from a group) |

### Privacy

The plugin forwards only the commands listed above (the list comes from the server); no other chat content is sent. Each forwarded command carries the session ID, sender ID and nickname, used for subscription reminders and logs.
