# clients/tdx_client.py
import requests
import json
# 從同一個資料夾的 config.py 讀取金鑰
from config import TDX_CLIENT_ID, TDX_CLIENT_SECRET

class TDXClient:
    def __init__(self):
        # 1. 取得 Token 的專屬網址
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        # 2. 初始化時自動去拿一張通行證 (Token)
        self.access_token = self._get_token()

    def _get_token(self):
        """向 TDX 伺服器換取 Access Token"""
        data = {
            "content-type": "application/x-www-form-urlencoded",
            "grant_type": "client_credentials",
            "client_id": TDX_CLIENT_ID,
            "client_secret": TDX_CLIENT_SECRET
        }
        response = requests.post(self.auth_url, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(f"TDX Token 取得失敗，請檢查 .env 的金鑰是否正確！錯誤訊息: {response.text}")

    def get_nearby_parking(self, lat: float, lon: float, radius_meters: int = 500):
        """
        使用 TDX Advanced API 找尋附近的停車場基本資料
        """
        # 你指定的進階空間查詢 API
        url = "https://tdx.transportdata.tw/api/advanced/v1/Parking/OffStreet/CarPark/NearBy"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        # TDX 的空間過濾參數：利用 $spatialFilter 讓政府的伺服器幫我們算距離
        params = {
            "$spatialFilter": f"nearby({lat}, {lon}, {radius_meters})",
            "$format": "JSON"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API 請求失敗: HTTP {response.status_code}")
            return None

# ==========================================
# 測試區塊 (只會在直接執行此檔案時運作)
# ==========================================
if __name__ == "__main__":
    print("啟動 TDX 客戶端，正在連線換取 Token...")
    client = TDXClient()
    print("✅ Token 取得成功！\n")
    
    # 測試地點：中壢火車站
    test_lat = 24.9537
    test_lon = 121.2256
    search_radius = 500
    
    print(f"正在搜尋 中壢火車站 ({test_lat}, {test_lon}) 附近 {search_radius} 公尺的路外停車場...")
    
    # 呼叫 API
    result_data = client.get_nearby_parking(test_lat, test_lon, search_radius)
    
    if result_data:
        # TDX 的 Advanced API 回傳通常會是一個包含多筆資料的列表 (List) 或是包在 CarParks 裡面
        # 這裡做一個安全的讀取機制
        parks = result_data.get("CarParks", []) if isinstance(result_data, dict) else result_data

        print(json.dumps(parks[0], ensure_ascii=False, indent=4))
        print(f"成功找到 {len(parks)} 個停車場！前 3 筆資料摘要：\n")
        for i, park in enumerate(parks[:3], 1):
            # TDX 的 JSON 結構比較深，我們把它挖出來印
            name = park.get("CarParkName", {}).get("Zh_tw", "未知名稱")
            address = park.get("Address", "無地址")
            
            print(f"[{i}] 🅿️ {name}")
            print(f"    📍 地址: {address}")
    else:
        print("⚠️ 沒有抓到資料。")