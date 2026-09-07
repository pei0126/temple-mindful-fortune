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
    direct_verdict: str = Field(description="【直白定調/是非解答】一句話超直白定調（如是非題直接給答案與機會機率，接地氣不繞圈子）")
    poem_interpretation: str = Field(description="【籤詩大白話】把古文籤詩翻成現代年輕人一秒看懂的大白話")
    story_inspiration: str = Field(description="【典故白話講】用現代白話說典故，講出核心道理")
    situation_analysis: str = Field(description="【針對你這件事的剖析】直球切入使用者具體問的事情，給出實質分析")
    actions: ActionGuide = Field(description="具體行動指南 (超具體的實操步驟 Do's & Don'ts)")
    encouragement: str = Field(description="【為你打氣】像好友一樣親切、熱血、給力的打氣金句")

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

def build_smart_fallback_analysis(lot: LotInfo, user_question: str) -> StructuredAnalysis:
    """生成直白、接地氣、針對提問的備用結構化解籤（無 API 或連線失敗時的優質備援）"""
    q = user_question.lower()
    is_positive = any(g in lot.grade for g in ["大吉", "上吉", "中吉", "上上", "吉", "大安"])
    story_short = lot.story.split("。")[0] if lot.story else lot.lot_name
    
    # 判斷問題類型
    if any(k in q for k in ["搶", "票", "門票", "演唱會", "買到", "bigbang"]):
        if is_positive:
            verdict = f"【直白解答】：勝率極高，全力爭取！此籤為「{lot.grade}」，氣場正旺，把握時機果斷出手即可。"
            sit = f"針對你想問的「{user_question}」：此籤象徵時機與狀態俱備，與其焦慮自我懷疑，不如把準備工作做足，勝算都在你這邊。"
            dos = [
                f"【核心策略】依循「{lot.lot_name}」吉兆，鎖定目標第一時間果斷下定決心，不猶豫猶疑。",
                "【實操準備】提前確認相關帳號設定與應變管道，確保關鍵時刻操作流程一氣呵成。",
                f"【心態轉化】借鑒典故【{story_short}】的勝勢底氣，心態篤定，好運自然相隨。"
            ]
            donts = [
                "【忌猶豫】開跑當下千萬別三心二意猶豫挑剔，能先拿下核心目標就是最大贏家。",
                "【忌慌亂】切勿因周遭緊張氛圍自亂陣腳，穩住呼吸操作才能發揮最佳水準。",
                "【忌偏門】運勢已在正道，切忌急躁尋求不明來源或風險代辦，避免得不償失。"
            ]
        else:
            verdict = f"【直白解答】：機率偏低，建議平常心看待！此籤為「{lot.grade}」，提醒莫過度執著於單一結果。"
            sit = f"針對你想問的「{user_question}」：籤詩暗示客觀競爭激烈或機緣未到，過度強求容易身心俱疲，放寬心胸方能撥雲見日。"
            dos = [
                f"【核心心法】體悟典故【{story_short}】之隨緣智慧，設定理性停損線，不讓這件事打亂日常生活。",
                "【備案規劃】事先想好即使結果不如預期的替代方案（如與好友聚餐慶祝或安排其他娛樂），轉移焦點。",
                "【從容面對】抱持「得之我幸、失之我命」的豁達心態，反而能看清更多生活中的美好可能。"
            ]
            donts = [
                "【忌強求執念】切忌將這場爭取視為唯一快樂來源，不要讓焦慮影響工作與作息。",
                "【忌衝動追高】若第一時間未能如願，千萬不要衝動花費超額代價或向不明第三方涉險購買。",
                "【忌自我懷疑】機率與運氣本是客觀常態，沒拿到純屬機緣，切莫歸咎於個人能力而陷入內耗。"
            ]
    elif any(k in q for k in ["轉職", "工作", "換工作", "離職", "跳槽", "面試", "升遷", "創業"]):
        if is_positive:
            verdict = f"【直白解答】：可以衝！這支籤是「{lot.grade}」，代表轉職或推進的好時機，新的機會將為你帶來突破！"
            sit = f"針對你詢問的工作問題「{user_question}」：局勢正在好轉，你的能力已經累積足夠，該展現自信抓住機會。"
            dos = [
                f"【核心出擊】結合「{lot.lot_name}」破局之勢，梳理過往核心成果與解決問題的實例，大方爭取。",
                "【人脈借力】主動向產業前輩或信任夥伴打聽市場真實情報，掌握第一手風向。",
                f"【心態建設】學習典故【{story_short}】的主動果斷，拋開冒牌者症候群，相信自己值得更好。"
            ]
            donts = [
                "【忌裹足不前】不要自我懷疑或因害怕跨出舒適圈而錯過推進視窗。",
                "【忌貿然裸辭】未在實質合約確定前，仍需守好現有職責，確保安全著陸。",
                "【忌被畫大餅】切莫被浮誇的承諾蒙蔽，務必檢視實際制度與工作環境。"
            ]
        else:
            verdict = f"【直白解答】：建議先穩住，暫時不要衝動換！籤詩評等為「{lot.grade}」，提示目前環境變數多，先蓄積實力為上策。"
            sit = f"針對工作問題「{user_question}」：當前外部局勢尚不明朗，急著跳槽可能會跳入另一個坑，建議騎驢找馬、先充實自己。"
            dos = [
                f"【深耕本分】以【{story_short}】為鑑，在現有崗位上把能學的技能與人脈資產拿到手。",
                "【暗中佈局】趁外部風浪多時沉下心打磨核心實力，等待局勢反轉成熟的良機。",
                "【多方求證】多方客觀調查目標領域的真實穩定度，避免因片面資訊做出誤判。"
            ]
            donts = [
                "【忌情緒用事】不要因為一時受氣或疲憊就衝動提離職。",
                "【忌盲目跟風】不要看到別人跳槽就跟著浮躁，每個人承擔風險的資本不同。",
                "【忌忽視積累】不要輕易拋棄在目前環境中辛苦累積的信任資產。"
            ]
    else:
        # 通用是非/決策題
        if is_positive:
            verdict = f"【直白解答】：答案偏向「是／正面肯定」！這是一張「{lot.grade}」的好籤，局勢向好，順勢而為！"
            sit = f"針對你所問的「{user_question}」：阻礙正逐步散去，轉機就在眼前，只要照著核心目標穩步推進即可。"
            dos = [
                f"【順應吉時】以「{lot.lot_name}」為指引，保持信心與執行力，把想法具體落實為今日行動。",
                "【積極溝通】主動爭取機會，及時向身邊值得信賴的夥伴尋求協同與反饋。",
                f"【正向放大】借【{story_short}】之力量，專注於能創造價值的環節，擴大成果。"
            ]
            donts = [
                "【忌過度內耗】不要前怕狼後怕虎，過度糾結未發生的細節反而消耗行動力。",
                "【忌聽信雜音】不要輕易受旁人未經深思的消極評語動搖本心。",
                "【忌半途鬆懈】好籤需要踏實落地，切莫在最後推進關頭掉以輕心。"
            ]
        else:
            verdict = f"【直白解答】：建議「先緩緩／謹慎評估」！這張籤評等為「{lot.grade}」，提示目前變數較多，先停看聽比硬衝更安全。"
            sit = f"針對你所問的「{user_question}」：眼前可能有些隱藏細節還沒看清，先冷靜梳理，不要急著在此刻下不可逆的重大決定。"
            dos = [
                f"【沉澱梳理】汲取典故【{story_short}】之啟示，收集客觀事證，把利弊清單具體化分析。",
                "【留有餘地】給自己一段冷靜沉澱期，傾聽不同角度的客觀建言，做好多重避險準備。",
                "【守住節奏】把重心放回自身可控的日常事務上，靜待時機成熟明朗。"
            ]
            donts = [
                "【忌焦躁攤牌】切忌在情緒激動或焦慮狀態下做關鍵決定，以免事後懊悔。",
                "【忌急於求成】切莫跳過必要的評估步驟而強行逆勢推進。",
                "【忌忽視直覺警訊】不要強行合理化心中的疑慮，感覺不對勁時先停步往往最安全。"
            ]

    clean_content = lot.content.replace("\n", " ")
    poem_interp = f"這首籤詩（{lot.lot_name}・{lot.grade}）原文是「{clean_content}」。用現代白話說就是：『好時機即將到來，先前的準備與努力都在打底！只要你心意堅定、做好該做的準備，時間到了自然順理成章拿下！』"
    story_insp = f"典故【{lot.story}】用白話講：就像高手出招，關鍵在於『快、準、穩』！不要猶豫不決，機會出現的瞬間全力出手就是致勝關鍵。"
    encouragement = "別焦慮！神明已經給出方向，接下來就看你的行動了。相信自己的直覺與準備，放手去衝，好事自然發生！"

    return StructuredAnalysis(
        direct_verdict=verdict,
        poem_interpretation=poem_interp,
        story_inspiration=story_insp,
        situation_analysis=sit,
        actions=ActionGuide(dos=dos, donts=donts),
        encouragement=encouragement
    )

