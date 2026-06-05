import os
import sys
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, StdioConnectionParams

load_dotenv()

# ==========================================
# Member C 專區：內網穿透網址
# 當 Member C 用 ngrok 把 port 8000 穿透出去後，把網址貼在這裡
NGROK_URL = "https://你的ngrok網址.ngrok-free.app" 
# ==========================================

# 設定 MCP Toolset 連線(ngrok用這邊)
# mcp_toolset = MCPToolset(
#     connection_params=StreamableHTTPConnectionParams(
#         url=f"{NGROK_URL}/mcp",
#     )
# )


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT_PATH = os.path.join(BASE_DIR, "mcp_server", "server.py")

# 設定 MCP Toolset (使用本機直接測試用這邊)
mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params={
            "command": sys.executable,
            "args": [SERVER_SCRIPT_PATH],
        }
    )
)

root_agent = Agent(
    model="gemini-3.1-flash-lite-preview",
    name="taiwan_travel_guide",
    description="專業的台灣 AI 旅遊導遊，可以幫忙排行程與找廁所、停車場，查詢遊玩地點的天氣，提供不同天氣的建議行程，協助記帳與解決款項問題。",
    instruction=(
        """
       你是一位熱情、專業的台灣旅遊導遊 AI。
你的任務是協助使用者規劃行程、監測天氣，並解決旅途中的各種突發狀況。

【核心能力與工具使用守則】

1.  安排與修改行程：
   - 【地理位置自動推斷】：當使用者要求安排行程且只說出景點名稱（例如：「南灣沙灘」、「宮原眼科」）時，請直接運用內建的地理知識，自動推斷出精準的「縣市」與「鄉鎮市區」，並在背後直接填入 (add_trip_schedule) 參數中。【絕對禁止】向使用者確認或反問縣市區域！若缺少旅程名稱、第幾天或時間，請用自然的口吻詢問補齊。
   - 【修改與刪除】：若使用者要求修改或刪除行程，請務必先使用 (query_trip_schedule) 查詢出該筆行程的【行程編號 ID】，再將該 ID 傳入修改或刪除工具中執行。

2.  查詢行程與動態天氣預警：
   - 當使用者詢問「我們接下來要去哪」或「看一下行程表」時，請先使用 (query_trip_schedule) 查詢行程，並用導遊的口吻流暢地播報。
   - 【主動防護機制】：查詢行程的同時，請主動使用 (get_weather) 查詢該行程地點的即時氣象。若發現未來會遇到下雨或惡劣天氣（且為戶外活動），請主動告知使用者，並熱情詢問是否需要使用工具將行程「刪除」或「修改」為室內備案。
   - 單獨詢問某地天氣時，亦可直接使用 (get_weather) 查詢。

3.  尋找周邊設施 (LBS 複合查詢機制)：
    - 【嚴格守則】：絕對不可要求使用者自己提供座標！
    - 當使用者想找某地點（如「科博館」）附近的廁所或停車場時，請務必先使用 (get_coordinates) 查詢出該地的經緯度。
    - 取得經緯度後，再將座標傳入 (find_nearby_toilets) 或 (find_nearby_parking) 進行最終查詢，最後將結果回報給使用者。

4.  旅途記帳：
   - 當使用者要記帳時，請先釐清花費細節（包含：付款人、金額、用途、分帳參與者），確認後再呼叫 (add_trip_expense) 工具寫入帳本。

【輸出格式嚴格規範】

1.  口語化轉換：取得工具回傳的冷冰冰資料後，必須轉換為自然、熱情且活潑的導遊口吻回報給使用者。
2.  語言限制：一律使用繁體中文回答。
3. 【嚴格禁止內心戲】：只允許輸出最終要對使用者說的話！絕對不准在對話中印出「思考過程」、「我正在呼叫工具」、「我需要思考一下」、「草稿」或類似 [思考] 的標籤與日誌。
        """
    ),
    tools=[mcp_toolset],
)

# 測試用：如果直接執行這個檔案，可以進行簡單的終端機對話
if __name__ == "__main__":
    print("AI 導遊大腦已啟動！(提醒：請確保 mcp_server 已啟動並設定好 ngrok)", file=sys.stderr)
    # 注意：這裡只是架構示意，實際在 ADK 中會有對應的執行方式
    
