from fastmcp import FastMCP
import math

# 初始化 MCP Server
mcp = FastMCP(name="travel_guide_server")

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
    print(f"--- 收到尋找廁所請求！座標: ({latitude}, {longitude}) ---")
    
    # TODO (Member B): 這裡之後要實作去接政府開放平台 API 或資料庫的邏輯
    # 目前先回傳測試假資料
    
    result = (
        f"根據您的座標 ({latitude}, {longitude})，"
        f"為您找到最近的公廁是「車站前站公廁」，距離約 150 公尺，且備有無障礙設施。"
    )
    return result

if __name__ == "__main__":
    print("啟動 Travel Guide MCP Server...")
    # 使用 HTTP transport 啟動，port 設為 8000
    mcp.run(transport="http", port=8000)