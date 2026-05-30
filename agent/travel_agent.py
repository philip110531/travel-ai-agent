import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

load_dotenv()

# ==========================================
# Member C 專區：內網穿透網址
# 當 Member C 用 ngrok 把 port 8000 穿透出去後，把網址貼在這裡
NGROK_URL = "https://你的ngrok網址.ngrok-free.app" 
# ==========================================

# 設定 MCP Toolset 連線
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{NGROK_URL}/mcp",
    )
)

travel_agent = Agent(
    model="gemini-2.5-flash",
    name="taiwan_travel_guide",
    description="專業的台灣 AI 旅遊導遊，可以幫忙排行程與找廁所。",
    instruction=(
        """
        你是一位熱情、專業的台灣旅遊導遊 AI。
        你的任務是協助使用者規劃行程，並解決旅途中的突發狀況。
        
        【重要規則】
        1. 當使用者說想上廁所，或詢問附近哪裡有公廁時，你必須引導他們提供「經緯度座標」，
           然後使用 MCP 工具 (find_nearby_toilets) 來獲取附近的公廁資訊。
        2. 取得公廁資訊後，請用自然的口語化方式回報給使用者。
        3. 請一律使用繁體中文回答。
        """
    ),
    tools=[mcp_toolset],
)

# 測試用：如果直接執行這個檔案，可以進行簡單的終端機對話
if __name__ == "__main__":
    print("AI 導遊大腦已啟動！(提醒：請確保 mcp_server 已啟動並設定好 ngrok)")
    # 注意：這裡只是架構示意，實際在 ADK 中會有對應的執行方式