# clients/weather_client.py
import requests
import urllib3
from config import WEATHER_API_KEY

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WeatherService:
    def __init__(self):
        self.headers = {"Authorization": WEATHER_API_KEY}
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/"
        
        # 全台灣 22 縣市專屬 API 路由表
        self.city_map = {
            "宜蘭縣": "F-D0047-001", "桃園市": "F-D0047-005", "新竹縣": "F-D0047-009",
            "苗栗縣": "F-D0047-013", "彰化縣": "F-D0047-017", "南投縣": "F-D0047-021",
            "雲林縣": "F-D0047-025", "嘉義縣": "F-D0047-029", "屏東縣": "F-D0047-033",
            "臺東縣": "F-D0047-037", "花蓮縣": "F-D0047-041", "澎湖縣": "F-D0047-045",
            "基隆市": "F-D0047-049", "新竹市": "F-D0047-053", "嘉義市": "F-D0047-057",
            "臺北市": "F-D0047-061", "高雄市": "F-D0047-065", "新北市": "F-D0047-069",
            "臺中市": "F-D0047-073", "臺南市": "F-D0047-077", "連江縣": "F-D0047-081",
            "金門縣": "F-D0047-085"
        }

    def get_town_weather(self, city_name: str, town_name: str) -> dict:
        if not WEATHER_API_KEY:
            return {"error": "未設定天氣 API 金鑰"}

        normalized_city = city_name.replace("台", "臺")
        dataset_id = self.city_map.get(normalized_city)
        if not dataset_id:
            return {"error": f"找不到 {city_name} 的 API 路由"}

        target_url = f"{self.base_url}{dataset_id}"

        # 🌟 關鍵修正：不在 URL 進行過濾，直接裸抓該縣市！
        params = {"format": "JSON"}

        try:
            response = requests.get(target_url, headers=self.headers, params=params, verify=False)
            if response.status_code != 200:
                return {"error": f"API 請求失敗: HTTP {response.status_code}"}
                
            data = response.json()
            locations_list = data.get("records", {}).get("Locations", [])
            if not locations_list:
                return {"error": f"氣象署沒有回傳資料"}

            # 抓出該縣市下所有的「區」
            districts = locations_list[0].get("Location", [])
            
            # 🌟 在 Python 裡面用迴圈尋找我們的目標區
            target_district = None
            for d in districts:
                if d.get("LocationName") == town_name:
                    target_district = d
                    break

            if not target_district:
                return {"error": f"在 {normalized_city} 中找不到 {town_name}"}

            # 🌟 尋找終極大絕招：「天氣預報綜合描述」
            for element in target_district.get("WeatherElement", []):
                if element.get("ElementName") == "天氣預報綜合描述":
                    # 抽出最近一個時段的描述
                    forecast_str = element["Time"][0]["ElementValue"][0]["WeatherDescription"]
                    
                    return {
                        "city": f"{normalized_city}{town_name}",
                        "suggestion": forecast_str
                    }

            return {"error": "找不到天氣預報綜合描述欄位"}

        except Exception as e:
            return {"error": f"解析發生錯誤: {e}"}

# ==========================================
# 🧪 測試區塊 
# ==========================================
if __name__ == "__main__":
    weather_svc = WeatherService()
    
    test_locations = [
        ("臺中市", "西屯區"),
        ("臺北市", "信義區"),
        ("屏東縣", "恆春鎮"),
        ("桃園市", "中壢區")
    ]
    
    print("全台動態天氣測試...\n")
    for city, town in test_locations:
        result = weather_svc.get_town_weather(city, town)
        if "error" in result:
            print(f"❌ {city}{town}: {result['error']}")
        else:
            print(f"✅ {city}{town}: {result['suggestion']}")