// =====================================================
// API 設定
// USE_MOCK_DATA = false：正式呼叫 localhost 後端 / Agent API
// 如果後端還沒開好，可以暫時改成 true 測試畫面。
// =====================================================
const USE_MOCK_DATA = false;

// 先連 localhost。
const AGENT_API_URL = "http://127.0.0.1:8001/";

let currentItinerary = null;
let currentDay = 1;
let currentLocation = null;
let currentRoomCode = null;
let expenses = [];


// =====================================================
// 送出使用者訊息
// =====================================================
async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();

    if (!text) return;

    appendMessage("user", text);
    input.value = "";

    await sendTextToAgent(text);
}


// =====================================================
// 將文字送到 Agent API
// 所有需要透過 AI 處理的功能，都可以共用這個函式。
// =====================================================
async function sendTextToAgent(text) {
    if (USE_MOCK_DATA) {
        setTimeout(() => {
            const mockAiResponse = `
我已經幫你安排好一份台中二日遊行程，右邊會同步更新成行程儀表板。

<ITINERARY_DATA>
{
    "room_code": "TRV-DEMO",
    "tripName": "台中二日遊",
    "days": [
        {
            "day": 1,
            "items": [
                {
                    "id": 1,
                    "time": "09:30",
                    "location": "國立自然科學博物館",
                    "city": "臺中市",
                    "town": "北區",
                    "description": "適合早上參觀的室內景點。",
                    "status": "pending"
                },
                {
                    "id": 2,
                    "time": "12:00",
                    "location": "勤美誠品綠園道",
                    "city": "臺中市",
                    "town": "西區",
                    "description": "附近有很多餐廳與咖啡廳，適合安排午餐與散步。",
                    "status": "pending"
                }
            ]
        },
        {
            "day": 2,
            "items": [
                {
                    "id": 3,
                    "time": "10:00",
                    "location": "彩虹眷村",
                    "city": "臺中市",
                    "town": "南屯區",
                    "description": "色彩鮮明、很好拍照的景點。",
                    "status": "pending"
                }
            ]
        }
    ]
}
</ITINERARY_DATA>
            `;

            processAiResponse(mockAiResponse);
        }, 700);

        return;
    }

    try {
        appendMessage("bot", "正在幫你處理，請稍候...");

        const response = await fetch(AGENT_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text,
                room_code: currentRoomCode,
                latitude: currentLocation ? currentLocation.latitude : null,
                longitude: currentLocation ? currentLocation.longitude : null
            })
        });

        const responseText = await response.text();

        processAiResponse(responseText);
    } catch (error) {
        console.error("呼叫後端失敗：", error);
        appendMessage("bot", "連線後端失敗，請確認 API 是否啟動、網址是否正確，或後端是否允許 CORS。");
    }
}


// =====================================================
// 新增聊天訊息
// role 可傳入 "user" 或 "bot"
// =====================================================
function appendMessage(role, text) {
    const chatBox = document.getElementById("chat-box");

    const messageDiv = document.createElement("div");
    messageDiv.className = `msg ${role}`;
    messageDiv.textContent = text;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}


// =====================================================
// 處理 AI 回覆
// 支援兩種情況：
// 1. 後端直接回傳純文字
// 2. 後端回傳 JSON 字串，裡面可能有 reply / message / response
//
// 同時會解析：
// <ITINERARY_DATA> ... </ITINERARY_DATA>
// =====================================================
function processAiResponse(rawResponseText) {
    let responseText = rawResponseText;

    // 如果後端回傳的是 JSON 格式，先嘗試取出文字欄位
    try {
        const parsed = JSON.parse(rawResponseText);

        if (typeof parsed === "string") {
            responseText = parsed;
        } else if (parsed.reply) {
            responseText = parsed.reply;
        } else if (parsed.message) {
            responseText = parsed.message;
        } else if (parsed.response) {
            responseText = parsed.response;
        } else if (parsed.text) {
            responseText = parsed.text;
        } else {
            responseText = JSON.stringify(parsed, null, 2);
        }
    } catch (error) {
        // 不是 JSON 就維持原本純文字
    }

    extractRoomCodeFromText(responseText);

    const regex = /<ITINERARY_DATA>([\s\S]*?)<\/ITINERARY_DATA>/;
    const match = responseText.match(regex);

    let chatMessage = responseText;
    let itineraryJson = null;

    if (match && match[1]) {
        try {
            const jsonText = match[1].trim();
            itineraryJson = JSON.parse(jsonText);

            // 把隱藏 JSON 從聊天內容中移除，避免顯示在聊天框
            chatMessage = responseText.replace(regex, "").trim();
        } catch (error) {
            console.error("解析 ITINERARY_DATA JSON 失敗：", error);
            chatMessage = responseText.replace(regex, "").trim();
            chatMessage += "\n\n系統提醒：行程資料解析失敗，請確認 AI 回傳的 JSON 格式是否正確。";
        }
    }

    if (chatMessage) {
        appendMessage("bot", chatMessage);
    }

    if (itineraryJson) {
        updateItineraryFromJson(itineraryJson);
    }
}


