# 線上宮廟解籤系統 (SoulGuanYin SaaS MVP)

結合傳統東方籤詩智慧與現代認知心理學的「線上宮廟智慧解籤與陪伴系統」MVP。

## 核心理念
- **非算命、非八字預測**：將籤詩與典故作為心理投射 (Psychological Projection) 與認知再架構 (Cognitive Reframing) 的輔助工具。
- **行動指引**：依據使用者的真實處境，產出清晰具體的行動建議 (Do's & Don'ts) 與同理陪伴。
- **260 首傳統靈籤全集**：內建完整三大宮廟靈籤資料庫，支援靈活切換。
- **輕量零設定**：採用本機 **SQLite** 資料庫，開箱即用。

---

## 內建籤詩庫 (共 260 首)

| 籤詩系統 | 籤號範圍 | 簡介與特色 |
| :--- | :--- | :--- |
| ⛩️ **六十甲子籤** | 第 1 ~ 60 籤 | 台灣各大媽祖廟、傳統民間宮廟最通用之六十甲子籤詩。 |
| ⚔️ **關聖帝君一百籤** | 第 1 ~ 100 籤 | 行天宮等關帝廟通用之雷雨師一百首靈籤，以處世智慧、義理著稱。 |
| 🪷 **觀音靈籤一百首** | 第 1 ~ 100 籤 | 龍山寺、普陀山等觀音廟宇百首靈籤，慈悲撫慰、啟迪心性。 |

---

## 快速啟動指南

### 1. 安裝 Python 依賴套件
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
將 `.env.example` 複製為 `.env`，並填入 OpenAI API Key（若未填入則會以 Mock 模式運行）：
```env
# 資料庫設定 (預設使用本機 SQLite 檔案)
DB_PATH=temple.db

# LLM 設定
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o
```

### 3. 資料庫自動初始化
系統啟動時會**自動建立 SQLite 資料表並完整注入 260 首籤詩資料**（儲存於 `temple.db`），無需手動執行任何 SQL 指令！

> 如需手動檢視或自訂 SQL 結構，可直接查閱 `schema.sql`。

### 4. 啟動後端伺服器
```bash
python main.py
```
伺服器將在 `http://localhost:8000` 運行，開啟瀏覽器即可切換不同籤系進行抽籤與心理學賦權解籤！

---

## API 端點

- `GET /`：網頁操作介面 (支援三大籤系切換)
- `GET /api/lot_types`：取得支援的籤詩系統清單
- `POST /api/interpret`：抽籤與 AI 智慧解籤（支援指定 `lot_type` 與 `lot_number`）
- `GET /api/health`：系統健康檢查與 260 首籤詩資料庫載入狀態
- `GET /docs`：Swagger API 互動式文件
