# -*- coding: utf-8 -*-
"""
Compile all 260 lots, generate schema.sql, save json files, and initialize SQLite temple.db
"""

import os
import json
import sqlite3
from scripts.build_temple_datasets import LOTS_60_JIAZI
from scripts.lots_guandi_100 import LOTS_GUANDI_100
from scripts.lots_guanyin_100 import LOTS_GUANYIN_100

def run():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. Format all records
    records_60_jiazi = []
    for item in LOTS_60_JIAZI:
        records_60_jiazi.append({
            "lot_type": "60_jiazi",
            "lot_type_name": "六十甲子籤",
            "lot_number": item["lot_number"],
            "lot_name": item["lot_name"],
            "grade": item["grade"],
            "content": item["content"],
            "story": item["story"]
        })

    records_guandi_100 = []
    for item in LOTS_GUANDI_100:
        records_guandi_100.append({
            "lot_type": "guandi_100",
            "lot_type_name": "關聖帝君一百籤",
            "lot_number": item["lot_number"],
            "lot_name": item["lot_name"],
            "grade": item["grade"],
            "content": item["content"],
            "story": item["story"]
        })

    records_guanyin_100 = []
    for item in LOTS_GUANYIN_100:
        records_guanyin_100.append({
            "lot_type": "guanyin_100",
            "lot_type_name": "觀音靈籤一百首",
            "lot_number": item["lot_number"],
            "lot_name": item["lot_name"],
            "grade": item["grade"],
            "content": item["content"],
            "story": item["story"]
        })

    all_records = records_60_jiazi + records_guandi_100 + records_guanyin_100
    print(f"Total compiled lots: {len(all_records)} (60_jiazi: {len(records_60_jiazi)}, guandi_100: {len(records_guandi_100)}, guanyin_100: {len(records_guanyin_100)})")

    # 2. Write JSON files
    with open(os.path.join(data_dir, "lots_60_jiazi.json"), "w", encoding="utf-8") as f:
        json.dump(records_60_jiazi, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, "lots_guandi_100.json"), "w", encoding="utf-8") as f:
        json.dump(records_guandi_100, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, "lots_guanyin_100.json"), "w", encoding="utf-8") as f:
        json.dump(records_guanyin_100, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, "lots_all.json"), "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print("Saved JSON files to data/ folder.")

    # 3. Generate schema.sql
    sql_statements = [
        "-- ==============================================================================",
        "-- SQLite 資料庫結構定義 (線上宮廟智慧解籤系統 - 260 首傳統靈籤完整版)",
        "-- 包含：六十甲子籤 (60首)、關聖帝君一百籤 (100首)、觀音靈籤一百首 (100首)",
        "-- ==============================================================================\n",
        "-- 1. 籤詩基本資料表 (lots)",
        "CREATE TABLE IF NOT EXISTS lots (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    lot_type TEXT NOT NULL,                       -- 籤詩系統類別 (60_jiazi / guandi_100 / guanyin_100)",
        "    lot_type_name TEXT NOT NULL,                  -- 籤詩系統名稱 (六十甲子籤 / 關聖帝君一百籤 / 觀音靈籤一百首)",
        "    lot_number INTEGER NOT NULL,                  -- 籤號 (1 ~ 60 或 1 ~ 100)",
        "    lot_name TEXT NOT NULL,                       -- 籤名 (例如：第一籤 甲子、第一籤 甲甲、第一籤)",
        "    grade TEXT NOT NULL,                          -- 吉凶等級 (大吉、上上、上吉、中吉、中平、下下等)",
        "    content TEXT NOT NULL,                        -- 籤詩原文 (四句七言/五言詩)",
        "    story TEXT NOT NULL,                          -- 典故由來與歷史象徵",
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "    UNIQUE(lot_type, lot_number)",
        ");\n",
        "CREATE INDEX IF NOT EXISTS idx_lots_type_number ON lots(lot_type, lot_number);\n",
        "-- 2. 抽籤與 AI 解析紀錄表 (user_draws)",
        "CREATE TABLE IF NOT EXISTS user_draws (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    lot_id INTEGER,",
        "    lot_type TEXT DEFAULT '60_jiazi',",
        "    lot_number INTEGER NOT NULL,",
        "    user_question TEXT NOT NULL,",
        "    ai_analysis TEXT NOT NULL,",
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "    FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL",
        ");\n",
        "CREATE INDEX IF NOT EXISTS idx_user_draws_created_at ON user_draws(created_at DESC);\n",
        "-- ==============================================================================",
        "-- 3. 籤詩資料注入 (260 首完整種子資料)",
        "-- =============================================================================="
    ]

    for rec in all_records:
        escaped_content = rec["content"].replace("'", "''")
        escaped_story = rec["story"].replace("'", "''")
        escaped_name = rec["lot_name"].replace("'", "''")
        escaped_type_name = rec["lot_type_name"].replace("'", "''")
        sql = (
            f"INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) "
            f"VALUES ('{rec['lot_type']}', '{escaped_type_name}', {rec['lot_number']}, '{escaped_name}', '{rec['grade']}', '{escaped_content}', '{escaped_story}');"
        )
        sql_statements.append(sql)

    schema_path = os.path.join(base_dir, "schema.sql")
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements) + "\n")

    print(f"Generated schema.sql with {len(all_records)} insert statements.")

    # 4. Insert directly into SQLite temple.db
    db_path = os.path.join(base_dir, "temple.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lots_type_number ON lots(lot_type, lot_number);")
    
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_draws_created_at ON user_draws(created_at DESC);")

    for rec in all_records:
        cursor.execute("""
            INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rec["lot_type"], rec["lot_type_name"], rec["lot_number"], rec["lot_name"], rec["grade"], rec["content"], rec["story"]))

    conn.commit()
    cursor.execute("SELECT lot_type, COUNT(*) FROM lots GROUP BY lot_type")
    counts = cursor.fetchall()
    print("Database SQLite populated successfully:")
    for t, c in counts:
        print(f"  - {t}: {c} lots")

    conn.close()

if __name__ == "__main__":
    run()
