# 任務：每日財經新聞爬蟲與摘要

## 目標
建立一個可透過設定檔自訂排程時間與收件人的爬蟲系統，自動抓取指定財經新聞網站的最新資訊，
並整理成結構化的每日摘要報告（國際 + 台灣分開），重要新聞需特別標示。
報告預設儲存為本地 Markdown 檔案；若有設定 Email，則額外寄送報告。

---

## 爬蟲來源清單

### 國際財經（5 個）
1. Bloomberg - https://www.bloomberg.com
2. Reuters - https://www.reuters.com/finance
3. Financial Times - https://www.ft.com
4. Wall Street Journal - https://www.wsj.com
5. CNBC - https://www.cnbc.com/finance

### 台灣財經（4 個）
1. 經濟日報 - https://money.udn.com
2. 工商時報 - https://www.ctee.com.tw
3. MoneyDJ 理財網 - https://www.moneydj.com
4. 數位時代 - https://www.bnext.com.tw

---

## 功能需求

### 1. 爬蟲功能
- 使用 Python 實作，套件優先考慮 `requests` + `BeautifulSoup` 或 `playwright`（針對動態渲染頁面）
- 每個網站抓取當天最新新聞，標題 + 摘要 + 連結，數量上限每站 **10 則**
- 需處理反爬機制（User-Agent、請求間隔、retry 邏輯）
- 若某網站爬取失敗，記錄錯誤 log 並跳過，不影響整體流程

### 2. 重要新聞判斷邏輯
以下條件符合其中之一即視為重要新聞，需特別 highlight：
- 標題包含關鍵字：`央行`、`Fed`、`升息`、`降息`、`通膨`、`CPI`、`GDP`、`裁員`、`倒閉`、`IPO`、`AI`、`半導體`、`台積電`、`輝達`、`nvidia`、`漲價`（不分大小寫）

### 3. 輸出格式
產出一份 Markdown 檔案，檔名格式：`daily_finance_news_YYYYMMDD.md`

內容結構如下：
- 重要新聞前加上 `⭐ **[重要]**` 標示
- 國際與台灣分區，各網站分小節

### 4. 美股昨日收盤價追蹤

每日報告需額外抓取以下標的**昨日收盤資料**，並顯示於報告最頂端獨立區塊：

| 標的 | 代號 | 資料來源建議 |
| ---- | ---- | ---------- |
| 道瓊工業平均指數 | ^DJI | Yahoo Finance |
| 標準普爾 500 指數 | ^GSPC | Yahoo Finance |
| 納斯達克綜合指數 | ^IXIC | Yahoo Finance |
| 羅素 2000 | ^RUT | Yahoo Finance |
| 美國 20 年期公債 ETF | TLT | Yahoo Finance |
| 台積電 ADR | TSM | Yahoo Finance |

- 使用 `yfinance` 套件抓取昨日收盤價、漲跌金額、漲跌幅（%）
- 若當天為週末或假日，顯示最近一個交易日數據，並標注實際日期
- 漲跌幅以顏色符號標示：上漲用 `▲`，下跌用 `▼`，持平用 `─`
- 輸出格式範例：
```markdown
## 📈 美股昨日收盤（2025-01-15）

| 指數／標的 | 收盤價 | 漲跌 | 漲跌幅 |
|-----------|--------|------|--------|
| 道瓊（^DJI） | 43,153.13 | ▼ -241.83 | -0.56% |
| S&P 500（^GSPC） | 5,842.47 | ▼ -40.53 | -0.69% |
| 納斯達克（^IXIC） | 19,338.29 | ▼ -109.56 | -0.56% |
| 羅素 2000（^RUT） | 2,215.36 | ▲ +12.44 | +0.56% |
| TLT | 88.23 | ▲ +0.45 | +0.51% |
| 台積電 ADR（TSM） | 198.72 | ▼ -3.28 | -1.62% |
```

### 5. Email 寄送功能（選用）