// =====================================================
// 從文字中抓房間代碼，例如 TRV-A8K2
// =====================================================
function extractRoomCodeFromText(text) {
    const roomCodeRegex = /(TRV-[A-Z0-9]{4})/;
    const match = text.match(roomCodeRegex);

    if (match && match[1]) {
        setCurrentRoomCode(match[1]);
    }
}


// =====================================================
// 設定目前房間代碼，並更新畫面
// =====================================================
function setCurrentRoomCode(roomCode) {
    if (!roomCode) return;

    currentRoomCode = roomCode;

    const roomInfo = document.getElementById("room-info");

    if (roomInfo) {
        roomInfo.innerHTML = `
            目前房間代碼：<strong>${escapeHtml(currentRoomCode)}</strong><br>
            你可以把這個代碼分享給其他人，讓他們載入同一份行程。
        `;
    }

    const expenseRoomCodeInput = document.getElementById("expense-room-code");
    if (expenseRoomCodeInput && !expenseRoomCodeInput.value.trim()) {
        expenseRoomCodeInput.value = currentRoomCode;
    }
}


// =====================================================
// 載入房間代碼
// 這裡不直接打 MCP，而是把「我要載入房間」交給 Agent 判斷。
// =====================================================
function loadRoomByCode() {
    const input = document.getElementById("room-code-input");
    const roomCode = input.value.trim().toUpperCase();

    if (!roomCode) {
        alert("請輸入房間代碼。");
        return;
    }

    setCurrentRoomCode(roomCode);
    input.value = "";

    const message = `我要載入房間 ${roomCode}`;

    appendMessage("user", message);
    sendTextToAgent(message);
}


// =====================================================
// 用解析出來的 itinerary JSON 更新行程儀表板
// 新版後端可能只有 room_code + days，不一定有 tripName。
// =====================================================
function updateItineraryFromJson(itineraryJson) {
    if (itineraryJson.room_code) {
        setCurrentRoomCode(itineraryJson.room_code);
    }

    if (!Array.isArray(itineraryJson.days)) {
        console.error("行程 JSON 格式錯誤：", itineraryJson);
        appendMessage("bot", "系統提醒：收到的行程資料格式不完整，無法更新行程儀表板。");
        return;
    }

    if (!itineraryJson.tripName) {
        itineraryJson.tripName = currentRoomCode
            ? `房間 ${currentRoomCode} 的行程`
            : "我的旅遊行程";
    }

    itineraryJson.days.forEach((day) => {
        if (!Array.isArray(day.items)) {
            day.items = [];
        }

        day.items.forEach((item, index) => {
            if (!item.id) {
                item.id = Number(`${day.day}${index + 1}`);
            }

            if (!item.status) {
                item.status = "pending";
            }

            if (!item.description) {
                item.description = "目前沒有備註。";
            }

            if (!item.city) {
                item.city = "";
            }

            if (!item.town) {
                item.town = "";
            }

            if (!item.time) {
                item.time = "未定";
            }

            if (!item.location) {
                item.location = "未命名景點";
            }
        });
    });

    currentItinerary = itineraryJson;
    currentDay = currentItinerary.days.length > 0 ? currentItinerary.days[0].day : 1;

    renderDashboard(currentItinerary);
}


// =====================================================
// 渲染整個行程儀表板
// =====================================================
function renderDashboard(itinerary) {
    const tripTitle = document.getElementById("trip-title");
    const tripSummary = document.getElementById("trip-summary");

    tripTitle.textContent = itinerary.tripName;

    const totalDays = itinerary.days.length;
    const totalItems = itinerary.days.reduce((sum, day) => {
        return sum + day.items.length;
    }, 0);

    tripSummary.textContent = `共 ${totalDays} 天，${totalItems} 個行程景點`;

    renderDayTabs(itinerary.days);
    renderTimeline(itinerary, currentDay);
}


