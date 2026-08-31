<div align="center">

# 🔭 asoscope — 零依赖 App Store 情报 CLI

**在终端里搜索、剖析、对比、盯榜全球 App Store，只用 Apple 公开接口，免登录、免密钥、不下载 IPA。**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](#-设计思路与迭代规划)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#-环境要求)
[![Tests](https://img.shields.io/badge/tests-53%20passed-success.svg)](#-运行测试)

**🌐 语言 / Languages：简体中文 · [繁體中文](docs/README.zh-TW.md) · [English](docs/README.en.md)**

</div>

---

## 🎉 项目介绍

**asoscope** 是一款本地优先（local-first）的 App Store 情报命令行工具，面向独立开发者、ASO（应用商店优化）从业者、产品经理、竞品分析师与自动化脚本场景。它把 Apple 官方的 **iTunes Search API** 与 **公开 RSS 榜单/评论源** 封装成一套统一、可组合、可导出的终端指令：搜索全球 175 个地区的应用、读取完整元数据、抓取用户评论与评分分布、浏览各类目榜单、横向对比多款竞品、把关注的应用加入本地观察清单并自动快照版本/价格/评分变化。

### 😮‍💨 它解决什么痛点

- 🧭 **查数据要开一堆网页**：App Store 网页端不利于批量查询，也无法直接喂给脚本；asoscope 一条命令返回结构化结果，支持表格 / JSON / CSV / Markdown 四种格式与文件输出。
- 🔐 **同类工具门槛与风险高**：部分工具依赖 Apple ID 登录、调用私有接口甚至下载 IPA 二进制，存在封号与合规风险。asoscope **只访问 Apple 公开、免密钥、只读接口，不认证、不碰私有接口、不下载 IPA**。
- 🧱 **运行环境沉重**：很多 CLI 拖着一长串第三方依赖，安装即“依赖地狱”。asoscope 仅使用 **Python 3.8+ 标准库，运行时零第三方依赖**，Windows / macOS / Linux 全平台一致运行。
- 📊 **竞品盯盘靠手动**：内置本地观察清单与快照 diff，版本更新、调价、评分波动一目了然，数据只存本机，绝无遥测。

### 💡 灵感来源与差异化

本项目的产品灵感来自 GitHub Trending 在榜项目 [majd/ipatool](https://github.com/majd/ipatool)（Go，搜索/下载 App Store 安装包的命令行工具）——它验证了“在终端里操作 App Store”这一真实需求。但 asoscope **没有复制其任何代码**，并选择了一条更安全、更通用的差异化路线：

| 维度 | 传统 IPA 工具 | **asoscope（本项目）** |
| --- | --- | --- |
| 接口性质 | 需 Apple ID 认证、涉及私有接口 | ✅ 仅公开免密钥只读接口 |
| 合规风险 | 账号与分发风险 | ✅ 不登录、不下载 IPA |
| 核心能力 | 下载安装包 | ✅ 元数据情报：搜索/详情/评论/榜单/对比/盯盘 |
| 运行依赖 | 平台二进制 | ✅ Python 标准库，零三方依赖，跨平台 |
| 输出形态 | 文件下载 | ✅ 表格/JSON/CSV/Markdown，天然适配自动化 |

> ⚖️ asoscope 仅使用 Apple 公开数据端点，仅供合法的市场研究与开发分析用途，请遵守目标地区法律法规与 Apple 服务条款。

---

## ✨ 核心特性

- 🌍 **全球多区搜索** —— 支持任意 ISO 3166-1 双字母地区（`us` / `jp` / `gb` / `cn` …），iPhone / iPad 实体可选，支持类目过滤、免费/付费过滤、最低评分过滤，以及相关度 / 评分 / 评分数 / 名称四种排序。
- 🪪 **双模式精准查询** —— `lookup` 同时支持数字 Track ID 与 Bundle ID（如 `com.duolingo.DuolingoMobile`），返回 40+ 字段的完整元数据。
- 💬 **公开评论抓取** —— 按“最新 / 最有帮助”排序分页拉取用户评论；`--stats` 一键输出 1–5 星分布与页面均分，快速感知口碑。
- 🏆 **公开榜单浏览** —— 免费榜 / 付费榜 / 畅销榜 / 新上架榜四类榜单，支持地区、类目与数量参数。
- ⚖️ **竞品横向对比** —— `compare` 接受 Track ID 与 Bundle ID 混合输入，一张表输出价格、版本、评分、类目等对比结果。
- 👀 **本地观察清单 + 快照 Diff** —— `watch` 子命令把应用加入本地清单，反复快照后自动比对版本号、价格、均分、评分数、包体大小、发版日期的变化；**数据只保存在本机**。
- 🧮 **四种导出格式** —— 对齐终端表格（**中日韩全角字符宽度感知，不会错位**）、JSON、CSV、Markdown，`-o` 任意落盘，可直接接入 Excel / BI / CI。
- 🧰 **零三方运行时依赖** —— 仅用 Python 标准库；自带 TTL 磁盘缓存、指数退避重试、确定性退出码，工程级健壮性。
- 🧪 **离线可跑的完整测试** —— 53 个单元测试基于真实抓取并脱敏的接口夹具，运行测试全程不需要联网。

---

## 🚀 快速开始

### 📌 环境要求

| 项目 | 要求 |
| --- | --- |
| Python | **3.8 及以上**（3.8 / 3.9 / 3.10 / 3.11 / 3.12 均验证） |
| 操作系统 | Windows 10+、macOS 11+、任意主流 Linux 发行版 |
| 网络 | 仅需访问 `itunes.apple.com`（Apple 公开端点） |
| 账号 / 密钥 | ❌ 不需要 Apple ID，不需要任何 API Key |
| 第三方依赖 | ❌ 零依赖 |

查看 Python 版本：

```bash
python3 --version   # Windows 上通常是 python --version
```

### 📦 安装

**方式一：pip 安装（推荐）**

```bash
pip install asoscope-cli
```

**方式二：pipx 隔离安装（命令行工具最佳实践）**

```bash
pipx install asoscope-cli
```

**方式三：从源码免安装运行**

```bash
git clone https://github.com/gitstq/asoscope.git
cd asoscope
python3 -m asoscope --version
```

安装成功后验证：

```bash
asoscope --version     # 输出 asoscope 1.0.0
asoscope --help        # 查看全部命令
```

### ⚡ 一分钟上手（可直接复制）

```bash
# 1. 搜索美区免费的习惯打卡 App，按评分排序，只看前 5 个
asoscope search "habit tracker" --price free --sort rating -n 5

# 2. 用 Bundle ID 查询完整元数据，输出 JSON
asoscope lookup --bundle com.duolingo.DuolingoMobile -f json

# 3. 看日区游戏类免费榜前 10，输出 Markdown
asoscope -c jp charts top-free --genre games -n 10 -f md

# 4. 抓某款应用最新一页评论的评分分布
asoscope reviews 570060128 --stats

# 5. 把竞品加入观察清单并快照
asoscope watch add 570060128
asoscope watch snapshot
asoscope watch diff
```

---

## 📖 详细使用指南

### 🧭 命令总览

```text
asoscope [全局参数] <命令> [命令参数]

命令：
  search    搜索应用
  lookup    查询单个应用的完整元数据
  reviews   抓取公开用户评论 / 评分分布
  charts    浏览公开榜单（免费/付费/畅销/新上架）
  compare   横向对比两款及以上应用
  watch     本地观察清单：add / rm / ls / snapshot / diff
  genres    列出支持的类目别名与数字 ID
```

### 🎛️ 全局参数（写在子命令前后都可以）

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-c, --country` | App Store 地区，双字母国家/地区码 | `us` |
| `-f, --format` | 输出格式：`table` / `json` / `csv` / `md` | `table` |
| `-o, --output` | 把结果写入文件而非标准输出 | — |
| `--timeout` | 单次请求超时秒数 | `15` |
| `--no-cache` | 跳过本地 TTL 缓存 | 关闭 |
| `--data-dir` | 自定义 `watchlist.json` 所在目录 | 系统默认目录 |

> 💡 全局参数两种位置等价：`asoscope -f json search notion` 与 `asoscope search notion -f json` 结果完全一致。

### 1) 🔍 search —— 搜索应用

```bash
asoscope search <关键词> [选项]
```

| 参数 | 说明 |
| --- | --- |
| `-n, --limit` | 返回数量，1–200，默认 20 |
| `--device` | `iphone`（默认）或 `ipad` |
| `--genre` | 类目别名（如 `games`、`productivity`）或 Apple 数字类目 ID |
| `--price` | `free` / `paid` / `all` |
| `--min-rating` | 仅保留均分不低于该值的应用 |
| `--sort` | `relevance`（默认）/ `rating` / `ratings` / `name` |

示例：

```bash
# 美区效率类、均分 4.5 以上的免费笔记应用，按评分数排序，导出 CSV
asoscope search "notes" --genre productivity --price free \
  --min-rating 4.5 --sort ratings -f csv -o notes.csv
```

### 2) 🪪 lookup —— 完整元数据

```bash
asoscope lookup --id 570060128            # 按 Track ID
asoscope lookup --bundle com.duolingo.DuolingoMobile   # 按 Bundle ID
```

表格模式下逐字段展示：开发者、卖方、版本、价格与币种、整体/当前版本评分、类目、内容分级、包体大小（MB）、最低系统版本、支持语言、上架/发版时间、更新日志、商店链接、图标与简介。JSON 模式输出全部原始归一化字段，便于程序消费。

### 3) 💬 reviews —— 用户评论与口碑

```bash
asoscope reviews <track_id> [--page 1] [--sort recent|helpful] [--stats]
```

```bash
# 抓第 2 页“最有帮助”的评论，输出 JSON
asoscope reviews 570060128 --page 2 --sort helpful -f json

# 只看评分分布（条数、页面均分、1–5 星计数）
asoscope reviews 570060128 --stats
```

### 4) 🏆 charts —— 榜单

```bash
asoscope charts <top-free|top-paid|top-grossing|new> [--genre 类目] [-n 数量]
```

```bash
# 港区财务类付费榜前 20
asoscope -c hk charts top-paid --genre finance -n 20
```

### 5) ⚖️ compare —— 竞品对比

输入可以混合 Track ID 与 Bundle ID，至少两个：

```bash
asoscope compare 570060128 com.mojang.minecraftpe -f md
```

### 6) 👀 watch —— 本地观察清单与变更监控

观察清单是一个人类可读的 JSON 文件（`watchlist.json`），只保存在本机，绝不上传。

```bash
asoscope watch add <track_id 或 bundle_id>   # ➕ 加入观察（自动先查询一次作为基线快照）
asoscope watch ls                            # 📋 列出全部观察对象
asoscope watch snapshot                      # 📸 对所有观察对象抓取一次新快照
asoscope watch snapshot --id 570060128       # 📸 只快照某一个
asoscope watch diff                          # 🔍 对比最近两次快照的字段变化
asoscope watch rm <track_id>                 # 🗑️ 移除观察
```

典型用法是配合系统计划任务（Linux/macOS 的 cron、Windows 的任务计划程序）每天执行一次 `snapshot` + `diff`，实现竞品版本/价格/评分的自动盯盘。`diff` 监测字段：**版本号、价格、显示价格、平均评分、评分数、包体大小、当前版本发布日期**。

### 🗂️ 数据与缓存目录（跨平台）

| 平台 | 观察清单目录 | 缓存目录 |
| --- | --- | --- |
| Windows | `%LOCALAPPDATA%\asoscope` | `%LOCALAPPDATA%\asoscope\cache` |
| macOS | `~/Library/Application Support/asoscope` | `~/Library/Caches/asoscope` |
| Linux | `$XDG_DATA_HOME/asoscope` 或 `~/.local/share/asoscope` | `$XDG_CACHE_HOME/asoscope` 或 `~/.cache/asoscope` |

也可以用环境变量 `ASOSCOPE_DATA_DIR`、`ASOSCOPE_CACHE_DIR` 或 `--data-dir` 参数覆盖。

### 🧑‍💻 作为 Python 库集成

asoscope 同时是一个干净的库，可直接嵌入你自己的程序：

```python
from asoscope.api import AppStoreClient
from asoscope.http import HttpClient, DiskCache

client = AppStoreClient(HttpClient(cache=DiskCache("./.cache")))
apps = client.search("habit tracker", country="us", price="free", sort="rating")
for app in apps[:5]:
    print(app.track_id, app.track_name, app.average_rating, app.formatted_price)

app = client.lookup(bundle_id="com.duolingo.DuolingoMobile")
reviews = client.reviews(app.track_id, country="us", sort="helpful")
```

### 🚦 退出码约定（便于脚本判断）

| 退出码 | 含义 |
| --- | --- |
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | 参数使用错误（如非法地区码） |
| 3 | 网络 / 接口错误（含重试耗尽） |
| 4 | 未找到目标应用 |
| 5 | 本地观察清单读写错误 |

### 🖼️ 运行截图 / 演示动图

> 📸 截图与终端录屏占位：建议放置 `docs/demo/` 目录，例如：
>
> - `docs/demo/search-demo.svg` —— 搜索与多格式导出
> - `docs/demo/watch-diff.gif` —— 观察清单快照与 diff 流程
>
> 社区贡献演示素材欢迎提 PR！

### 🧯 常见问题

**Q：需要 Apple ID 或 API Key 吗？**
不需要。asoscope 只调用 Apple 公开、免密钥的只读端点。

**Q：为什么搜索结果和手机商店里顺序不完全一致？**
公开 Search API 的相关度排序与登录态、个性化推荐的商店前台存在差异，这是 Apple 端点本身的行为；可改用 `--sort rating|ratings` 获得确定性排序。

**Q：评论一次最多拿多少条？**
公开评论 RSS 每页最多约 50 条，可用 `--page` 翻页；Apple 不提供全站评论导出。

**Q：提示网络错误（退出码 3）怎么办？**
检查到 `itunes.apple.com` 的连通性，必要时调大 `--timeout`；asoscope 已内置指数退避重试。

---

## 💡 设计思路与迭代规划

### 🧱 技术选型理由

- **Python 3 标准库、零三方依赖**：`urllib` 完成 HTTP、`json/csv/dataclasses/argparse/unittest` 覆盖全部需求，换来最低安装成本与最强跨平台一致性，也彻底消除供应链依赖风险。
- **分层架构**：`http`（传输/重试/缓存）→ `models`（三种 Apple 载荷归一化）→ `api`（端点与业务过滤）→ `store`（本地状态）→ `render`（序列化）→ `cli`（参数与编排），每层可独立测试与替换。
- **可测试性优先**：传输层通过注入式 opener 解耦网络，测试全部使用真实抓取的接口夹具，离线、确定、快速。
- **本地优先、零遥测**：观察清单与缓存均为本地明文 JSON，原子写入，程序不包含任何上报逻辑。

### 🗺️ 迭代路线图

- [ ] v1.1：评论情感关键词聚合、评论多页自动合并导出
- [ ] v1.2：`watch diff` 输出 Markdown 报告并支持邮件 / Webhook 提醒
- [ ] v1.3：榜单历史采样与排名变化趋势
- [ ] v1.4：Mac App Store（macOS 软件）媒体类型支持
- [ ] v1.5：可选的 TOML 配置文件与批量查询任务清单

### 🙋 社区贡献方向

新增类目别名、补充语言文档、贡献演示素材、提交边界用例与 fixture、优化表格渲染等都非常欢迎，流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 📦 打包与部署指南

asoscope 属于**工具库类项目**（跨平台 Python 包，无原生二进制），因此不发布平台可执行文件，而是以 wheel 形式分发，任意平台 `pip install` 后即可使用。

### 🔨 从源码构建 wheel

```bash
# macOS / Linux（会先跑测试再打包）
bash scripts/build.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1

# 或使用 Makefile
make build
```

产物输出到 `dist/asoscope_cli-<version>-py3-none-any.whl`，这是通用 wheel（`py3-none-any`），同一文件可在三个平台安装：

```bash
pip install dist/asoscope_cli-1.0.0-py3-none-any.whl
```

### ✅ 运行测试

```bash
make test
# 等价于
python3 -m unittest discover -s tests -v
```

### 🚢 部署到服务器 / CI

```bash
pip install asoscope-cli
# 在 CI 中把结果直接落盘为制品
asoscope -c us charts top-free -n 50 -f json -o topfree.json
```

兼容环境：Python 3.8+ / Windows、macOS、Linux；无编译步骤、无原生依赖。

---

## 🤝 贡献指南

我们欢迎 Issue、PR 与文档改进！开始前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，核心约定：

1. **分支与提交**：使用 `feat/xxx`、`fix/xxx` 分支；提交信息遵循 Angular 规范（`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`）。
2. **零依赖红线**：新增运行时第三方依赖需先开 Issue 论证；标准库能实现的一律用标准库。
3. **测试必须离线通过**：新端点请补充脱敏夹具，不允许测试依赖联网。
4. **兼容性**：保持 Python 3.8 语法与标准库兼容，注意三平台路径差异。
5. 每个 PR 只做一件事，并同步更新 `CHANGELOG.md`。

---

## 📄 开源协议说明

本项目基于 **[MIT License](LICENSE)** 开源，允许自由使用、修改、分发与商用，保留版权与许可声明即可。

---

<div align="center">

如果 asoscope 帮你省下了翻商店的时间，欢迎点一个 ⭐ Star 支持！

**🌐 简体中文 · [繁體中文](docs/README.zh-TW.md) · [English](docs/README.en.md)**

</div>
