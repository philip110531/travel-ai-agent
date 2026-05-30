# AI 旅遊導遊助手 (AI Travel Guide Agent)

這是一個結合大語言模型 (LLM)、適地性服務 (LBS) 與現代互動式網頁技術的 AI 旅遊專案。本系統採用業界最新的 **Model Context Protocol (MCP)** 架構，將 AI 的「大腦決策」與「後端實體操作」完美解耦，為使用者提供動態的旅遊規劃與當下情境的即時協助。

## 專案目標 (Project Goals)

打造一個不只是「文字對話框」的智慧旅遊系統。本專案將實現：
1. **互動式行程儀表板**：前端接收 AI 規劃的行程後，轉化為具有分頁、時間軸與景點卡片的豐富介面。
2. **LBS 即時周邊服務**：結合台灣政府資料開放平臺，根據使用者手機的 GPS 座標，即時運算並推薦最近的公廁與停車場。
3. **情境語音導覽**：導入 Web Speech API，讓系統具備擬人化的語音播報能力。
4. **現代化微服務架構**：實踐 AI Agent (Client) 與 FastMCP (Server) 雙向通訊的系統開發流程。
5. **動態行程重算**： 旅遊難免遇到突發狀況（例如：下雨、某個景點沒開、或者在某處待太久）。Agent 可以根據當下的時間與天氣，即時建議備案或重新排列後續行程。
6. **記帳與分帳功能**： 結合旅遊情境，讓使用者隨手對著 Agent 說「剛剛午餐我付了 1000 元，幫我跟小明、小華平分」，系統自動記錄進這趟旅程的帳本。
7. **協同編輯與群組功能(有空再做)**： 出遊通常是群體的。可以加入讓多個使用者加入同一個行程「房間」的功能，大家可以一起對 Agent 許願（例如：A說想吃燒肉，B說想去逛街），讓 Agent 綜合大家的意見排行程。

---

## 系統架構 (System Architecture)

專案採用標準的主從架構 (Client-Server)，分為三大模組：

* ** AI 大腦 (Google ADK)**：負責自然語言理解、意圖判斷。遇到需要外部資料時，主動呼叫 MCP Tool。
* ** 實體工具箱 (FastMCP Server)**：運行於本機的 Python 伺服器，負責執行實體邏輯（如：計算座標距離、撈取政府 API），並將結果回傳給 AI。
* ** 互動介面 (Frontend)**：將 AI 產出的結構化資料 (JSON) 渲染成可點擊、可互動的網頁視覺元件。

*(開發階段透過 **ngrok** 將本機 FastMCP 伺服器穿透至雲端，供 Google ADK 進行連線測試。)*

---

## 團隊分工與工作目標 (Team Roles & Tools)

本專案採用 FastMCP 微服務架構，團隊依據功能模組與技術棧劃分為四大角色，確保開發流程順暢且互不干擾：

### Member A: AI 大腦設計師 (AI Agent Developer)
* **工作目標**：
  * **核心對話與意圖識別**：設計 `travel_agent` 的 System Prompt，確保 AI 能精準區分使用者的意圖（例如：「排行程」、「找附近設施」或「記帳」），並觸發對應的 MCP Tool。
  * **動態行程重算邏輯**：撰寫情境提示詞，引導 AI 根據突發狀況（如下雨、延誤）與當下時間，自動提取備案並重新排列後續行程。
  * **自然語言處理 (NLP)**：處理記帳功能的實體擷取 (Entity Extraction)，將口語化的「剛剛午餐我付了 1000 元，幫我跟小明平分」精準轉換為結構化參數傳遞給後端。
* **使用工具**：Python, Google ADK 平台, Prompt Engineering。

### Member B: 核心後端工程師 (Backend & DB Developer)
* **工作目標**：
  * **MCP 伺服器建置**：建立與維護本機端的 FastMCP 伺服器，開發供 AI 呼叫的各項 `@mcp.tool` 函數。
  * **LBS 空間運算**：實作經緯度距離計算邏輯，當接收到前端座標時，能從資料中篩選並回傳最近的公廁與停車場。
  * **記帳資料庫設計**：建置輕量級資料庫，設計行程與帳本的資料表 (Schema)，並完成記帳系統的 CRUD (新增/讀取/更新/刪除) API 工具。
* **使用工具**：Python, FastMCP, SQLite (或 PostgreSQL), SQLAlchemy / SQLModel。

### Member C: 網路通訊與資料工程師 (Network & Data Engineer)
* **工作目標**：
  * **環境穿透與連線維護**：負責設定 Expose Local to Global 環境，提供穩定的 HTTPS 網址供 AI 大腦進行 Webhook 連線測試。
  * **政府與外部 API 介接**：下載並清洗台灣政府資料開放平臺的公廁與停車場資料；串接外部「天氣預報 API」，提供動態重算所需的天氣數據。
  * **資料預處理**：撰寫腳本將龐大的 CSV/JSON 開放資料轉換為後端資料庫易於讀取的格式。
* **使用工具**：ngrok 或 Cloudflare Tunnel, Python (Requests, Pandas), 外部天氣 API。

### Member D: 前端互動工程師 (Frontend UI/UX Developer)
* **工作目標**：
  * **互動式行程儀表板**：拋棄純文字框，將 AI 產出的行程 JSON 渲染為直覺的「分頁 (Tabs)」、「時間軸 (Timeline)」與「景點卡片」介面。
  * **感測器與硬體 API 整合**：串接 Geolocation API 獲取使用者當下座標，並導入 Web Speech API 完成 AI 導遊的語音播報功能。
  * **記帳與狀態介面**：開發記帳與分帳的視覺化面板，幫助使用者在旅途中快速檢視當前花費與帳目明細。
* **使用工具**：React 或 Vue.js, TailwindCSS / UI 元件庫, JavaScript, 瀏覽器 Web APIs。

---

## Git 版控規範 (Git Workflow)
  * 主幹分支：main (穩定版本)。

  * 開發分支：請各位從 main 開出自己的功能分支，例如 feature/mcp-toilet 或 feature/ui-timeline。

  * 合併規範：完成後發起 Pull Request (PR)，確認程式碼無衝突且可運行後再合併。