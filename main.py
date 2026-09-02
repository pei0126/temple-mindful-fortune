import os
import json
import time
import logging
import sqlite3
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

# 載入環境變數
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ==============================================================================
# 環境變數與多模型 (Multi-Model) 支援設定
# ==============================================================================
DB_PATH = os.getenv("DB_PATH", "temple.db").strip()
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gemini-3.1-flash-lite-preview").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "temple888").strip()

# 支援的多模型清單 (Multi-Model Catalog)
AVAILABLE_MODELS = [
    {
        "id": "gemini-3.1-flash-lite-preview",
        "name": "Gemini 3.1 Flash-Lite Preview",
        "provider": "Google Gemini",
        "badge": "推薦・極速",
        "description": "Google 最新 Gemini 3.1 輕量預覽版，推理速度極快且同理心高"
    },
    {
        "id": "gemini-3.1-pro-preview",
        "name": "Gemini 3.1 Pro Preview",
        "provider": "Google Gemini",
        "badge": "深度推理",
        "description": "Google 旗艦思考模型，擅長複雜人生處境深層洞察"
    },
    {
        "id": "gemini-3-flash-preview",
        "name": "Gemini 3 Flash Preview",
        "provider": "Google Gemini",
        "badge": "旗艦閃速",
        "description": "Google 新一代平衡型模型，兼具速度與細膩筆觸"
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "provider": "OpenAI",
        "badge": "OpenAI 旗艦",
        "description": "OpenAI 旗艦全能模型，邏輯條理分明"
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o mini",
        "provider": "OpenAI",
        "badge": "輕量快速",
        "description": "OpenAI 輕巧型模型，反應迅速"
    }
]

def normalize_model_name(raw_name: Optional[str]) -> str:
    """自動正規化模型名稱，支援人類可讀名稱與 API ID"""
    if not raw_name:
        raw_name = OPENAI_MODEL or "gemini-3.1-flash-lite-preview"
    
    name = raw_name.strip()
    lower = name.lower().replace(" ", "-").replace("_", "-")
    
    # 處理常見 Google Gemini 名稱對應
    if "gemini-3.1-flash-lite" in lower:
        return "gemini-3.1-flash-lite-preview"
    if "gemini-3.1-pro" in lower:
        return "gemini-3.1-pro-preview"
    if "gemini-3-flash" in lower:
        return "gemini-3-flash-preview"
    if "gemini-2.5-flash-lite" in lower:
        return "gemini-2.5-flash-lite"
    if "gemini-2.5-flash" in lower:
        return "gemini-2.5-flash"
    if "gemini-2.5-pro" in lower:
        return "gemini-2.5-pro"
    if "gpt-4o-mini" in lower:
        return "gpt-4o-mini"
    if "gpt-4o" in lower:
        return "gpt-4o"
    if "gemini" in lower:
        return lower
        
    return name

# 全域管理員執行時期預設模型
current_runtime_model: str = normalize_model_name(OPENAI_MODEL)

def get_llm_client(requested_model: Optional[str] = None) -> tuple[Optional[OpenAI], str]:
    """
    動態根據模型與 API Key 取得對應的 OpenAI Client (支援 Google Gemini 與 OpenAI 相容端點)
    """
    api_key = OPENAI_API_KEY
    if not api_key or api_key.startswith("your-") or api_key.startswith("sk-your"):
        return None, "mock"

    model_id = normalize_model_name(requested_model or current_runtime_model)
    base_url = OPENAI_BASE_URL

    # 自動偵測端點：若為 Google Gemini 密鑰或 Gemini 模型且未自訂 base_url，導向 Google OpenAI 相容端點
    if not base_url:
        if api_key.startswith("AQ.") or api_key.startswith("AIza") or model_id.startswith("gemini"):
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        elif model_id.startswith("deepseek"):
            base_url = "https://api.deepseek.com/v1"

    try:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        return client, model_id
    except Exception as e:
        logger.warning(f"Failed to create LLM client for {model_id}: {e}")
        return None, model_id

