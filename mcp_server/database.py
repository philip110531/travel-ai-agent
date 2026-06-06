import sqlite3
import os
import random
import string
import json
from datetime import datetime

# 使用絕對路徑，確保資料庫在專案根目錄
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "travel_ledger.db"
)

def init_db():
    """初始化所有資料表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ==========================================
    # 1. 房間表 - 用於無帳號狀態共享
    # ==========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT UNIQUE NOT NULL,
            room_name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            itinerary_data TEXT DEFAULT '{}'
        )
    """)
    
    # ==========================================
    # 2. 行程表 - 關聯到房間
    # ==========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itinerary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT NOT NULL,
            day INTEGER NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            city TEXT NOT NULL,
            town TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (room_code) REFERENCES rooms(room_code) ON DELETE CASCADE
        )
    """)
    
    # ==========================================
    # 3. 記帳表 - 關聯到房間
    # ==========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT NOT NULL,
            payer TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            participants TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_code) REFERENCES rooms(room_code) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 資料庫已初始化（包含房間管理系統）", flush=True)

# ==========================================
# 房間管理函數
# ==========================================

def generate_room_code():
    """
    生成 6 碼房間代碼 (如: TRV-A8K2)
    格式：TRV-XXXX (3字母+4隨機字母數字)
    """
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=4))
    return f"TRV-{code}"

def create_room(room_name: str) -> str:
    """
    建立新房間
    Returns: JSON 字符串，包含 room_code 和 message
    """
    try:
        room_code = generate_room_code()
        
        # 確保房間代碼不重複
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        while True:
            cursor.execute("SELECT id FROM rooms WHERE room_code = ?", (room_code,))
            if not cursor.fetchone():
                break
            room_code = generate_room_code()
        
        cursor.execute(
            "INSERT INTO rooms (room_code, room_name, itinerary_data) VALUES (?, ?, ?)",
            (room_code, room_name, json.dumps({"tripName": room_name, "days": []}))
        )
        conn.commit()
        conn.close()
        
        result = {
            "success": True,
            "room_code": room_code,
            "message": f"✅ 房間已建立！房間代碼是：【{room_code}】\n請妥善保管此代碼，日後可用它繼續編輯這份行程。"
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        result = {
            "success": False,
            "message": f"❌ 建立房間失敗：{str(e)}"
        }
        return json.dumps(result, ensure_ascii=False)

def get_or_create_room(room_code: str, room_name: str = None) -> str:
    """
    取得現有房間或建立新房間
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM rooms WHERE room_code = ?", (room_code,))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            return json.dumps({
                "success": True,
                "room_code": room_code,
                "message": f"✅ 房間【{room_code}】已加載！"
            }, ensure_ascii=False)
        else:
            if not room_name:
                room_name = f"旅程-{room_code}"
            return create_room(room_name)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"❌ 加載房間失敗：{str(e)}"
        }, ensure_ascii=False)

def get_room_itinerary_json(room_code: str) -> str:
    """
    取得房間的完整行程 JSON（用於隱藏標籤）
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT itinerary_data FROM rooms WHERE room_code = ?", (room_code,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return json.dumps({"tripName": "未知行程", "days": []})
    except Exception as e:
        print(f"❌ 查詢行程失敗：{str(e)}", flush=True)
        return json.dumps({"tripName": "錯誤", "days": []})

def update_room_itinerary(room_code: str, itinerary_json: str) -> str:
    """
    更新房間的行程 JSON
    """
    try:
        # 驗證 JSON 格式
        itinerary_data = json.loads(itinerary_json)

        if "room_code" in itinerary_data:
            del itinerary_data["room_code"] 

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rooms SET itinerary_data = ?, last_updated = CURRENT_TIMESTAMP WHERE room_code = ?",
            (json.dumps(itinerary_data, ensure_ascii=False), room_code)
        )
        conn.commit()
        conn.close()
        
        return json.dumps({
            "success": True,
            "message": f"✅ 房間【{room_code}】的行程已更新"
        }, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "message": "❌ 行程 JSON 格式錯誤"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"❌ 更新失敗：{str(e)}"
        }, ensure_ascii=False)

# ==========================================
# 行程管理函數 (改為使用 room_code)
# ==========================================

def add_schedule_item(room_code: str, day: int, time: str, location: str, city: str, town: str, description: str = "") -> str:
    """
    新增行程項目到房間
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO itinerary (room_code, day, time, location, city, town, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (room_code, day, time, location, city, town, description)
        )
        conn.commit()
        conn.close()
        return f"✅ 已新增：第{day}天 {time} 前往 {city}{town}的【{location}】。"
    except Exception as e:
        return f"❌ 新增失敗：{str(e)}"

