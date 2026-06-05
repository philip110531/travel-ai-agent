import sqlite3
import os, sys

DB_PATH = "travel_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 記帳表 (保持不變)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_name TEXT NOT NULL,
            payer TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            participants TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. 行程表 (新增 city 與 town 欄位)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itinerary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_name TEXT NOT NULL,
            day INTEGER NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            city TEXT NOT NULL,          -- 新增：縣市 (如: 臺北市)
            town TEXT NOT NULL,          -- 新增：鄉鎮市區 (如: 信義區)
            description TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()
    print("✅ 資料庫 (包含天氣區域欄位) 初始化完成。", file=sys.stderr)

# ... [保留 add_expense 函數] ...

# ==========================================
# 行程表專用函數 (增、刪、改、查)
# ==========================================

def add_schedule_item(trip_name: str, day: int, time: str, location: str, city: str, town: str, description: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO itinerary (trip_name, day, time, location, city, town, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (trip_name, day, time, location, city, town, description)
        )
        conn.commit()
        conn.close()
        return f"✅ 已新增：第{day}天 {time} 前往 {city}{town}的【{location}】。"
    except Exception as e:
        return f"❌ 新增失敗：{str(e)}"

def get_trip_schedule(trip_name: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 查詢時必須把 id 拿出來，AI 之後修改或刪除才找得到目標
        cursor.execute(
            "SELECT id, day, time, location, city, town, description, status FROM itinerary WHERE trip_name = ? ORDER BY day ASC, time ASC",
            (trip_name,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"目前 {trip_name} 還沒有安排任何行程。"
            
        result = f"【{trip_name} 行程表】\n"
        current_day = 0
        for row in rows:
            item_id, day, time, loc, city, town, desc, status = row
            if day != current_day:
                result += f"\n👉 第 {day} 天：\n"
                current_day = day
            
            status_mark = "✅" if status == "completed" else "🕒" if status == "pending" else "❌"
            # 印出 [ID] 讓 AI 知道這筆行程的代號
            result += f"  [行程編號:{item_id}] {status_mark} {time} - {loc} ({city}{town}) 備註:{desc}\n"
            
        return result
    except Exception as e:
        return f"❌ 查詢失敗：{str(e)}"

def update_schedule_item(item_id: int, new_time: str, new_location: str, new_city: str, new_town: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE itinerary SET time=?, location=?, city=?, town=? WHERE id=?",
            (new_time, new_location, new_city, new_town, item_id)
        )
        conn.commit()
        conn.close()
        return f"✅ 行程編號 {item_id} 已成功更新為：{new_time} {new_location} ({new_city}{new_town})。"
    except Exception as e:
        return f"❌ 更新失敗：{str(e)}"

def delete_schedule_item(item_id: int) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM itinerary WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        return f"✅ 行程編號 {item_id} 已成功刪除。"
    except Exception as e:
        return f"❌ 刪除失敗：{str(e)}"

if __name__ == "__main__":
    init_db()