# ==============================================================================
# 支援的籤詩系統定義
# ==============================================================================
LOT_SYSTEMS = {
    "60_jiazi": {
        "id": "60_jiazi",
        "name": "六十甲子籤",
        "title": "媽祖 / 六十甲子靈籤",
        "max_lots": 60,
        "description": "台灣最普及的傳統媽祖與民間宮廟六十甲子籤詩。"
    },
    "guandi_100": {
        "id": "guandi_100",
        "name": "關聖帝君一百籤",
        "title": "關聖帝君雷雨師一百籤",
        "max_lots": 100,
        "description": "行天宮等關帝廟宇通用之雷雨師一百首靈籤，以義理與處世指引著稱。"
    },
    "guanyin_100": {
        "id": "guanyin_100",
        "name": "觀音靈籤一百首",
        "title": "觀音佛祖一百靈籤",
        "max_lots": 100,
        "description": "普陀山與龍山寺等觀音廟宇百首靈籤，慈悲撫慰、啟迪心靈智慧。"
    }
}

# ==============================================================================
# SQLite 資料庫初始化與連線輔助
# ==============================================================================
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    """初始化 SQLite 資料庫與完整籤詩種子資料 (260 首)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 建立 lots 表 (含 lot_type 支援多籤系)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_type TEXT NOT NULL,
                    lot_type_name TEXT NOT NULL,
                    lot_number INTEGER NOT NULL,
                    lot_name TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    content TEXT NOT NULL,
                    story TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(lot_type, lot_number)
                );
            """)
            
            # 建立 user_draws 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_draws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_id INTEGER,
                    lot_type TEXT DEFAULT '60_jiazi',
                    lot_number INTEGER NOT NULL,
                    user_question TEXT NOT NULL,
                    ai_analysis TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL
                );
            """)
            
            # 建立索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_lots_type_number ON lots(lot_type, lot_number);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_draws_created_at ON user_draws(created_at DESC);")
            
            # 檢查並載入籤詩種子資料
            cursor.execute("SELECT COUNT(*) FROM lots")
            count = cursor.fetchone()[0]
            
            if count < 260:
                json_path = os.path.join(os.path.dirname(__file__), "data", "lots_all.json")
                if os.path.exists(json_path):
                    logger.info("Loading 260 lots from data/lots_all.json into SQLite...")
                    with open(json_path, "r", encoding="utf-8") as f:
                        all_lots = json.load(f)
                        for lot in all_lots:
                            cursor.execute("""
                                INSERT OR REPLACE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                lot["lot_type"],
                                lot["lot_type_name"],
                                lot["lot_number"],
                                lot["lot_name"],
                                lot["grade"],
                                lot["content"],
                                lot["story"]
                            ))
                    conn.commit()
                    logger.info("Successfully seeded 260 lots into SQLite database.")
        
        logger.info(f"SQLite database is ready at: {DB_PATH}")
    except Exception as e:
        logger.error(f"Error initializing SQLite database: {e}")

# ==============================================================================
# 資料結構定義 (Pydantic Models)
# ==============================================================================
class InterpretRequest(BaseModel):
    lot_type: str = Field(default="60_jiazi", description="籤詩系統 (60_jiazi / guandi_100 / guanyin_100)")
    lot_number: int = Field(..., ge=1, le=100, description="抽取的籤號 (1 ~ 60 或 1 ~ 100)")
    user_question: str = Field(..., min_length=2, max_length=500, description="使用者目前面臨的困境或想詢問的事情")
    model: Optional[str] = Field(default=None, description="選用的 AI 模型 (如未指定則採用管理員預設模型)")

class AdminAuthRequest(BaseModel):
    password: str = Field(..., description="管理員密碼")

class AdminSetModelRequest(BaseModel):
    model: str = Field(..., description="欲設定為全站預設的 AI 模型 ID")
    password: Optional[str] = Field(default=None, description="管理員密碼")

class AdminTestConnectionRequest(BaseModel):
    model: Optional[str] = Field(default=None, description="欲測試的模型 ID")
    password: Optional[str] = Field(default=None, description="管理員密碼")

class ActionGuide(BaseModel):
    dos: List[str] = Field(description="建議採取的具體行動 (Do's)")
    donts: List[str] = Field(description="建議避免的盲點或心態 (Don'ts)")

class StructuredAnalysis(BaseModel):
    poem_interpretation: str = Field(description="籤意白話轉譯與核心意境")
    story_inspiration: str = Field(description="典故故事與現代心理學啟示")
    situation_analysis: str = Field(description="結合使用者問題的當下處境剖析")
    actions: ActionGuide = Field(description="具體行動指南")
    encouragement: str = Field(description="富有同理心與力量的溫暖結語")

