from fastmcp import FastMCP
import json
import os
import sys

from lbs_utils import calculate_distance
import database
from geopy.geocoders import Nominatim

# 1. 處理資料夾路徑，讓 server.py 能讀取到上一層 api_client 裡面的程式
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
api_client_dir = os.path.join(base_dir, "api_client")
if api_client_dir not in sys.path:
    sys.path.append(api_client_dir)

# 2. 引入寫好的客戶端
from tdx_client import TDXClient
from weather_client import WeatherService


# 3. 初始化外部 API 客戶端 (確保伺服器啟動時，Token 就準備好了)
print("正在初始化外部 API...", file=sys.stderr)
tdx_client = TDXClient()
weather_service = WeatherService()
print("外部 API 初始化完成！", file=sys.stderr)

# 初始化 MCP Server
mcp = FastMCP(name="travel_guide_server")

# 確保伺服器啟動時，資料庫已經準備好
database.init_db()

# ---------------------------------------------------------
# LBS 工具區
# ---------------------------------------------------------

@mcp.tool
def find_nearby_toilets(latitude: float, longitude: float) -> str:
    """
    尋找使用者所在地附近的公廁。
    Args:
        latitude (float): 使用者當下的緯度。
        longitude (float): 使用者當下的經度。
    Returns:
        str: 附近的公廁資訊回報。
    """
    print(f"--- 收到尋找廁所請求！座標: ({latitude}, {longitude}) ---", file=sys.stderr)
    
    # 1. 計算真實 JSON 檔案的路徑
    # 假設 server.py 在 mcp_server 資料夾，JSON 在上一層的 datas 資料夾
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "datas", "toilet_processed.json")
    
    # 2. 嘗試讀取 Member C 準備的資料
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            real_toilets = json.load(f)
    except FileNotFoundError:
        return "系統錯誤：找不到公廁資料庫 (toilet_processed.json)，請確認資料已備妥。"
    except json.JSONDecodeError:
        return "系統錯誤：公廁資料庫格式損壞。"

    # LBS 核心運算：計算距離並找出最近的
    nearest_toilet = None
    min_distance = float('inf')

    # 注意這裡把假資料變數換成了 real_toilets
    for toilet in real_toilets:
        # 假設真實 JSON 的欄位名稱也是 lat 和 lon，如果有不同需對應修改
        dist = calculate_distance(latitude, longitude, toilet.get("lat", 0), toilet.get("lon", 0))
        if dist < min_distance:
            min_distance = dist
            nearest_toilet = toilet
            
    # 如果最近的廁所超過 2000 公尺，就說附近沒有
    if min_distance > 2000:
        return "很抱歉，在您方圓 2 公里內找不到公廁。"
    
    acc_text = "備有無障礙設施" if nearest_toilet["accessibility"] else "無無障礙設施"
    
    result = (
        f"根據您的座標，為您找到最近的公廁是「{nearest_toilet['name']}」，"
        f"距離約 {int(min_distance)} 公尺，且{acc_text}。"
    )
    return result

# ---------------------------------------------------------
# 記帳工具區
# ---------------------------------------------------------

@mcp.tool
def add_trip_expense(trip_name: str, payer: str, amount: float, description: str, participants: str) -> str:
    """
    新增一筆旅途花費，用於群組記帳與分帳。
    Args:
        trip_name (str): 這趟旅程的名稱 (例如: 宜蘭二日遊)。
        payer (str): 付錢的人是誰 (例如: 小明)。
        amount (float): 總共付了多少錢。
        description (str): 這筆錢花在哪裡 (例如: 午餐吃牛肉麵)。
        participants (str): 有誰要一起分這筆錢，請用逗號分隔名字 (例如: 小明,小華,小美)。
    Returns:
        str: 記帳結果回報。
    """
    print(f"--- 收到記帳請求！{payer} 付了 {amount} ({description}) ---", file=sys.stderr)
    return database.add_expense(trip_name, payer, amount, description, participants)

# ==========================================
# 新增的工具：天氣與停車場
# ==========================================

@mcp.tool
def get_weather(city_name: str, town_name: str) -> str:
    """
    查詢指定縣市與鄉鎮市區的即時天氣預報。
    Args:
        city_name (str): 縣市名稱 (例如: 臺北市, 臺中市)。
        town_name (str): 鄉鎮市區名稱 (例如: 信義區, 西屯區)。
    Returns:
        str: 該地區的天氣概況與建議。
    """
    print(f"--- 收到天氣查詢請求！{city_name}{town_name} ---", file=sys.stderr)
    result = weather_service.get_town_weather(city_name, town_name)
    
    if "error" in result:
        return f"天氣查詢失敗：{result['error']}"
        
    return f"【{city_name}{town_name} 天氣概況】\n{result['suggestion']}"

