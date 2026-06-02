import os
from dotenv import load_dotenv

load_dotenv()

TDX_CLIENT_ID = os.getenv("TDX_CLIENT_ID")
TDX_CLIENT_SECRET = os.getenv("TDX_CLIENT_SECRET")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not TDX_CLIENT_ID or not TDX_CLIENT_SECRET:
    print("警告：TDX API 金鑰未設定，請確認 .env 檔案中有正確的 TDX_CLIENT_ID 和 TDX_CLIENT_SECRET。")
if not WEATHER_API_KEY:
    print("警告：天氣預報 API 金鑰未設定，請確認 .env 檔案中有正確的 WEATHER_API_KEY。")