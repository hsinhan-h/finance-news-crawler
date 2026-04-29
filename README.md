# 每日財經新聞爬蟲與摘要

自動抓取國際與台灣財經新聞，產生每日 Markdown 摘要報告，可選擇性寄送 Email。

---

## 功能

- 抓取 9 個財經新聞網站（5 國際 + 4 台灣），每站最多 10 則
- 追蹤美股 6 個指數／標的的昨日收盤資料（yfinance）
- 自動標示重要新聞（含關鍵字偵測）
- 報告輸出至 `output/` 資料夾（Markdown 格式）
- 可選：透過 SMTP 或 Gmail OAuth 寄送 HTML 報告 + 附件
- 可選：內建每日排程（`schedule` 套件）

---

## 安裝

### 環境需求
- Python 3.10+

### 安裝相依套件

```bash
pip install -r requirements.txt
```

---

## 設定 config.yaml

開啟 `config.yaml` 並依需求調整：

```yaml
schedule:
  enabled: false       # true = 啟動常駐排程模式
  run_time: "05:00"    # 24 小時制
  timezone: "Asia/Taipei"

email:
  enabled: false       # 改為 true 才會寄信
  ...

crawler:
  max_articles_per_site: 10
  request_delay_min: 2
  request_delay_max: 5
```

---

## 執行

```bash
# 立即執行一次（測試用）
python main.py --run-now

# 啟動常駐排程模式（依 config.yaml 時間每日自動執行）
python main.py --schedule
```

報告會儲存在 `output/daily_finance_news_YYYYMMDD.md`。

---

## 啟用 Email 功能（選用，只需設定一次）

### 方案 A：使用通用 SMTP

適合 Outlook、公司信箱、自架 mail server，也可用 Gmail SMTP 搭配 App Password。

```yaml
email:
  enabled: true
  method: smtp
  sender_address: alerts@example.com
  host: smtp.example.com
  port: 587
  security: starttls
  username: alerts@example.com
  password: your_smtp_password
  subject_template: "📰 每日財經摘要 {date}"
  recipients:
    - recipient@example.com
```

欄位說明：
- `security`: 支援 `ssl`、`starttls`、`none`
- `port`: 常見為 `465`（SSL）或 `587`（STARTTLS）
- `username` / `password`: SMTP 帳密；若你的服務要求 App Password，請填 App Password

### 方案 B：使用 Gmail OAuth

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)，建立新專案
2. 啟用 **Gmail API**（API 和服務 → 程式庫 → 搜尋 Gmail API → 啟用）
3. 建立 OAuth 2.0 憑證（API 和服務 → 憑證 → 建立憑證 → OAuth 用戶端 ID）
   - 應用程式類型選「**桌面應用程式**」
4. 下載 `credentials.json`，放到專案根目錄

```yaml
email:
  enabled: true
  method: gmail_oauth
  sender_address: your@gmail.com
  credentials_file: credentials.json
  token_file: token.json
  subject_template: "📰 每日財經摘要 {date}"
  recipients:
    - recipient@example.com
```

第一次執行時，瀏覽器會自動開啟 Google 登入頁面。授權後自動產生 `token.json`，之後排程執行完全免手動操作。

```bash
python main.py --run-now
```

### 安全性

- `credentials.json` 與 `token.json` 已加入 `.gitignore`，請勿上傳至 Git
- 若使用 SMTP，建議改用 `.env` 或系統環境變數管理密碼，不要把真實密碼提交到版本控制

---

## 若使用 Windows 工作排程器

將 `config.yaml` 中的 `schedule.enabled` 設為 `false`，再透過「工作排程器」設定：
- **動作**：`python C:\path\to\main.py --run-now`
- **觸發器**：每天 05:00

---

## 專案結構

```
finance-news-crawler/
├── main.py               # 程式進入點
├── config.yaml           # 所有設定
├── requirements.txt
├── README.md
├── stock_tracker.py      # 美股資料抓取（yfinance）
├── report_generator.py   # Markdown 報告生成
├── scrapers/             # 各網站爬蟲模組
│   ├── base.py
│   ├── bloomberg.py
│   ├── reuters.py
│   ├── ft.py
│   ├── wsj.py
│   ├── cnbc.py
│   ├── udn.py
│   ├── ctee.py
│   ├── moneydj.py
│   └── bnext.py
├── notifier/
│   ├── email_sender.py   # Email 寄送分流
│   ├── smtp_sender.py    # SMTP 寄信
│   └── gmail_sender.py   # Gmail OAuth 寄信
├── output/               # 每日產出的 Markdown 報告
└── logs/                 # 執行 log
```

---

## 重要新聞關鍵字

以下關鍵字（不分大小寫）任一出現於標題或摘要，即標示為 ⭐ 重要：

`央行`、`Fed`、`升息`、`降息`、`通膨`、`CPI`、`GDP`、`裁員`、`倒閉`、`IPO`、`AI`、`半導體`、`台積電`、`輝達`、`nvidia`、`漲價`