class LotInfo(BaseModel):
    id: Optional[str] = None
    lot_type: str = "60_jiazi"
    lot_type_name: str = "六十甲子籤"
    lot_number: int
    lot_name: str
    grade: str
    content: str
    story: str

class InterpretResponse(BaseModel):
    success: bool
    lot: LotInfo
    analysis: StructuredAnalysis
    model_used: str
    draw_id: Optional[str] = None

# ==============================================================================
# Lifespan 事件管理
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 應用程式啟動時初始化資料庫
    init_sqlite_db()
    client, model_id = get_llm_client()
    if client:
        logger.info(f"AI Engine initialized. Default model: {model_id}")
    else:
        logger.warning("No valid API Key detected. Fallback Mock mode active.")
    yield

# ==============================================================================
# FastAPI 應用實例建立
# ==============================================================================
app = FastAPI(
    title="Online Temple Fortune Interpretation API",
    description="SaaS 級線上宮廟智慧解籤系統 (支援六十甲子籤、關聖帝君一百籤、觀音靈籤一百首、管理者多模型後台與心理學解讀)",
    version="1.3.0",
    lifespan=lifespan
)

# 啟用 CORS 跨來源資源共用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Helper Functions
# ==============================================================================
def fetch_lot_from_db(lot_type: str, lot_number: int) -> LotInfo:
    """從 SQLite 取得特定籤系與籤號的籤詩資料"""
    if lot_type not in LOT_SYSTEMS:
        lot_type = "60_jiazi"

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lots WHERE lot_type = ? AND lot_number = ?", (lot_type, lot_number))
            row = cursor.fetchone()
            if row:
                return LotInfo(
                    id=str(row["id"]),
                    lot_type=row["lot_type"],
                    lot_type_name=row["lot_type_name"],
                    lot_number=row["lot_number"],
                    lot_name=row["lot_name"],
                    grade=row["grade"],
                    content=row["content"],
                    story=row["story"]
                )
    except Exception as e:
        logger.error(f"Error fetching lot from SQLite: {e}")

    system_info = LOT_SYSTEMS.get(lot_type, LOT_SYSTEMS["60_jiazi"])
    return LotInfo(
        id=None,
        lot_type=lot_type,
        lot_type_name=system_info["name"],
        lot_number=lot_number,
        lot_name=f"第 {lot_number} 籤",
        grade="吉",
        content="日出便見風雲散，\n光明清淨照世間。\n一向前途通大道，\n萬事清吉保平安。",
        story="傳統典故。寓意撥雲見日，循序漸進，守持正念。"
    )