@mcp.tool
def find_nearby_parking(latitude: float, longitude: float, radius: int = 500) -> str:
    """
    尋找使用者所在地附近的停車場。
    Args:
        latitude (float): 緯度。
        longitude (float): 經度。
        radius (int): 搜尋半徑(公尺)，預設為 500。
    Returns:
        str: 附近的停車場資訊。
    """
    print(f"--- 收到停車場查詢請求！座標: ({latitude}, {longitude}) ---", file=sys.stderr)
    result_data = tdx_client.get_nearby_parking(latitude, longitude, radius)

    if not result_data:
        return "抱歉，目前無法取得停車場資料，或連線發生錯誤。"

    # 安全地讀取 TDX 資料結構
    parks = result_data.get("CarParks", []) if isinstance(result_data, dict) else result_data

    if not parks:
        return f"在您方圓 {radius} 公尺內沒有找到路外停車場。"

    # 整理前 3 個停車場回傳給 AI
    reply = f"為您找到附近 {len(parks)} 個停車場，以下是最接近的前 3 個：\n"
    for i, park in enumerate(parks[:3], 1):
        name = park.get("CarParkName", {}).get("Zh_tw", "未知名稱")
        address = park.get("Address", "無地址")
        reply += f"{i}. {name} (地址: {address})\n"

    return reply

# ==========================================
# 行程管理工具區
# ==========================================

@mcp.tool
def add_trip_schedule(trip_name: str, day: int, time: str, location: str, city: str, town: str, description: str = "") -> str:
    """
    安排新增行程。
    Args:
        trip_name (str): 旅程名稱。
        day (int): 第幾天。
        time (str): 時間 (如: 10:30)。
        location (str): 地點名稱 (如: 逢甲夜市)。
        city (str): 縣市 (如: 臺中市)。
        town (str): 鄉鎮市區 (如: 西屯區)。
        description (str): 備註。
    """
    return database.add_schedule_item(trip_name, day, time, location, city, town, description)

@mcp.tool
def query_trip_schedule(trip_name: str) -> str:
    """查詢行程表，並取得各行程的【行程編號 ID】。"""
    return database.get_trip_schedule(trip_name)

@mcp.tool
def modify_trip_schedule(item_id: int, new_time: str, new_location: str, new_city: str, new_town: str) -> str:
    """
    修改已存在的行程。
    Args:
        item_id (int): 從 query_trip_schedule 查詢到的【行程編號】。
        new_time (str): 新的時間。
        new_location (str): 新的地點名稱。
        new_city (str): 新的縣市。
        new_town (str): 新的鄉鎮市區。
    """
    return database.update_schedule_item(item_id, new_time, new_location, new_city, new_town)

@mcp.tool
def remove_trip_schedule(item_id: int) -> str:
    """
    刪除不需要的行程。
    Args:
        item_id (int): 從 query_trip_schedule 查詢到的【行程編號】。
    """
    return database.delete_schedule_item(item_id)

@mcp.tool
def get_coordinates(location_name: str) -> str:
    """
    將地點名稱轉換為經緯度座標 (Geocoding)。
    當需要尋找某個景點附近的設施 (停車場、廁所)，但缺乏座標時，請先呼叫此工具。
    Args:
        location_name (str): 地點名稱或地址 (例如: 國立自然科學博物館, 逢甲夜市)。
    Returns:
        str: 該地點的經緯度資訊，或找不到時的錯誤提示。
    """
    print(f"--- 收到座標查詢請求！地點: {location_name} ---", file=sys.stderr)
    try:
        # Nominatim 是免費服務，規定必須提供一個 user_agent 名稱
        geolocator = Nominatim(user_agent="travel_ai_agent_mcp")
        
        # 加上 "台灣" 關鍵字可以大幅提高搜尋的準確度
        search_query = f"{location_name}, 台灣"
        location = geolocator.geocode(search_query)
        
        if location:
            return f"找到「{location_name}」的座標：緯度 {location.latitude}, 經度 {location.longitude}"
        else:
            return f"抱歉，地圖資料庫中找不到「{location_name}」的精確座標，請嘗試提供更完整的名稱。"
    except Exception as e:
        return f"座標查詢發生錯誤: {str(e)}"

if __name__ == "__main__":
    print("啟動 Travel Guide MCP Server...", file=sys.stderr)
    # 使用 HTTP transport 啟動，port 設為 8000 (ngrok用下面這條)
    # mcp.run(transport="http", port=8000)
    
    
    # 使用本基測是用下面這條
    mcp.run(transport="stdio")