#### 5-1. 預設行為
- **Email 功能預設為關閉**，報告僅儲存至本地 `output/` 資料夾
- 若使用者未在 `config.yaml` 中設定 Email 區塊，或 `enabled: false`，程式不會嘗試寄信，也不會報錯
- 只有明確設定 `enabled: true` 且填寫完整設定後，才會啟用寄送流程

#### 5-2. Email 設定方式（需要時才填寫）
在 `config.yaml` 中加入以下區塊即可啟用：
```yaml
email:
  enabled: true                        # 改為 true 才會啟用寄送，預設 false
  method: gmail_oauth                  # 使用 OAuth 2.0，不需輸入密碼
  sender_address: your@gmail.com
  credentials_file: credentials.json  # 從 Google Cloud Console 下載
  token_file: token.json              # 第一次授權後自動產生，之後免登入
  subject_template: "📰 每日財經摘要 {date}"
  recipients:
    - user1@example.com
    - user2@example.com
```

#### 5-3. Gmail OAuth 初次設定步驟（只需做一次）
1. 前往 [Google Cloud Console](https://console.cloud.google.com/) 建立新專案
2. 啟用 **Gmail API**
3. 建立 OAuth 2.0 憑證，類型選「**桌面應用程式**」
4. 下載 `credentials.json`，放到專案根目錄
5. 第一次執行時，瀏覽器自動開啟請你登入 Google 帳號並授權
6. 授權完成後自動產生 `token.json`，**之後排程執行完全不需要人工介入**

#### 5-4. Email 內容規格
- 郵件主旨由 `subject_template` 決定，`{date}` 自動替換為當日日期
- 郵件本文將 Markdown 報告轉換為 **HTML 格式**寄出（使用 `markdown2` 套件）
- 同時附加原始 `.md` 檔案作為附件

#### 5-5. 安全性說明
- `credentials.json` 與 `token.json` 請加入 `.gitignore`，不要上傳至 Git
- 不需要密碼，也不需要開啟「低安全性應用程式存取」

### 6. 排程設定

排程時間統一透過 `config.yaml` 設定，程式以 `schedule` 套件讀取並執行，**無需手動修改 crontab**。

#### 6-1. 設定方式
```yaml
schedule:
  enabled: true          # true / false，控制是否啟用內建排程
  run_time: "05:00"      # 每日執行時間，格式 HH:MM（24 小時制）
  timezone: "Asia/Taipei"
```

#### 6-2. 執行方式
```bash
# 啟動常駐排程模式（程式會持續運行，依設定時間自動觸發）
python main.py --schedule

# 立即執行一次（忽略排程設定，用於測試）
python main.py --run-now
```

#### 6-3. 若需使用系統排程（選用）
若偏好使用 Windows Task Scheduler，可將 `schedule.enabled` 設為 `false`，
再透過工作排程器設定：
- 動作：執行 `python main.py --run-now`
- 觸發器：每天 05:00

### 7. 其他
- 產出的 Markdown 檔統一存放在專案內的 `output/` 資料夾
- 提供 `requirements.txt`
- 提供 `README.md` 說明如何安裝、設定 `config.yaml` 與啟動

---

## 技術限制與偏好
- 語言：Python 3.10+
- 不使用付費 API
- 盡量避免被封鎖，請加入適當的請求延遲（每站間隔 2~5 秒）

---

## 專案結構（建議）
```
project/
├── main.py               # 程式進入點，支援 --schedule / --run-now
├── config.yaml           # 所有設定：排程時間、Email 收件人、寄送開關
├── credentials.json      # Gmail OAuth 憑證（需加入 .gitignore）
├── token.json            # Gmail OAuth Token（自動產生，需加入 .gitignore）
├── requirements.txt
├── README.md
├── scrapers/             # 各網站爬蟲模組
├── notifier/             # Email 寄送模組（enabled: false 時自動跳過）
├── output/               # 每日產出的 Markdown 報告（必定產出）
└── logs/                 # 錯誤與執行 log
```