def generate_ai_interpretation(lot: LotInfo, user_question: str, requested_model: Optional[str] = None) -> tuple[StructuredAnalysis, str]:
    """呼叫指定 LLM (Gemini 3.1 / GPT-4o 等) 進行嚴謹心理學視角的結構化解籤"""
    target_model = requested_model or current_runtime_model
    client, model_id = get_llm_client(target_model)
    
    if not client:
        # Mock Response when API key is missing
        logger.info("Using Fallback Mock Interpretation Engine.")
        analysis = StructuredAnalysis(
            poem_interpretation=f"此籤（{lot.lot_type_name} {lot.lot_name}）象徵著當前的混沌局勢即將迎來轉機。籤詩以『日出風雲散』為喻，表明外在的阻礙與內心的焦慮正逐步消退，前方的道路正在展開。",
            story_inspiration=f"借鑑典故【{lot.story}】，古人在面對困境時，關鍵在於堅守正道並保持耐性。這在心理學上相當於『情緒沉澱與認知重構』，唯有先穩住內在定力，方能看清外在局勢。",
            situation_analysis=f"針對你所詢問的『{user_question}』：你目前可能正處於過渡期的心理拉扯中，容易被局部的未確定性所困擾。籤詩提示你，目前最需要的不是慌忙尋找外在解答，而是釐清當前能夠由自己掌控的核心要素。",
            actions=ActionGuide(
                dos=[
                    "將焦點放在當下可直接控制的具體任務上，採取小步前進策略。",
                    "主動與信任的夥伴或專業前輩溝通，尋求客觀回饋。",
                    "給自己設定明確的休整時間，避免在焦慮時做出重大決策。"
                ],
                donts=[
                    "避免陷入非黑即白的極端思維，不要過度放大暫時的挫折。",
                    "切忌隨波逐流或急於求成而忽略了基本功的積累。",
                    "不要將責任全盤歸咎於外在環境，而放棄了自我能動性。"
                ]
            ),
            encouragement="籤詩是心靈的鏡子，真正的力量始終在你自己的心中。保持從容與信念，每一步紮實的探索都在為你的蛻變累積能量。"
        )
        return analysis, "內建心理學模擬引擎 (Fallback)"

    system_prompt = """你是一位結合傳統東方智慧與現代認知心理學的「智慧解籤員與心靈陪伴導師」。
【嚴格原則與底線】：
1. 絕不進行算命、預測未來吉凶、八字算命、鐵口直斷或怪力亂神。
2. 你的核心任務是：把籤詩原文與歷史典故作為「心理投射 (Psychological Projection)」與「認知再架構 (Cognitive Reframing)」的工具。
3. 具備高度同理心、溫暖且理性，引導使用者從當下的焦慮或困境中，梳理出清晰的思緒與具體可行、可落地的行動建議 (Do's & Don'ts)。
4. 請嚴格以繁體中文輸出符合指定 JSON Schema 的結構化格式。
"""

    user_prompt = f"""
【求籤者詢問事項/困境】：
{user_question}

【抽得籤詩資訊】：
- 籤詩系統：{lot.lot_type_name}
- 籤號：{lot.lot_name} (第 {lot.lot_number} 籤)
- 評等：{lot.grade}
- 籤詩原文：
{lot.content}
- 典故歷史：
{lot.story}

請依照上述資訊，為求籤者提供結構化的解析。必須嚴格輸出為以下 JSON 格式：
{{
  "poem_interpretation": "籤意白話轉譯 (以白話深入淺出闡述籤詩象徵的核心意境)",
  "story_inspiration": "典故現代啟示 (解析歷史典故背後的心理學象徵意義與思維啟發)",
  "situation_analysis": "處境解析 (結合使用者所問的具體問題，分析其當下心理盲點與局勢要點)",
  "actions": {{
    "dos": [
      "具體行動建議 1",
      "具體行動建議 2",
      "具體行動建議 3"
    ],
    "donts": [
      "應避免的盲點或心態 1",
      "應避免的盲點或心態 2",
      "應避免的盲點或心態 3"
    ]
  }},
  "encouragement": "結語陪伴 (溫暖、賦權 Empowering 且具同理心的支持話語)"
}}
"""

    try:
        logger.info(f"Invoking AI model: {model_id} for user question...")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        return StructuredAnalysis(**parsed), model_id
    except Exception as e:
        logger.error(f"Error calling LLM ({model_id}): {e}")
        # 若大模型發生異常，優雅降級回退為結構化模擬解讀
        fallback_analysis = StructuredAnalysis(
            poem_interpretation=f"此籤（{lot.lot_type_name} {lot.lot_name}）寓意轉機在即，沉著以對。籤文提示當前應先調順心態，方能在變動中洞察先機。",
            story_inspiration=f"典故【{lot.story}】提示我們：行穩致遠，先求定力再求突破。",
            situation_analysis=f"針對您所提問的『{user_question}』：當前局勢的核心關鍵在於梳理能夠掌控的要素，切忌急躁躁進。",
            actions=ActionGuide(
                dos=["先理清客觀事實，將目標拆解為每日可行的小任務。", "與信任的前輩或夥伴交流反饋。"],
                donts=["避免在焦慮時做重大決策。", "切忌被一時的情緒波折牽著走。"]
            ),
            encouragement="心安則道隆，給自己一點沉澱的時間，答案就在內心深處。"
        )
        return fallback_analysis, f"{model_id} (降級防護模式)"