def get_room_schedule(room_code: str) -> str:
    """
    查詢房間的完整行程表
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, day, time, location, city, town, description, status FROM itinerary WHERE room_code = ? ORDER BY day ASC, time ASC",
            (room_code,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"目前房間【{room_code}】還沒有安排任何行程。"
            
        result = f"【房間 {room_code} 的行程表】\n"
        current_day = 0
        for row in rows:
            item_id, day, time, loc, city, town, desc, status = row
            if day != current_day:
                result += f"\n👉 第 {day} 天：\n"
                current_day = day
            
            status_mark = "✅" if status == "completed" else "🕒" if status == "pending" else "❌"
            result += f"  [ID:{item_id}] {status_mark} {time} - {loc} ({city}{town})\n"
            
        return result
    except Exception as e:
        return f"❌ 查詢失敗：{str(e)}"

def update_schedule_item(item_id: int, new_time: str, new_location: str, new_city: str, new_town: str) -> str:
    """
    修改行程項目
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE itinerary SET time=?, location=?, city=?, town=? WHERE id=?",
            (new_time, new_location, new_city, new_town, item_id)
        )
        conn.commit()
        conn.close()
        return f"✅ 行程已成功更新。"
    except Exception as e:
        return f"❌ 更新失敗：{str(e)}"

def delete_schedule_item(item_id: int) -> str:
    """
    刪除行程項目
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM itinerary WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        return f"✅ 行程已成功刪除。"
    except Exception as e:
        return f"❌ 刪除失敗：{str(e)}"

# ==========================================
# 記帳管理函數 (改為使用 room_code)
# ==========================================

def add_expense(room_code: str, payer: str, amount: float, description: str, participants: str) -> str:
    """
    新增記帳項目到房間
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (room_code, payer, amount, description, participants) VALUES (?, ?, ?, ?, ?)",
            (room_code, payer, amount, description, participants)
        )
        conn.commit()
        conn.close()
        
        # 計算分帳
        participants_list = [p.strip() for p in participants.split(',')]
        per_person = amount / len(participants_list)
        
        result = f"✅ 記帳成功！\n{payer} 付了 ${amount:.2f}\n"
        result += f"分帳給：{', '.join(participants_list)}\n"
        result += f"每人應付：${per_person:.2f}"
        
        return result
    except Exception as e:
        return f"❌ 記帳失敗：{str(e)}"

def get_room_expenses(room_code: str) -> str:
    """
    查詢房間的全部記帳
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, payer, amount, description, participants, timestamp FROM expenses WHERE room_code = ? ORDER BY timestamp DESC",
            (room_code,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"房間【{room_code}】暫無記帳紀錄。"
            
        result = f"【房間 {room_code} 的記帳表】\n"
        total_amount = 0
        
        for row in rows:
            item_id, payer, amount, desc, participants, timestamp = row
            total_amount += amount
            result += f"• {timestamp[:10]} | {payer} 付 ${amount:.2f} ({desc})\n"
        
        result += f"\n總支出：${total_amount:.2f}"
        return result
    except Exception as e:
        return f"❌ 查詢失敗：{str(e)}"

if __name__ == "__main__":
    init_db()
    print("資料庫初始化完成", flush=True)
