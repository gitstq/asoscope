<div align="center">

# 🔭 asoscope — 零相依 App Store 情報 CLI

**在終端機裡搜尋、剖析、比較、追蹤全球 App Store，只使用 Apple 公開端點，免登入、免金鑰、不下載 IPA。**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](#-設計理念與迭代規劃)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#-環境需求)
[![Tests](https://img.shields.io/badge/tests-54%20passed-success.svg)](#-執行測試)

**🌐 語言：[简体中文](../README.md) · 繁體中文 · [English](README.en.md)**

</div>

---

## 🎉 專案介紹

**asoscope** 是一款本地優先（local-first）的 App Store 情報命令列工具，適合獨立開發者、ASO（App Store 最佳化）從業人員、產品經理、竞品分析師與自動化流程使用。它把 Apple 官方的 **iTunes Search API** 與**公開 RSS 榜單／評論來源**封裝成一套簡潔、可組合、可匯出的終端機指令：搜尋全球各個店面的應用程式、讀取完整詮釋資料、擷取使用者評論與評分分布、瀏覽各分類榜單、橫向比較競品、把關注的應用程式加入本地觀察清單，並自動快照版本／價格／評分的變化。

### 😮‍💨 解決了什麼痛點

- 🧭 **查資料要開一堆分頁**：App Store 網頁版不利於大量查詢，也無法直接接進指令稿。asoscope 一條指令就回傳結構化結果，支援表格／JSON／CSV／Markdown 四種格式與檔案輸出。
- 🔐 **同類工具門檻與風險高**：部分工具需要 Apple ID 登入、呼叫私有端點，甚至下載 IPA 檔案，存在帳號與合規風險。asoscope **只存取 Apple 公開、免金鑰、唯讀的端點：不認證、不碰私有介面、不下載 IPA**。
- 🧱 **執行環境笨重**：許多 CLI 背著一長串第三方套件相依，安裝就像走進「相依地獄」。asoscope 只使用 **Python 3.8+ 標準函式庫，執行階段零第三方相依**，在 Windows／macOS／Linux 上行為完全一致。
- 📊 **竞品追蹤全靠手動**：內建本地觀察清單與快照差異比對，版本更新、調價、評分波動一目了然；資料只存在本機，完全沒有遙測。

### 💡 靈感來源與差異化

本專案的產品靈感來自 GitHub Trending 上榜專案 [majd/ipatool](https://github.com/majd/ipatool)（以 Go 撰寫、用於在終端機搜尋與下載 App Store 安裝包的工具）——它印證了「在終端機操作 App Store」是真實需求。但 asoscope **完全沒有複製它的程式碼**，並刻意走上一條更安全、更通用的差異化路線：

| 面向 | 傳統 IPA 工具 | **asoscope（本專案）** |
| --- | --- | --- |
| 端點性質 | 需 Apple ID 認證、牽涉私有端點 | ✅ 僅使用公開免金鑰的唯讀端點 |
| 合規風險 | 帳號與散布風險 | ✅ 不登入、不下載 IPA |
| 核心能力 | 下載安裝包 | ✅ 詮釋資料情報：搜尋／查詢／評論／榜單／比較／追蹤 |
| 執行相依 | 平台專屬執行檔 | ✅ Python 標準函式庫、零相依、跨平台 |
| 輸出形式 | 下載檔案 | ✅ 表格／JSON／CSV／Markdown，天生適合自動化 |

> ⚖️ asoscope 只使用 Apple 的公開資料端點，僅供合法的市場研究與開發分析用途，請遵守當地法規與 Apple 服務條款。

---

## ✨ 核心特性

- 🌍 **全球多店面搜尋** —— 支援任意 ISO 3166-1 雙字母地區（`us`／`jp`／`gb`／`cn`……），可選 iPhone／iPad 實體，具備分類、免費／付費、最低評分等篩選，以及相關度／評分／評價數／名稱四種排序。
- 🪪 **雙模式精準查詢** —— `lookup` 同時支援數字 Track ID 與 Bundle ID（例如 `com.duolingo.DuolingoMobile`），回傳 40 個以上的完整詮釋欄位。
- 💬 **公開評論擷取** —— 依「最新／最有幫助」排序分頁擷取使用者評論；`--stats` 一次輸出 1–5 星分布與該頁平均，快速掌握口碑。
- 🏆 **公開榜單瀏覽** —— 免費榜／付費榜／營收榜／新上架榜四類榜單，可指定地區、分類與數量。
- ⚖️ **竞品橫向比較** —— `compare` 接受 Track ID 與 Bundle ID 混合輸入，一張表呈現價格、版本、評分、分類等比較結果。
- 👀 **本地觀察清單 + 快照差異** —— `watch` 子指令把應用程式加入本機清單，重複快照後自動比對版本號、價格、平均評分、評價數、安裝包大小、發版日期的變化；**資料只會留在你的電腦上**。
- 🧮 **四種匯出格式** —— 對齊的終端機表格（**具備中日韓全形字元寬度感知，絕不錯位**）、JSON、CSV、Markdown，以 `-o` 隨意存檔，可直接銜接 Excel／BI／CI。
- 🧰 **零第三方執行階段相依** —— 僅用 Python 標準函式庫；內建 TTL 磁碟快取、指數退避重試與明確的結束碼，達到工程級穩健度。
- 🧪 **可離線執行的完整測試** —— 54 個單元測試以真實擷取並去敏感化的端點夾具執行，跑測試完全不需要連網。

---

## 🚀 快速開始

### 📌 環境需求

| 項目 | 需求 |
| --- | --- |
| Python | **3.8（含）以上**（已於 3.8／3.9／3.10／3.11／3.12 驗證） |
| 作業系統 | Windows 10+、macOS 11+、任何主流 Linux 發行版 |
| 網路 | 只需連得到 `itunes.apple.com`（Apple 公開端點） |
| 帳號／金鑰 | ❌ 不需要 Apple ID，也不需要任何 API Key |
| 第三方相依 | ❌ 零相依 |

確認 Python 版本：

```bash
python3 --version   # Windows 上通常是 python --version
```

### 📦 安裝方式

**方式一：pip 安裝（推薦）**

```bash
pip install asoscope-cli
```

**方式二：pipx 隔離安裝（CLI 工具的最佳實踐）**

```bash
pipx install asoscope-cli
```

**方式三：從原始碼免安裝執行**

```bash
git clone https://github.com/gitstq/asoscope.git
cd asoscope
python3 -m asoscope --version
```

安裝後驗證：

```bash
asoscope --version     # 顯示 asoscope 1.0.0
asoscope --help        # 查看全部指令
```

### ⚡ 一分鐘上手（可直接複製）

```bash
# 1. 搜尋美區免費的習慣養成 App，依評分排序，只看前 5 名
asoscope search "habit tracker" --price free --sort rating -n 5

# 2. 用 Bundle ID 查詢完整詮釋資料，輸出 JSON
asoscope lookup --bundle com.duolingo.DuolingoMobile -f json

# 3. 看日區遊戲類免費榜前 10 名，輸出 Markdown
asoscope -c jp charts top-free --genre games -n 10 -f md

# 4. 擷取某款應用程式最新一頁評論的評分分布
asoscope reviews 570060128 --stats

# 5. 把竞品加入觀察清單並建立快照
asoscope watch add 570060128
asoscope watch snapshot
asoscope watch diff
```

---

## 📖 詳細使用指南

### 🧭 指令總覽

```text
asoscope [全域參數] <指令> [指令參數]

指令：
  search    搜尋應用程式
  lookup    查詢單一應用程式的完整詮釋資料
  reviews   擷取公開使用者評論／評分分布
  charts    瀏覽公開榜單（免費／付費／營收／新上架）
  compare   比較兩款以上應用程式
  watch     本地觀察清單：add / rm / ls / snapshot / diff
  genres    列出支援的分類別名與數字 ID
```

### 🎛️ 全域參數（寫在子指令前後都可以）

| 參數 | 說明 | 預設值 |
| --- | --- | --- |
| `-c, --country` | App Store 店面，雙字母地區碼 | `us` |
| `-f, --format` | 輸出格式：`table`／`json`／`csv`／`md` | `table` |
| `-o, --output` | 把結果寫入檔案而非標準輸出 | — |
| `--timeout` | 單一請求逾時秒數 | `15` |
| `--no-cache` | 略過本機 TTL 快取 | 關閉 |
| `--data-dir` | 自訂 `watchlist.json` 所在資料夾 | 系統預設目錄 |

> 💡 兩種位置完全等價：`asoscope -f json search notion` 與 `asoscope search notion -f json` 的結果一致。

### 1) 🔍 search —— 搜尋應用程式

```bash
asoscope search <關鍵字> [選項]
```

| 參數 | 說明 |
| --- | --- |
| `-n, --limit` | 回傳數量，1–200，預設 20 |
| `--device` | `iphone`（預設）或 `ipad` |
| `--genre` | 分類別名（如 `games`、`productivity`）或 Apple 數字分類 ID |
| `--price` | `free`／`paid`／`all` |
| `--min-rating` | 只保留平均評分不低於此值的應用程式 |
| `--sort` | `relevance`（預設）／`rating`／`ratings`／`name` |

範例：

```bash
# 美區生產力類、平均 4.5 分以上的免費筆記 App，依評價數排序並匯出 CSV
asoscope search "notes" --genre productivity --price free \
  --min-rating 4.5 --sort ratings -f csv -o notes.csv
```

### 2) 🪪 lookup —— 完整詮釋資料

```bash
asoscope lookup --id 570060128                          # 依 Track ID
asoscope lookup --bundle com.duolingo.DuolingoMobile   # 依 Bundle ID
```

表格模式會逐欄展示：開發者、賣方、版本、價格與幣別、整體／現版本評分、分類、內容分級、安裝包大小（MB）、最低系統版本、支援語言、上架／發版時間、版本更新內容、商店連結、圖示與簡介。JSON 模式則輸出完整的正規化物件，方便程式取用。

### 3) 💬 reviews —— 使用者評論與口碑

```bash
asoscope reviews <track_id> [--page 1] [--sort recent|helpful] [--stats]
```

```bash
# 擷取第 2 頁「最有幫助」的評論，輸出 JSON
asoscope reviews 570060128 --page 2 --sort helpful -f json

# 只看評分分布（筆數、該頁平均、1–5 星計數）
asoscope reviews 570060128 --stats
```

### 4) 🏆 charts —— 榜單

```bash
asoscope charts <top-free|top-paid|top-grossing|new> [--genre 分類] [-n 數量]
```

```bash
# 港區財務類付費榜前 20 名
asoscope -c hk charts top-paid --genre finance -n 20
```

### 5) ⚖️ compare —— 竞品比較

輸入可混合 Track ID 與 Bundle ID，至少兩個：

```bash
asoscope compare 570060128 com.mojang.minecraftpe -f md
```

### 6) 👀 watch —— 本地觀察清單與變更監控

觀察清單是一份人類可讀的 JSON 檔（`watchlist.json`），只存在本機，絕不上傳。

```bash
asoscope watch add <track_id 或 bundle_id>   # ➕ 加入觀察（自動先查一次作為基線快照）
asoscope watch ls                            # 📋 列出全部觀察對象
asoscope watch snapshot                      # 📸 為所有觀察對象擷取新快照
asoscope watch snapshot --id 570060128       # 📸 只快照某一個
asoscope watch diff                          # 🔍 比對最近兩次快照的欄位變化
asoscope watch rm <track_id>                 # 🗑️ 移除觀察
```

常見做法是搭配系統排程（Linux／macOS 的 cron、Windows 的工作排程器）每天執行一次 `snapshot` 加上 `diff`，實現竞品版本／價格／評分的自動追蹤。`diff` 監測欄位：**版本號、價格、顯示價格、平均評分、評價數、安裝包大小、現版本發布日期**。

### 🗂️ 資料與快取資料夾（跨平台）

| 平台 | 資料目錄 | 快取目錄 |
| --- | --- | --- |
| Windows | `%LOCALAPPDATA%\asoscope` | `%LOCALAPPDATA%\asoscope\cache` |
| macOS | `~/Library/Application Support/asoscope` | `~/Library/Caches/asoscope` |
| Linux | `$XDG_DATA_HOME/asoscope` 或 `~/.local/share/asoscope` | `$XDG_CACHE_HOME/asoscope` 或 `~/.cache/asoscope` |

也可用環境變數 `ASOSCOPE_DATA_DIR`、`ASOSCOPE_CACHE_DIR` 或 `--data-dir` 參數覆寫。

### 🧑‍💻 作為 Python 套件整合

asoscope 同時是一個乾淨的函式庫，可直接嵌進你自己的程式：

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

### 🚦 結束碼約定（方便指令稿判斷）

| 結束碼 | 意義 |
| --- | --- |
| 0 | 成功 |
| 1 | 一般錯誤 |
| 2 | 參數使用錯誤（例如不合法的地區碼） |
| 3 | 網路／端點錯誤（含重試用盡） |
| 4 | 找不到目標應用程式 |
| 5 | 本機觀察清單讀寫錯誤 |

### 🖼️ 執行截圖／展示動圖

> 📸 截圖與終端機錄影預留位置，建議放置於 `docs/demo/` 資料夾，例如：
>
> - `docs/demo/search-demo.svg` —— 搜尋與多格式匯出
> - `docs/demo/watch-diff.gif` —— 觀察清單快照與差異比對流程
>
> 歡迎透過 PR 貢獻展示素材！

### 🧯 常見問題

**Q：需要 Apple ID 或 API Key 嗎？**
不需要。asoscope 只呼叫 Apple 公開、免金鑰的唯讀端點。

**Q：為什麼搜尋結果順序和手機上的 App Store 不完全一樣？**
公開 Search API 的相關度排序，與帶有登入狀態、個人化推薦的商店前台本來就不同，這是 Apple 端點本身的行為；可改用 `--sort rating|ratings` 取得具確定性的排序。

**Q：評論一次最多能抓幾筆？**
公開評論 RSS 每頁最多約 50 筆，可用 `--page` 往後翻頁；Apple 並未提供全站評論匯出。

**Q：出現網路錯誤（結束碼 3）怎麼辦？**
請檢查連往 `itunes.apple.com` 的連線，必要時調大 `--timeout`；asoscope 已內建指數退避重試。

---

## 💡 設計理念與迭代規劃

### 🧱 技術選型理由

- **Python 3 標準函式庫、零第三方相依**：`urllib` 負責 HTTP，`json`／`csv`／`dataclasses`／`argparse`／`unittest` 涵蓋其餘一切，換來最低安裝成本、最強跨平台一致性，也徹底消除供應鏈相依風險。
- **分層架構**：`http`（傳輸／重試／快取）→ `models`（三種 Apple 承載格式正規化）→ `api`（端點與商業篩選）→ `store`（本機狀態）→ `render`（序列化）→ `cli`（參數與編排），每一層都能獨立測試、獨立替換。
- **可測性優先**：傳輸層透過可注入的 opener 與網路解耦，測試全部使用真實擷取的端點夾具，離線、確定、快速。
- **本地優先、零遙測**：觀察清單與快取都是本機明文 JSON，採原子寫入；程式本身不含任何回報邏輯。

### 🗺️ 迭代路線圖

- [ ] v1.1：評論情感關鍵字聚合、評論多頁自動合併匯出
- [ ] v1.2：`watch diff` 輸出 Markdown 報告，並支援郵件／Webhook 通知
- [ ] v1.3：榜單歷史取樣與名次變化趨勢
- [ ] v1.4：支援 Mac App Store（macOS 軟體）媒體類型
- [ ] v1.5：選用的 TOML 設定檔與批次查詢工作清單

### 🙋 社群貢獻方向

新增分類別名、補充語言文件、貢獻展示素材、提交邊界案例與夾具、優化表格排版等都相當歡迎，流程請見 [CONTRIBUTING.md](../CONTRIBUTING.md)。

---

## 📦 打包與部署指南

asoscope 屬於**工具／函式庫類型的專案**（跨平台 Python 套件，沒有原生執行檔），因此以 wheel 形式釋出，而非各平台的執行檔：在任何平台上 `pip install` 即可使用。

### 🔨 從原始碼組建 wheel

```bash
# macOS / Linux（會先跑測試再打包）
bash scripts/build.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1

# 或使用 Makefile
make build
```

產物會輸出至 `dist/asoscope_cli-<version>-py3-none-any.whl`，這是通用 wheel（`py3-none-any`），同一個檔案就能在三個平台安裝：

```bash
pip install dist/asoscope_cli-1.0.0-py3-none-any.whl
```

### ✅ 執行測試

```bash
make test
# 等同於
python3 -m unittest discover -s tests -v
```

### 🚢 部署到伺服器／CI

```bash
pip install asoscope-cli
# 在 CI 中把結果直接存為產物
asoscope -c us charts top-free -n 50 -f json -o topfree.json
```

相容環境：Python 3.8+／Windows、macOS、Linux；無編譯步驟、無原生相依。

---

## 🤝 貢獻指南

歡迎提交 Issue、PR 與文件改進！開始前請先閱讀 [CONTRIBUTING.md](../CONTRIBUTING.md)，核心約定如下：

1. **分支與提交**：使用 `feat/xxx`、`fix/xxx` 分支；提交訊息遵循 Angular 規範（`feat:`／`fix:`／`docs:`／`refactor:`／`test:`／`chore:`）。
2. **零相依紅線**：新增執行階段第三方相依前請先開 Issue 討論；標準函式庫做得到的，一律使用標準函式庫。
3. **測試必須離線通過**：新端點請補上去敏感化夾具，測試不得依賴連網。
4. **相容性**：維持 Python 3.8 語法與標準函式庫相容，留意三平台路徑差異。
5. 每個 PR 只做一件事，並同步更新 `CHANGELOG.md`。

---

## 📄 授權條款說明

本專案以 **[MIT License](../LICENSE)** 釋出，允許自由使用、修改、散布與商業使用，惟須保留版權與授權聲明。

---

<div align="center">

如果 asoscope 幫你省下翻商店的時間，歡迎給一顆 ⭐ Star 鼓勵！

**🌐 [简体中文](../README.md) · 繁體中文 · [English](README.en.md)**

</div>