def save_draw_record(lot: LotInfo, user_question: str, analysis: StructuredAnalysis) -> Optional[str]:
    """將抽籤結果存入 SQLite user_draws 表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            lot_id_val = int(lot.id) if lot.id and str(lot.id).isdigit() else None
            cursor.execute("""
                INSERT INTO user_draws (lot_id, lot_type, lot_number, user_question, ai_analysis)
                VALUES (?, ?, ?, ?, ?)
            """, (
                lot_id_val,
                lot.lot_type,
                lot.lot_number,
                user_question,
                json.dumps(analysis.model_dump(), ensure_ascii=False)
            ))
            conn.commit()
            return str(cursor.lastrowid)
    except Exception as e:
        logger.error(f"Error saving draw to SQLite: {e}")
        return None

# ==============================================================================
# API Endpoints
# ==============================================================================
@app.get("/api/models")
async def get_available_models():
    """取得支援的多模型清單與當前管理員設定的預設模型"""
    return {
        "success": True,
        "current_default": current_runtime_model,
        "models": AVAILABLE_MODELS
    }

@app.post("/api/admin/verify")
async def verify_admin(req: AdminAuthRequest):
    """【管理者安全驗證】驗證管理員通行密碼"""
    if req.password.strip() == ADMIN_PASSWORD:
        return {"success": True, "message": "管理員密碼驗證成功"}
    raise HTTPException(status_code=401, detail="管理員密碼錯誤，請重新輸入")

@app.post("/api/admin/set_model")
async def admin_set_model(req: AdminSetModelRequest, x_admin_password: Optional[str] = Header(None)):
    """【管理者 API】切換全站執行時期預設 AI 模型 (需密碼授權)"""
    provided_password = (req.password or x_admin_password or "").strip()
    if provided_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="管理者密碼驗證失敗，無權限執行此操作")

    global current_runtime_model
    normalized = normalize_model_name(req.model)
    current_runtime_model = normalized
    logger.info(f"Admin updated global runtime AI model to: {current_runtime_model}")
    return {
        "success": True,
        "message": f"全站預設 AI 模型已成功切換為: {current_runtime_model}",
        "active_model": current_runtime_model
    }

@app.post("/api/admin/test_connection")
async def admin_test_connection(req: AdminTestConnectionRequest, x_admin_password: Optional[str] = Header(None)):
    """【管理者 API】一鍵測試指定模型之 API 連線與延遲回應 (需密碼授權)"""
    provided_password = (req.password or x_admin_password or "").strip()
    if provided_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="管理者密碼驗證失敗，無權限執行此操作")

    target = req.model or current_runtime_model
    client, model_id = get_llm_client(target)
    
    if not client:
        return {
            "success": False,
            "model": model_id,
            "latency_ms": 0,
            "message": "未檢測到有效 API Key (目前處於 Mock 模擬模式)"
        }
        
    start_time = time.time()
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        latency = int((time.time() - start_time) * 1000)
        return {
            "success": True,
            "model": model_id,
            "latency_ms": latency,
            "message": f"連線成功！模型反應正常（耗時 {latency}ms）"
        }
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        logger.error(f"Admin connection test failed for {model_id}: {e}")
        return {
            "success": False,
            "model": model_id,
            "latency_ms": latency,
            "message": f"連線測試失敗: {str(e)}"
        }

@app.get("/api/lot_types")
async def get_lot_types():
    """取得支援的籤詩系統列表與說明"""
    return {
        "success": True,
        "systems": list(LOT_SYSTEMS.values())
    }

@app.get("/api/lots")
async def get_lots_list(lot_type: Optional[str] = None):
    """取得指定籤系或全部籤詩清單 (包含籤號、籤名、吉凶、詩句、典故)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if lot_type:
                cursor.execute("""
                    SELECT id, lot_type, lot_type_name, lot_number, lot_name, grade, content, story 
                    FROM lots WHERE lot_type = ? ORDER BY lot_number
                """, (lot_type,))
            else:
                cursor.execute("""
                    SELECT id, lot_type, lot_type_name, lot_number, lot_name, grade, content, story 
                    FROM lots ORDER BY lot_type, lot_number
                """)
            rows = cursor.fetchall()
            return {
                "success": True,
                "lots": [dict(r) for r in rows]
            }
    except Exception as e:
        logger.error(f"Error fetching lots list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/daily_lot")
