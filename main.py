import os
import json
import time
import logging
import sqlite3
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Header, Request
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

            # 建立 daily_lot_draws 表 (用於 IP 與裝置鎖定每日一籤，一天限抽一次)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_lot_draws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draw_date TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    lot_type TEXT NOT NULL,
                    lot_number INTEGER NOT NULL,
                    daily_focus TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 建立索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_lots_type_number ON lots(lot_type, lot_number);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_draws_created_at ON user_draws(created_at DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_draws_lookup ON daily_lot_draws(draw_date, ip_address, device_id);")
            
            # 檢查並載入籤詩種子資料
            cursor.execute("SELECT COUNT(*) FROM lots")
            count = cursor.fetchone()[0]
            
            if count < 360:
                json_path = os.path.join(os.path.dirname(__file__), "data", "lots_all.json")
                if os.path.exists(json_path):
                    logger.info("Loading 360 lots from data/lots_all.json into SQLite...")
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
                    logger.info("Successfully seeded 360 lots into SQLite database.")
        
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
    language: Optional[str] = Field(default="zh-TW", description="解籤輸出語言 (zh-TW: 繁體中文, en: English, ja: 日本語, ko: 한국어)")

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

def build_smart_fallback_analysis(lot: LotInfo, user_question: str, language: str = "zh-TW") -> StructuredAnalysis:
    """生成直白、接地氣、針對提問的備用結構化解籤（支援繁中/英/日/韓多語系備援）"""
    lang = (language or "zh-TW").lower()
    is_positive = any(g in lot.grade for g in ["大吉", "上吉", "中吉", "上上", "吉", "大安"])
    story_short = lot.story.split("。")[0] if lot.story else lot.lot_name

    if "en" in lang:
        if is_positive:
            verdict = f"【Direct Verdict】: Highly favorable (Yes / Go for it!). This lot is graded '{lot.grade}'. Momentum is on your side—act decisively!"
            sit = f"Regarding your question '{user_question}': Conditions are aligning well. Instead of overthinking, focus on solid execution."
            dos = [
                f"【Core Strategy】Align with the auspicious omen of '{lot.lot_name}' and take the initiative without hesitation.",
                "【Preparation】Double-check your key tools and channels in advance so you can execute smoothly at critical moments.",
                f"【Mindset】Draw confidence from the historic lesson of '{story_short}'; staying grounded brings luck."
            ]
            donts = [
                "【Avoid Hesitation】Do not second-guess yourself at the starting line; seizing the moment is key.",
                "【Avoid Panic】Stay calm and ignore surrounding noise to perform at your best.",
                "【Avoid Shortcuts】You are on the right path—avoid risky or unverified short cuts."
            ]
            encouragement = "Have faith in your preparation. The signs are clear—step forward boldly and good things will follow!"
        else:
            verdict = f"【Direct Verdict】: Exercise patience (Proceed with caution). This lot is graded '{lot.grade}'. Do not force an immediate outcome."
            sit = f"Regarding your question '{user_question}': External conditions are fluctuating. Steady preparation beats rushed action."
            dos = [
                f"【Patience】Reflect on the wisdom of '{story_short}'; set rational boundaries and protect your daily peace of mind.",
                "【Plan B】Prepare secondary options so you remain adaptable regardless of immediate results.",
                "【Composure】Embrace a calm attitude; clarity comes when you let the dust settle."
            ]
            donts = [
                "【Avoid Fixation】Do not make this single matter the sole measure of your happiness.",
                "【Avoid Impulsive Bets】Do not overcommit resources when the timing is not yet ripe.",
                "【Avoid Self-Doubt】Temporary delays are natural; avoid internal exhaustion."
            ]
            encouragement = "Take a deep breath. Slowing down today protects your long-term success. Trust the unfolding journey."
        clean_content = lot.content.replace("\n", " ")
        poem_interp = f"Poem ({lot.lot_name} / {lot.grade}): '{clean_content}'. In plain words: Steady dedication prepares the soil; when the right time arrives, things flourish naturally."
        story_insp = f"Story Wisdom ({lot.story}): Success belongs to those who observe carefully and strike with calm precision."

    elif "ja" in lang:
        if is_positive:
            verdict = f"【率直な判定】：大いに有望（進むべし・吉）！おみくじは「{lot.grade}」です。運気は追い風、迷わず果敢に行動しましょう。"
            sit = f"ご相談の「{user_question}」について：機は熟しつつあります。自己疑念を捨て、着実な一歩を踏み出すことで勝機を掴めます。"
            dos = [
                f"【基本方針】「{lot.lot_name}」の吉兆に乗り、目標を定めたら躊躇なく行動に移すこと。",
                "【具体的準備】重要な連絡や環境設定を事前に整え、好機を逃さない態勢を作ること。",
                f"【心の持ち方】故事「{story_short}」の勢いに学び、堂々とした姿勢で幸運を引き寄せること。"
            ]
            donts = [
                "【優柔不断は禁物】チャンスが来たら迷いすぎず、本質を掴むことに集中してください。",
                "【焦りは禁物】周囲の雰囲気に流されず、冷静な判断を保つこと。",
                "【無理な抜け道は避ける】正攻法で進むことが最大の近道です。"
            ]
            encouragement = "あなたの努力はしっかり実を結びます。自分を信じて前向きに進んでください！"
        else:
            verdict = f"【率直な判定】：今は静観・慎重に（急がず機を待つべし）。おみくじは「{lot.grade}」です。無理な前進は控えましょう。"
            sit = f"ご相談の「{user_question}」について：周囲の状況が流動的です。焦って決断するより、地力を蓄える時期です。"
            dos = [
                f"【本質を見極める】故事「{story_short}」の教えを胸に、冷静に状況を整理し無理な執着を手放すこと。",
                "【代替案の用意】万一に備えたプランBを整え、心の余裕を確保すること。",
                "【基礎固め】日常のルーティンを大切にし、時が満ちるのを待つこと。"
            ]
            donts = [
                "【過度な執着】一つの結果に囚われて心身を消耗しないこと。",
                "【感情的な衝動買い・契約】焦って不透明な選択肢に飛びつかないこと。",
                "【過度な自己否定】タイミングの問題です。自分を責めず充電に充ててください。"
            ]
            encouragement = "焦る必要はありません。今は力を蓄える大切な時間です。心が整えば道は自ずと拓けます。"
        clean_content = lot.content.replace("\n", " ")
        poem_interp = f"神籤の言葉（{lot.lot_name}・{lot.grade}）:「{clean_content}」。現代語訳：『雲が晴れて光が射すように、誠実に積み重ねた努力がやがて明るい未来を照らします』"
        story_insp = f"歴史故事（{lot.story}）：『急がば回れ、肝心な局面で冷静さを保つ者が真の果実を得る』"

    elif "ko" in lang:
        if is_positive:
            verdict = f"【명쾌한 결론】：승률 매우 높음 (적극 추진 추천)! 이번 점괘는 '{lot.grade}'입니다. 기운이 좋으니 망설이지 말고 결단하세요."
            sit = f"질문하신 '{user_question}'에 대해: 타이밍과 여건이 갖춰지고 있습니다. 불안해하기보다 준비한 실력을 발휘할 때입니다."
            dos = [
                f"【핵심 전략】'{lot.lot_name}'의 길조를 따라 목표를 확정하고 과감하게 실행하세요.",
                "【실전 준비】중요한 계정 및 일정을 사전 점검하여 결정적 순간에 막힘없이 대처하세요.",
                f"【마인드셋】'{story_short}'의 고사처럼 흔들림 없는 확신을 가지면 행운이 따릅니다."
            ]
            donts = [
                "【망설임 금지】기회가 왔을 때 지나치게 재거나 망설이지 마세요.",
                "【조급함 금지】주변 분위기에 휩쓸려 페이스를 잃지 마세요.",
                "【위험한 편법 지양】정공법으로 나아가는 것이 가장 확실한 지름길입니다."
            ]
            encouragement = "당신의 노력이 빛을 발할 순간입니다. 스스로를 믿고 당당하게 전진하세요!"
        else:
            verdict = f"【명쾌한 결론】：속도 조절 필요 (신중한 관망 추천)! 이번 점괘는 '{lot.grade}'입니다. 무리하게 밀어붙이지 마세요."
            sit = f"질문하신 '{user_question}'에 대해: 외부 환경의 변수가 많습니다. 지금은 성급한 결정보다 내실을 다질 때입니다."
            dos = [
                f"【지혜로운 대처】'{story_short}'의 교훈처럼 마음의 여유를 두고 감정적 소모를 줄이세요.",
                "【대체 플랜 마련】원하는 결과가 즉시 나오지 않더라도 대안을 준비해 두세요.",
                "【마인드 정돈】통제할 수 있는 일상에 집중하며 흐름이 좋아질 때를 기다리세요."
            ]
            donts = [
                "【과도한 집착】하나의 결과에 지나치게 매달려 일상을 망치지 마세요.",
                "【충동적 결정】불안감 때문에 무리한 지출이나 섣부른 약속을 하지 마세요.",
                "【자책감 지양】타이밍의 문제일 뿐입니다. 스스로를 탓하며 에너지를 낭비하지 마세요."
            ]
            encouragement = "잠시 숨을 고르세요. 지금의 멈춤은 더 큰 도약을 위한 준비 과정입니다."
        clean_content = lot.content.replace("\n", " ")
        poem_interp = f"점괘 원문 ({lot.lot_name} / {lot.grade}): '{clean_content}'. 현대적 풀이: '구름이 걷히고 햇살이 비추듯, 바른 마음으로 준비한 자에게 반드시 좋은 결실이 찾아옵니다.'"
        story_insp = f"역사 고사 ({lot.story}): '흐름을 관찰하며 실력을 비축할 때 진정한 승리를 거둘 수 있습니다.'"

    else:
        # Default: 繁體中文 (zh-TW)
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
            encouragement = "別焦慮！神明已經給出方向，接下來就看你的行動了。相信自己的直覺與準備，放手去衝，好事自然發生！"
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
            encouragement = "深呼吸，放輕鬆！暫時的停頓不是失敗，而是替下一段更好的相遇鋪路。先愛護好自己！"
        clean_content = lot.content.replace("\n", " ")
        poem_interp = f"這首籤詩（{lot.lot_name}・{lot.grade}）原文是「{clean_content}」。用現代白話說就是：『好時機即將到來，先前的準備與努力都在打底！只要你心意堅定、做好該做的準備，時間到了自然順理成章拿下！』"
        story_insp = f"典故【{lot.story}】用白話講：就像高手出招，關鍵在於『快、準、穩』！不要猶豫不決，機會出現的瞬間全力出手就是致勝關鍵。"

    return StructuredAnalysis(
        direct_verdict=verdict,
        poem_interpretation=poem_interp,
        story_inspiration=story_insp,
        situation_analysis=sit,
        actions=ActionGuide(dos=dos, donts=donts),
        encouragement=encouragement
    )

def generate_ai_interpretation(lot: LotInfo, user_question: str, requested_model: Optional[str] = None, language: str = "zh-TW") -> tuple[StructuredAnalysis, str]:
    """呼叫指定 LLM (Gemini 3.1 / GPT-4o 等) 進行超直白、接地氣的現代青年結構化解籤 (支援繁中/英/日/韓)"""
    target_model = requested_model or current_runtime_model
    client, model_id = get_llm_client(target_model)
    lang = (language or "zh-TW").lower()
    
    if not client:
        # Mock Response when API key is missing
        logger.info("Using Fallback Mock Interpretation Engine.")
        analysis = build_smart_fallback_analysis(lot, user_question, lang)
        return analysis, "內建直白模擬引擎 (Fallback)"

    # 針對語言設定專屬指導
    if "en" in lang:
        lang_instruction = """
【Language Instruction: ENGLISH】:
- Output ALL JSON field values strictly in clear, natural, modern, and empathetic ENGLISH.
- Translate ancient Chinese poem lines and historic lore into vivid, relatable English metaphors.
- Give crisp direct verdicts, practical Do's & Don'ts, and a warm, uplifting encouragement.
"""
    elif "ja" in lang:
        lang_instruction = """
【Language Instruction: JAPANESE (日本語)】:
- Output ALL JSON field values strictly in natural, empathetic, and culturally nuanced JAPANESE (日本語).
- 古文の籤詩や歴史故事を、現代の若者にも響く分かりやすい日本語（現代語訳・生きた比喩）で解説してください。
- 曖昧さを排した明確な方向性（是・非・勝率）、実践的なアドバイス（Do's & Don'ts）、温かい励ましの言葉を出力してください。
"""
    elif "ko" in lang:
        lang_instruction = """
【Language Instruction: KOREAN (한국어)】:
- Output ALL JSON field values strictly in natural, relatable, and encouraging KOREAN (한국어).
- 고대 점괘 시문과 역사 고사를 현대 청년들이 바로 이해할 수 있는 생생한 한국어로 해설하세요.
- 명쾌한 직설적 결론, 구체적 실천 지침 (Do's & Don'ts), 따뜻하고 힘이 나는 응원 문구를 출력하세요.
"""
    else:
        lang_instruction = """
【語言指示：台灣繁體中文 (Traditional Chinese)】:
- 所有 JSON 欄位內容嚴格以繁體中文輸出。風格超直白、接地氣、懂年輕人、拒絕太極。
- 將古文籤詩和歷史典故轉化為當代生活、職場、人際的生動比喻，字字入肉、講人話。
"""

    system_prompt = f"""你是一位說話風格「超直白、接地氣、懂年輕人」的現代宮廟智慧生活軍師與解籤大師。
【核心風格與解籤原則】：
1. 【直球對決・拒絕太極】：
   - 使用者提問（不論是是非題、抉擇題或運勢勝算），必須在 direct_verdict 第一時間給出乾脆清晰的答案、勝率或方向定調。
2. 【生動白話通俗易懂】：
   - 嚴禁使用生硬晦澀的教科書術語或假道學名詞。
3. 【嚴禁樣板套話・破除刻板常識 (Anti-Cliche & High Diversity)】：
   - 每一條具體實操 (Do's) 與避坑雷區 (Don'ts) 必須 100% 依據本次抽到的「籤詩詩意」＋「歷史典故核心哲理」＋「吉凶評等」與求籤者的具體問題深度融合！
4. 【熱血真摯與心理賦權】：
   - 像一個說真話、講義氣、站在使用者這邊的酷前輩或老廟祝，直白犀利卻充滿溫度。
{lang_instruction}
"""

    user_prompt = f"""
【求籤者提問 / User Question】：
{user_question}

【抽得籤詩詳細資訊 / Fortune Details】：
- 籤詩系統：{lot.lot_type_name}
- 籤號：{lot.lot_name} (第 {lot.lot_number} 籤)
- 評等吉凶：{lot.grade}
- 籤詩原文：
{lot.content}
- 歷史典故：
{lot.story}

【解讀與輸出指示 / Output Schema in Target Language】：
請嚴格輸出為以下 JSON 格式（所有欄位內容依指定語言輸出）：
{{
  "direct_verdict": "Direct concise verdict on user question and outcome probability",
  "poem_interpretation": "Plain modern translation of the poem highlighting the core message",
  "story_inspiration": "Modern life metaphor explaining the historical lore and strategic lesson",
  "situation_analysis": "In-depth analysis directly tailored to the user's specific question",
  "actions": {{
    "dos": [
      "Concrete step 1 based on this lot's unique philosophical insight",
      "Concrete step 2 for execution and key preparation",
      "Mindset adaptation and backup plan"
    ],
    "donts": [
      "Crucial pitfall/blindspot warned by this lot",
      "Dangerous impulsive behavior to strictly avoid",
      "Ineffective emotional overthinking to stop immediately"
    ]
  }},
  "encouragement": "Warm, empowering and punchy motivational closing message"
}}
"""

    try:
        logger.info(f"Invoking AI model: {model_id} (Lang: {lang}) for user question...")
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
        fallback_analysis = build_smart_fallback_analysis(lot, user_question, lang)
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
    request: Request,
    lot_type: str = "60_jiazi",
    date_str: Optional[str] = None,
    device_id: Optional[str] = None,
    language: str = "zh-TW"
):
    """
    取得當日專屬靈籤（支援 IP 與裝置識別碼雙重綁定，一天嚴格限抽一次）
    """
    import hashlib
    from datetime import date
    if not date_str:
        date_str = date.today().isoformat()
    
    if lot_type not in LOT_SYSTEMS:
        lot_type = "60_jiazi"
        
    system_info = LOT_SYSTEMS[lot_type]
    max_lots = system_info["max_lots"]

    # 提取 Client IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    elif request.client and request.client.host:
        client_ip = request.client.host
    else:
        client_ip = "127.0.0.1"

    eff_device_id = (device_id or "").strip() or "device_unknown"

    # 多語系每日心靈賦權微啟發 (Zen Affirmations)
    lang = (language or "zh-TW").lower()
    if "en" in lang:
        affirmations = [
            "Do not worry about the uncertain future; focus on the clear present. Stay centered in this moment.",
            "Patience brings clarity. Give your thoughts space to settle, and the answer will naturally appear.",
            "External circumstances reflect the inner mind; maintain your rhythm and inner peace.",
            "Every pause and waiting period stores profound energy for your next breakthrough.",
            "Accept uncertainty; refocus your energy on the single small step you can take today.",
            "Treat yourself and others with gentle firmness; calm confidence radiates its own light.",
            "Where waters end, clouds arise. A shift in perspective turns obstacles into serendipity.",
            "No effort is ever wasted; every footprint paves the way for tomorrow's fruition.",
            "When you stop overthinking and focus on what is before you, opportunities begin to align.",
            "Practice gratitude in ease, cultivate wisdom in challenge; keep your inner sky clear."
        ]
    elif "ja" in lang:
        affirmations = [
            "不透明な未来を案ずるより、今できる目の前の一歩に集中しましょう。心穏やかに。",
            "急いては事を仕損じる。心にゆとりを持てば、霧が晴れるように答えが見えてきます。",
            "外の世界は心を映す鏡。自分のペースと誠実さを保てば、運気は必ず好転します。",
            "立ち止まる時間は決して無駄ではありません。次の飛躍へのエネルギーを蓄えています。",
            "先の見えない不安を手放し、今日コントロールできる小さな行動に意識を向けましょう。",
            "自分にも他者にも優しく、芯を強く。落ち着いた佇まいは自ずと幸運を引き寄せます。",
            "行きては水尽きる処、坐しては雲起こる時を見る。柔軟な心境こそ最大の強みです。",
            "一歩一歩の足跡が、未来の豊かな実りを育んでいます。歩みを止めない自分を誇りましょう。"
        ]
    elif "ko" in lang:
        affirmations = [
            "불안한 미래를 걱정하기보다 명확한 현재에 집중하세요. 지금 이 순간에 머무르세요.",
            "서두르지 마세요. 마음에 여유를 줄 때 복잡한 안개가 걷히고 답이 보입니다.",
            "외부 상황은 마음의 거울입니다. 나만의 리듬과 중심을 지키면 상황은 달라집니다.",
            "잠시 멈춰 서는 시간은 다음 도약을 위한 소중한 에너지를 축적하는 과정입니다.",
            "통제할 수 없는 불확실성을 내려놓고, 오늘 내가 할 수 있는 작은 한 걸음에 집중하세요.",
            "자신과 타인을 온화하면서도 단단하게 대하세요. 침착함 자체가 강력한 빛입니다.",
            "물길이 다한 곳에서 피어오르는 구름을 보듯, 관점을 바꾸면 위기가 곧 기회가 됩니다.",
            "인생에 헛된 경험은 없습니다. 모든 발걸음이 내일의 값진 결실을 만들고 있습니다."
        ]
    else:
        affirmations = [
            "不為模糊不清的未來擔憂，只為清清楚楚的現在努力。安住當下，心無罣礙。",
            "事緩則圓，給思緒留一點沉澱的空間，迷霧散去，答案自會清澈浮現。",
            "外在的境遇是映照內心的鏡子；守住自己的節奏與正念，境隨心轉。",
            "每一次的停頓與等待，都是生命在為下一段躍進蓄積深厚能量。",
            "接納客觀局勢的未知，把注意力收回到今天能掌控的一小步行動上。",
            "以溫和而堅定的態度對待自己與他人，沉著從容，自帶光芒。",
            "行到水窮處，坐看雲起時；轉念即是轉機，順應機緣方得自若。",
            "人生沒有白走的路，每一步腳印都在替未來的開花結果鋪路。",
            "當你停止內耗、專注於此刻能做的小事，宇宙便會開始為你調度資源。",
            "順境時心懷謙卑與感恩，逆境時修養定力與智慧，心中自有一片晴空。"
        ]

    # 1. 查詢 SQLite 中今日此 IP 或 Device 是否已抽取過
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_lot_draws
                WHERE draw_date = ? AND (ip_address = ? OR (device_id != 'device_unknown' AND device_id = ?))
                ORDER BY id ASC LIMIT 1
            """, (date_str, client_ip, eff_device_id))
            existing_row = cursor.fetchone()

            if existing_row:
                # 已經抽取過，返回已鎖定的籤詩
                locked_lot_number = existing_row["lot_number"]
                locked_lot_type = existing_row["lot_type"]
                locked_focus = existing_row["daily_focus"] or affirmations[locked_lot_number % len(affirmations)]
                lot = fetch_lot_from_db(locked_lot_type, locked_lot_number)

                return {
                    "success": True,
                    "date": date_str,
                    "lot_type": locked_lot_type,
                    "lot_type_name": LOT_SYSTEMS.get(locked_lot_type, {}).get("name", "靈籤"),
                    "lot_number": locked_lot_number,
                    "device_id": eff_device_id,
                    "daily_focus": locked_focus,
                    "is_locked": True,
                    "already_drawn_today": True,
                    "lot": lot,
                    "message": "今日已揭曉專屬心靈晨光（一裝置/IP 每日限抽乙次）"
                }

            # 2. 尚未抽取，透過 Hash 種子計算唯一籤號並存入資料庫
            seed_str = f"daily_{date_str}_{client_ip}_{eff_device_id}_{lot_type}"
            hash_int = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
            daily_lot_number = (hash_int % max_lots) + 1
            daily_focus = affirmations[hash_int % len(affirmations)]
            
            cursor.execute("""
                INSERT INTO daily_lot_draws (draw_date, ip_address, device_id, lot_type, lot_number, daily_focus)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, client_ip, eff_device_id, lot_type, daily_lot_number, daily_focus))
            conn.commit()

            lot = fetch_lot_from_db(lot_type, daily_lot_number)

            return {
                "success": True,
                "date": date_str,
                "lot_type": lot_type,
                "lot_type_name": system_info["name"],
                "lot_number": daily_lot_number,
                "device_id": eff_device_id,
                "daily_focus": daily_focus,
                "is_locked": True,
                "already_drawn_today": False,
                "lot": lot
            }

    except Exception as e:
        logger.error(f"Error handling daily lot with DB lock: {e}")
        # 降級種子模式
        seed_str = f"daily_{date_str}_{lot_type}_{client_ip}"
        hash_int = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        daily_lot_number = (hash_int % max_lots) + 1
        daily_focus = affirmations[hash_int % len(affirmations)]
        lot = fetch_lot_from_db(lot_type, daily_lot_number)
        return {
            "success": True,
            "date": date_str,
            "lot_type": lot_type,
            "lot_type_name": system_info["name"],
            "lot_number": daily_lot_number,
            "device_id": eff_device_id,
            "daily_focus": daily_focus,
            "is_locked": True,
            "already_drawn_today": False,
            "lot": lot
        }

@app.post("/api/interpret", response_model=InterpretResponse)
async def interpret_lot(req: InterpretRequest):
    """
    接收籤系、抽籤號碼、使用者問題與語系，查詢 SQLite 籤詩資料庫，進行 AI 心理學賦權解籤並存檔。
    """
    effective_model = req.model or current_runtime_model
    effective_lang = req.language or "zh-TW"
    logger.info(f"Received interpretation request - Model: {effective_model}, Lang: {effective_lang}, System: {req.lot_type}, Lot: {req.lot_number}, Question: {req.user_question}")

    # 0. 依籤詩系統動態驗證 lot_number 上限
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
    
    # 2. 呼叫 AI 進行結構化解析 (支援多語系)
    analysis, model_used = generate_ai_interpretation(lot, req.user_question, effective_model, effective_lang)
    
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