// =====================================================
// 渲染 Day Tabs
// =====================================================
function renderDayTabs(days) {
    const dayTabs = document.getElementById("day-tabs");
    dayTabs.innerHTML = "";

    days.forEach((dayData) => {
        const tabButton = document.createElement("button");
        tabButton.className = "day-tab";
        tabButton.textContent = `Day ${dayData.day}`;

        if (dayData.day === currentDay) {
            tabButton.classList.add("active");
        }

        tabButton.addEventListener("click", () => {
            currentDay = dayData.day;

            if (currentItinerary) {
                renderDashboard(currentItinerary);
            }
        });

        dayTabs.appendChild(tabButton);
    });
}


// =====================================================
// 渲染 Timeline
// =====================================================
function renderTimeline(itinerary, selectedDay) {
    const timeline = document.getElementById("timeline");
    timeline.innerHTML = "";

    const dayData = itinerary.days.find((day) => {
        return day.day === selectedDay;
    });

    if (!dayData || dayData.items.length === 0) {
        timeline.innerHTML = `
            <div class="empty-dashboard">
                Day ${selectedDay} 目前沒有行程。
            </div>
        `;
        return;
    }

    dayData.items.forEach((item) => {
        const timelineItem = document.createElement("div");
        timelineItem.className = "timeline-item";

        const dot = document.createElement("div");
        dot.className = "timeline-dot";

        const card = createSpotCard(item);

        timelineItem.appendChild(dot);
        timelineItem.appendChild(card);
        timeline.appendChild(timelineItem);
    });
}


// =====================================================
// 建立景點卡片
// =====================================================
function createSpotCard(item) {
    const card = document.createElement("div");
    card.className = "spot-card";

    const statusText = getStatusText(item.status);
    const statusClass = getStatusClass(item.status);

    card.innerHTML = `
        <div class="spot-top">
            <div>
                <div class="spot-time">${escapeHtml(item.time)}</div>
                <div class="spot-title">${escapeHtml(item.location)}</div>
                <div class="spot-location">${escapeHtml(item.city)}${escapeHtml(item.town)}</div>
            </div>

            <span class="status-badge ${statusClass}">
                ${statusText}
            </span>
        </div>

        <div class="spot-description">
            ${escapeHtml(item.description || "目前沒有備註。")}
        </div>

        <div class="card-actions">
            <button class="small-btn" onclick="showSpotDetail(${item.id})">查看詳情</button>
            <button class="small-btn" onclick="speakSpot(${item.id})">語音導覽</button>
        </div>
    `;

    return card;
}


// =====================================================
// 查看景點詳情
// =====================================================
function showSpotDetail(itemId) {
    const item = findItineraryItemById(itemId);

    if (!item) {
        alert("找不到這個景點資料。");
        return;
    }

    alert(
        `景點：${item.location}\n` +
        `時間：${item.time}\n` +
        `地點：${item.city}${item.town}\n` +
        `說明：${item.description}`
    );
}


// =====================================================
// Web Speech API：語音導覽
// =====================================================
function speakSpot(itemId) {
    const item = findItineraryItemById(itemId);

    if (!item) {
        alert("找不到這個景點資料。");
        return;
    }

    if (!("speechSynthesis" in window)) {
        alert("你的瀏覽器不支援語音播報功能。");
        return;
    }

    const speechText = `現在為你介紹 ${item.location}。${item.description}`;

    const utterance = new SpeechSynthesisUtterance(speechText);
    utterance.lang = "zh-TW";
    utterance.rate = 1;
    utterance.pitch = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}


// =====================================================
// 根據 id 找出某一筆行程
// =====================================================
function findItineraryItemById(itemId) {
    if (!currentItinerary) return null;

    for (const day of currentItinerary.days) {
        for (const item of day.items) {
            if (item.id === itemId) {
                return item;
            }
        }
    }

    return null;
}


// =====================================================
// 狀態文字轉換
// =====================================================
function getStatusText(status) {
    if (status === "completed") return "已完成";
    if (status === "cancelled") return "已取消";
    return "待前往";
}


// =====================================================
// 狀態 CSS class 轉換
// =====================================================
function getStatusClass(status) {
    if (status === "completed") return "status-completed";
    if (status === "cancelled") return "status-cancelled";
    return "status-pending";
}


