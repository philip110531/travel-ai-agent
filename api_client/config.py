import os, sys
from dotenv import load_dotenv

# 1. 取得目前 config.py 所在資料夾 (api_client) 的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 往上一層推，找到專案根目錄 (travel_ai_agent)
base_dir = os.path.dirname(current_dir)

# 3. 精準定位 .env 檔案的絕對路徑
env_path = os.path.join(base_dir, ".env")

# 4. 強制載入該路徑的 .env 檔案
load_dotenv(dotenv_path=env_path)

# ==========================================
# 讀取金鑰
# ==========================================
TDX_CLIENT_ID = os.getenv("TDX_CLIENT_ID")
TDX_CLIENT_SECRET = os.getenv("TDX_CLIENT_SECRET")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TDX_CLIENT_ID or not TDX_CLIENT_SECRET:
    print(f"警告：TDX API 金鑰未設定，請確認 {env_path} 中有正確的金鑰。", file=sys.stderr)
if not WEATHER_API_KEY:
    print(f"警告：天氣預報 API 金鑰未設定，請確認 {env_path} 中有正確的金鑰。", file=sys.stderr)