async def get_daily_lot(
    lot_type: str = "60_jiazi",
    date_str: Optional[str] = None,
    user_id: Optional[str] = None,
    redraw_index: int = 0
):
    """取得當日專屬靈籤 (支援依日期、使用者隨機種子與重抽次數生成個人專屬靈籤與心理靜思賦權指引)"""
    import hashlib
    from datetime import date
    if not date_str:
        date_str = date.today().isoformat()
    
    if lot_type not in LOT_SYSTEMS:
        lot_type = "60_jiazi"
        
    system_info = LOT_SYSTEMS[lot_type]
    max_lots = system_info["max_lots"]
    
    # 構建專屬 Hash 種子：結合日期、籤系、使用者ID(如有)、重抽序號
    seed_parts = [f"daily_{date_str}_{lot_type}"]
    if user_id:
        seed_parts.append(str(user_id).strip())
    if redraw_index > 0:
        seed_parts.append(f"redraw_{redraw_index}")
    seed_str = "_".join(seed_parts)

    hash_int = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    daily_lot_number = (hash_int % max_lots) + 1
    
    lot = fetch_lot_from_db(lot_type, daily_lot_number)
    
    # 豐富的每日心理賦權微啟發 (Zen Affirmations)
    zen_affirmations = [
        "不為模糊不清的未來擔憂，只為清清楚楚的現在努力。安住當下，心無罣礙。",
        "事緩則圓，給思緒留一點沉澱的空間，迷霧散去，答案自會清澈浮現。",
        "外在的境遇是映照內心的鏡子；守住自己的節奏與正念，境隨心轉。",
        "每一次的停頓與等待，都是生命在為下一段躍進蓄積深厚能量。",
        "接納客觀局勢的未知，把注意力收回到今天能掌控的一小步行動上。",
        "以溫和而堅定的態度對待自己與他人，沉著從容，自帶光芒。",
        "行到水窮處，坐看雲起時；轉念即是轉機，順應機緣方得自若。",
        "人生沒有白走的路，每一步腳印都在替未來的開花結果鋪路。",
        "當你停止內耗、專注於此刻能做的小事，宇宙便會開始為你調度資源。",
        "順境時心懷謙卑與感恩，逆境時修養定力與智慧，心中自有一片晴空。",
        "所有的焦慮皆來自對未發生的預設；深呼吸，相信自己內在的韌性。",
        "萬事俱備不如心念篤定；帶著善意與信心出發，機緣自會在途中相遇。"
    ]
    daily_focus = zen_affirmations[hash_int % len(zen_affirmations)]

    return {
        "success": True,
        "date": date_str,
        "lot_type": lot_type,
        "lot_type_name": system_info["name"],
        "lot_number": daily_lot_number,
        "user_id": user_id,
        "redraw_index": redraw_index,
        "daily_focus": daily_focus,
        "lot": lot
    }

@app.post("/api/interpret", response_model=InterpretResponse)
async def interpret_lot(req: InterpretRequest):
    """
    接收籤系、抽籤號碼與使用者問題，查詢 SQLite 籤詩資料庫，進行 AI 心理學賦權解籤並存檔。
    """
    effective_model = req.model or current_runtime_model
    logger.info(f"Received interpretation request - Model: {effective_model}, System: {req.lot_type}, Lot: {req.lot_number}, Question: {req.user_question}")
    
    # 1. 查詢籤詩資料
    lot = fetch_lot_from_db(req.lot_type, req.lot_number)
    
    # 2. 呼叫 AI 進行結構化解析
    analysis, model_used = generate_ai_interpretation(lot, req.user_question, effective_model)
    
    # 3. 儲存紀錄至 SQLite 資料庫
    draw_id = save_draw_record(lot, req.user_question, analysis)
    
    return InterpretResponse(
        success=True,
        lot=lot,
        analysis=analysis,
        model_used=model_used,
        draw_id=draw_id
    )

@app.get("/api/health")
async def health_check():
    """健康檢查端點"""
    db_ok = False
    system_counts = {}
    total_count = 0
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT lot_type, COUNT(*) FROM lots GROUP BY lot_type")
            rows = cursor.fetchall()
            for r in rows:
                system_counts[r[0]] = r[1]
                total_count += r[1]
            db_ok = True
    except Exception:
        db_ok = False

    client, active_model = get_llm_client(current_runtime_model)
    return {
        "status": "healthy",
        "database_type": "sqlite",
        "database_path": DB_PATH,
        "database_connected": db_ok,
        "total_lots_seeded": total_count,
        "system_lots_breakdown": system_counts,
        "llm_configured": client is not None,
        "active_model": current_runtime_model
    }

# ==============================================================================
# 掛載靜態網頁 (Frontend)
# ==============================================================================
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