// =====================================================
// Geolocation 定位
// =====================================================
function getCurrentLocation() {
    const locationInfo = document.getElementById("location-info");

    if (!("geolocation" in navigator)) {
        locationInfo.textContent = "你的瀏覽器不支援 Geolocation 定位功能。";
        appendMessage("bot", "你的瀏覽器不支援定位功能。");
        return;
    }

    locationInfo.textContent = "正在取得定位，請稍候...";

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            currentLocation = {
                latitude: latitude,
                longitude: longitude,
                accuracy: accuracy
            };

            locationInfo.innerHTML = `
                已取得目前位置：<br>
                緯度：${latitude.toFixed(6)}<br>
                經度：${longitude.toFixed(6)}<br>
                誤差範圍：約 ${Math.round(accuracy)} 公尺
            `;

            appendMessage("bot", "已取得你的目前位置，之後查詢附近設施時會一併送出座標。");
        },
        (error) => {
            let errorMessage = "";

            if (error.code === error.PERMISSION_DENIED) {
                errorMessage = "你拒絕了定位權限，請允許瀏覽器定位後再試一次。";
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                errorMessage = "目前無法取得位置資訊。";
            } else if (error.code === error.TIMEOUT) {
                errorMessage = "定位逾時，請再試一次。";
            } else {
                errorMessage = "定位發生未知錯誤。";
            }

            locationInfo.textContent = errorMessage;
            appendMessage("bot", errorMessage);
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}


// =====================================================
// 查詢附近廁所
// 目前走 Agent API：把需求文字和目前座標一起送給後端。
// =====================================================
function searchNearbyToilets() {
    if (!currentLocation) {
        alert("請先取得目前位置。");
        return;
    }

    appendMessage("user", "請幫我查詢目前位置附近的廁所");
    sendTextToAgent("請幫我查詢目前位置附近的廁所");
}


// =====================================================
// 查詢附近停車場
// 目前走 Agent API：把需求文字和目前座標一起送給後端。
// =====================================================
function searchNearbyParking() {
    if (!currentLocation) {
        alert("請先取得目前位置。");
        return;
    }

    appendMessage("user", "請幫我查詢目前位置附近的停車場");
    sendTextToAgent("請幫我查詢目前位置附近的停車場");
}


// =====================================================
// 同時查詢廁所與停車場
// =====================================================
function searchAllFacilities() {
    if (!currentLocation) {
        alert("請先取得目前位置。");
        return;
    }

    appendMessage("user", "請幫我查詢目前位置附近的廁所和停車場");
    sendTextToAgent("請幫我查詢目前位置附近的廁所和停車場");
}


// =====================================================
// 若後端未來回傳結構化附近設施資料，可以用此函式渲染。
// 目前保留，避免之後接 JSON 時還要重寫 UI。
// =====================================================
function renderFacilities(data) {
    const facilityResults = document.getElementById("facility-results");
    facilityResults.innerHTML = "";

    const hasToilets = data.toilets && data.toilets.length > 0;
    const hasParkingLots = data.parkingLots && data.parkingLots.length > 0;

    if (!hasToilets && !hasParkingLots) {
        facilityResults.innerHTML = `
            <div class="empty-dashboard">
                目前沒有找到附近設施。
            </div>
        `;
        return;
    }

    data.toilets.forEach((toilet) => {
        const card = document.createElement("div");
        card.className = "facility-card";

        const toiletType = toilet.type || "未設定";
        const distanceText = toilet.distance ? `距離：約 ${escapeHtml(toilet.distance)} 公尺` : "距離：等待後端回傳";

        card.innerHTML = `
            <h4>廁所｜${escapeHtml(toilet.name)}</h4>
            <p>${distanceText}</p>
            <p>類型：${escapeHtml(toiletType)}</p>
            <p>地址：${escapeHtml(toilet.address || "無地址資料")}</p>
        `;

        facilityResults.appendChild(card);
    });

    data.parkingLots.forEach((parking) => {
        const card = document.createElement("div");
        card.className = "facility-card";

        const distance = parking.distance || "未知";
        const availableSpaces = parking.availableSpaces || "尚未提供";

        card.innerHTML = `
            <h4>停車場｜${escapeHtml(parking.name)}</h4>
            <p>距離：約 ${escapeHtml(distance)} 公尺</p>
            <p>剩餘車位：${escapeHtml(availableSpaces)}</p>
            <p>地址：${escapeHtml(parking.address || "無地址資料")}</p>
        `;

        facilityResults.appendChild(card);
    });
}