def generate_ai_interpretation(lot: LotInfo, user_question: str, requested_model: Optional[str] = None) -> tuple[StructuredAnalysis, str]:
    """呼叫指定 LLM (Gemini 3.1 / GPT-4o 等) 進行超直白、接地氣的現代青年結構化解籤"""
    target_model = requested_model or current_runtime_model
    client, model_id = get_llm_client(target_model)
    
    if not client:
        # Mock Response when API key is missing
        logger.info("Using Fallback Mock Interpretation Engine.")
        analysis = build_smart_fallback_analysis(lot, user_question)
        return analysis, "內建直白模擬引擎 (Fallback)"

    system_prompt = """你是一位說話風格「超直白、接地氣、懂年輕人」的現代宮廟智慧生活軍師與解籤大師。
【核心風格與解籤原則】：
1. 【直球對決・拒絕太極】：
   - 使用者提問（不論是是非題、抉擇題或運勢勝算），必須在 direct_verdict 第一時間給出乾脆清晰的答案、勝率或方向定調（例如：「勝率極高，全力去衝！」、「機率渺茫，莫強求！」、「先按兵不動，等局勢明朗」）。
2. 【全繁體中文・現代白話通俗易懂】：
   - 嚴禁使用生硬晦澀的教科書術語或打官腔（嚴禁出現：認知再架構、自我能動性、非黑即白思維、情緒沉澱、心理投射等假道學名詞）。
   - 將古文籤詩和歷史典故轉化為當代生活、職場、人際或具體情境的生動比喻，字字入肉、講人話。
3. 【嚴禁樣板套話・破除刻板常識 (Anti-Cliche & High Diversity)】：
   - ⚠️【極重要】絕不可給出機械化、隨處可見的網路空泛常識（例如：切勿每次搶票都只會提『檢查 Wi-Fi/5G、提早登入、不要按 F5、不要買黃牛』；切勿每次轉職都只會提『更新履歷、騎驢找馬』；切勿每次感情都只會提『多溝通、約出門喝咖啡』）。
   - 每一條具體實操 (Do's) 與避坑雷區 (Don'ts) 必須【100% 依據本次抽到的「籤詩詩意」＋「歷史典故核心哲理」＋「吉凶評等（吉/平/凶）」】與求籤者的具體問題深度融合！
4. 【根據籤詩意境客製化策略】：
   - 若為「隨緣放下、莫強求型」（如莊子鼓盆、陶淵明歸隱）：實操聚焦於「理性設限、設立停損點或預算上限、規劃落空時的愉悅轉念替代備案、把精力收回真實生活」；雷區聚焦於「切忌執念太深過度追高、切忌讓單一事件打亂生活重心與工作節奏」。
   - 若為「果斷出擊、勢在必得型」（如關公斬顏良、薛仁貴破敵）：實操聚焦於「集中優勢資源、快狠準出手、排除外界雜音干擾、專注瞬間爆發」；雷區聚焦於「切忌優柔寡斷、切忌瞻前顧後錯失良機」。
   - 若為「守候時機、蓄積底氣型」（如太公釣魚、蘇武牧羊）：實操聚焦於「靜觀其變、摸清環境規則、厚植底氣、等待反轉」；雷區聚焦於「切忌逆勢硬幹、切忌心浮氣躁急於求成」。
   - 若為「借力使力、合縱連橫型」（如管鮑分金、桃園結義）：實操聚焦於「善用外部資源、凝聚可靠夥伴神助攻、建立共識」；雷區聚焦於「切忌盲目個人英雄主義、切忌猜忌內耗」。
5. 【熱血真摯與心理賦權】：
   - 像一個說真話、講義氣、站在使用者這邊的酷前輩或老廟祝，直白犀利卻充滿溫度，讓人看完豁然開朗。
6. 請嚴格以繁體中文輸出符合指定 JSON Schema 的結構化格式。
"""

    user_prompt = f"""
【求籤者提問】：
{user_question}

【抽得籤詩詳細資訊】：
- 籤詩系統：{lot.lot_type_name}
- 籤號：{lot.lot_name} (第 {lot.lot_number} 籤)
- 評等吉凶：{lot.grade}
- 籤詩原文：
{lot.content}
- 歷史典故：
{lot.story}

【解讀與輸出指示】：
請完全吸收這首籤詩的詩意哲理與典故歷史，針對求籤者提出的具體問題「{user_question}」，給出獨一無二、絕無複製貼上感的現代直白結構化指引。

請嚴格輸出為以下 JSON 格式：
{{
  "direct_verdict": "【直白解答/是非定調】針對使用者問題直接定調勝算與走向（不打太極、直球切入），並結合此籤吉凶給予一針見血的結論。",
  "poem_interpretation": "【籤詩大白話】把籤詩原文用生動、生活化的大白話翻譯，點出詩中最關鍵的一句話對當前問題的指引。",
  "story_inspiration": "【典故白話講】用現代生活比喻深入淺出講述歷史典故，點出神明想透過這個故事傳遞的心態與謀略，講人話。",
  "situation_analysis": "【針對你這件事的直白剖析】將籤意與「{user_question}」緊密連結，分析當前形勢的利弊盲點與突破口。",
  "actions": {{
    "dos": [
      "【核心策略】深層結合本籤詩意與典故哲理，針對當前問題提出的第一步具體實操破局法（請展現本籤獨特觀點，拒絕空泛常識）",
      "【執行關鍵】結合當前情境，給出具體且跳脫平庸建議的落地手段或關鍵準備",
      "【心態轉化與備案】依據本籤指引設計的心理調適、停損機制或備選替代方案"
    ],
    "donts": [
      "【心態盲點】本籤最嚴厲警告的心態盲區或執念陷阱（緊扣籤詩哲理）",
      "【致命地雷】針對這件事最容易踩中、會讓局勢惡化的衝動或不當行為",
      "【無效消耗】該立即停止的自我懷疑、外部雜音干擾或過度執著"
    ]
  }},
  "encouragement": "【為你打氣】像好友或講義氣的廟祝軍師給予的熱血、溫暖且富有力量的打氣話語"
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
            temperature=0.8,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        # 若 LLM 遺漏 direct_verdict，自動補全
        if "direct_verdict" not in parsed or not parsed["direct_verdict"]:
            parsed["direct_verdict"] = f"【直白定調】：這是一張「{lot.grade}」籤，針對你問的「{user_question}」，請依循籤意智慧穩步應對！"
            
        return StructuredAnalysis(**parsed), model_id
    except Exception as e:
        logger.error(f"Error calling LLM ({model_id}): {e}")
        # 若大模型發生異常，回退為直白模擬解讀
        fallback_analysis = build_smart_fallback_analysis(lot, user_question)
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

    # 0. 依籤詩系統動態驗證 lot_number 上限（避免 60_jiazi 接受 61~100 而靜默 fallback）
    system_info = LOT_SYSTEMS.get(req.lot_type)
    if system_info:
        max_lots = system_info["max_lots"]
        if req.lot_number > max_lots:
            raise HTTPException(
                status_code=422,
                detail=f"【籤號超出範圍】{system_info['name']} 共有 {max_lots} 首籤，請輸入 1 ~ {max_lots} 之間的籤號。"
            )

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