// =====================================================
// 新增花費
// 目前先在前端記帳與分帳。
// 同時也把記帳句子送給 Agent，讓後端有機會存入 room_code 對應資料庫。
// =====================================================
function addExpense() {
    const roomCodeInput = document.getElementById("expense-room-code");
    const payerInput = document.getElementById("expense-payer");
    const amountInput = document.getElementById("expense-amount");
    const descriptionInput = document.getElementById("expense-description");
    const participantsInput = document.getElementById("expense-participants");

    const roomCode = currentRoomCode || roomCodeInput.value.trim().toUpperCase();
    const payer = payerInput.value.trim();
    const amount = Number(amountInput.value);
    const description = descriptionInput.value.trim();
    const participantsText = participantsInput.value.trim();

    if (!roomCode || !payer || !amount || !description || !participantsText) {
        alert("請完整輸入房間代碼、付款人、金額、用途與分帳人員。");
        return;
    }

    if (amount <= 0) {
        alert("金額必須大於 0。");
        return;
    }

    setCurrentRoomCode(roomCode);

    const participants = participantsText
        .split(",")
        .map((name) => name.trim())
        .filter((name) => name !== "");

    if (participants.length === 0) {
        alert("請至少輸入一位分帳人員。");
        return;
    }

    const expense = {
        id: Date.now(),
        roomCode: roomCode,
        payer: payer,
        amount: amount,
        description: description,
        participants: participants
    };

    expenses.push(expense);

    renderExpenses();
    calculateSplit();

    const agentMessage = `房間 ${roomCode}，剛剛 ${description} 是 ${payer} 付了 ${amount} 元，幫我跟 ${participants.join("、")} 分帳。`;

    appendMessage("user", agentMessage);
    sendTextToAgent(agentMessage);

    payerInput.value = "";
    amountInput.value = "";
    descriptionInput.value = "";
    participantsInput.value = "";
}


// =====================================================
// 渲染帳目列表
// =====================================================
function renderExpenses() {
    const expenseList = document.getElementById("expense-list");
    expenseList.innerHTML = "";

    if (expenses.length === 0) {
        expenseList.innerHTML = `
            <div class="empty-dashboard">
                目前沒有任何帳目。
            </div>
        `;
        return;
    }

    expenses.forEach((expense) => {
        const card = document.createElement("div");
        card.className = "expense-card";

        card.innerHTML = `
            <div class="expense-card-title">
                ${escapeHtml(expense.description)}
            </div>
            <p>房間：${escapeHtml(expense.roomCode)}</p>
            <p>付款人：${escapeHtml(expense.payer)}</p>
            <p>金額：${escapeHtml(expense.amount)} 元</p>
            <p>分帳人員：${escapeHtml(expense.participants.join("、"))}</p>
            <button class="small-btn danger-btn" onclick="deleteExpense(${expense.id})">刪除</button>
        `;

        expenseList.appendChild(card);
    });
}


// =====================================================
// 刪除花費
// 目前只刪前端資料。
// 若後端之後提供刪除記帳 API，再補 fetch。
// =====================================================
function deleteExpense(expenseId) {
    expenses = expenses.filter((expense) => {
        return expense.id !== expenseId;
    });

    renderExpenses();
    calculateSplit();

    appendMessage("bot", "已在前端刪除一筆花費。");
}


// =====================================================
// 計算分帳結果
// 規則：每筆花費由 participants 平分。
// payer 先付錢，所以 payer 會收到其他人應付的部分。
// =====================================================
function calculateSplit() {
    const splitResult = document.getElementById("split-result");

    if (expenses.length === 0) {
        splitResult.textContent = "分帳結果會顯示在這裡。";
        return;
    }

    const balance = {};

    expenses.forEach((expense) => {
        const eachAmount = expense.amount / expense.participants.length;

        if (!balance[expense.payer]) {
            balance[expense.payer] = 0;
        }

        balance[expense.payer] += expense.amount;

        expense.participants.forEach((person) => {
            if (!balance[person]) {
                balance[person] = 0;
            }

            balance[person] -= eachAmount;
        });
    });

    let html = "<strong>分帳結果：</strong><br>";

    Object.keys(balance).forEach((person) => {
        const money = balance[person];

        if (money > 0) {
            html += `${escapeHtml(person)} 應收 ${money.toFixed(0)} 元<br>`;
        } else if (money < 0) {
            html += `${escapeHtml(person)} 應付 ${Math.abs(money).toFixed(0)} 元<br>`;
        } else {
            html += `${escapeHtml(person)} 已平衡<br>`;
        }
    });

    splitResult.innerHTML = html;
}


// =====================================================
// 防止使用者輸入或資料內容破壞 HTML
// =====================================================
function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =====================================================
// 讓使用者按 Enter 也可以送出訊息
// =====================================================
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});