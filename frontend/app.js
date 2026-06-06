// =====================================================
// 模擬 AI 回傳的行程 JSON
// 之後 Member A / 後端 API 接好後，只要把這份假資料換成 API 回傳資料即可。
// =====================================================
const sampleItinerary = {
    tripName: "台中一日遊",
    days: [
        {
            day: 1,
            items: [
                {
                    id: 1,
                    time: "09:30",
                    location: "國立自然科學博物館",
                    city: "臺中市",
                    town: "北區",
                    description: "適合早上參觀的室內景點，可以看展覽、恐龍廳與科學互動展示。",
                    status: "pending"
                },
                {
                    id: 2,
                    time: "12:00",
                    location: "勤美誠品綠園道",
                    city: "臺中市",
                    town: "西區",
                    description: "附近有很多餐廳與咖啡廳，適合安排午餐與散步。",
                    status: "pending"
                },
                {
                    id: 3,
                    time: "15:00",
                    location: "審計新村",
                    city: "臺中市",
                    town: "西區",
                    description: "文青風格景點，有小店、甜點、拍照點，適合下午慢慢逛。",
                    status: "pending"
                },
                {
                    id: 4,
                    time: "18:30",
                    location: "逢甲夜市",
                    city: "臺中市",
                    town: "西屯區",
                    description: "晚上可以吃小吃、逛夜市，是台中很有代表性的夜間行程。",
                    status: "pending"
                }
            ]
        },
        {
            day: 2,
            items: [
                {
                    id: 5,
                    time: "10:00",
                    location: "彩虹眷村",
                    city: "臺中市",
                    town: "南屯區",
                    description: "色彩鮮明、很好拍照的景點，適合安排在第二天上午。",
                    status: "pending"
                },
                {
                    id: 6,
                    time: "13:30",
                    location: "高美濕地",
                    city: "臺中市",
                    town: "清水區",
                    description: "適合看夕陽與自然景觀，但要注意天氣和潮汐狀況。",
                    status: "pending"
                }
            ]
        }
    ]
};

let currentItinerary = null;
let currentDay = 1;
let currentLocation = null;
let expenses = [];


// =====================================================
// 送出使用者訊息
// =====================================================
function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();

    if (!text) return;

    appendMessage("user", text);
    input.value = "";

    // TODO：
    // 之後這裡可以改成 fetch() 串接 Member A / Member B 的後端 API。
    // 現階段先用假資料模擬 AI 回傳 JSON。
    setTimeout(() => {
        appendMessage("bot", "我先幫你產生一份示範行程，右邊已經渲染成行程儀表板。");

        currentItinerary = sampleItinerary;// 這裡直接用假資料，之後改成 API 回傳資料。
        currentDay = currentItinerary.days[0].day;

        renderDashboard(currentItinerary);
    }, 700);
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

            appendMessage("bot", "已取得你的目前位置，現在可以查詢附近廁所或停車場。");
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
// 目前先用 mock data，之後可改成 fetch() 串接後端。
// =====================================================
function searchNearbyToilets() {
    if (!currentLocation) {
        alert("請先取得目前位置。");
        return;
    }

    const toilets = getMockNearbyToilets();

    renderFacilities({
        toilets: toilets,
        parkingLots: []
    });

    appendMessage("bot", "已為你查詢附近廁所，結果顯示在附近設施面板。");
}


// =====================================================
// 查詢附近停車場
// 目前先用 mock data，之後可改成 fetch() 串接後端。
// =====================================================
function searchNearbyParking() {
    if (!currentLocation) {
        alert("請先取得目前位置。");
        return;
    }

    const parkingLots = getMockNearbyParking();

    renderFacilities({
        toilets: [],
        parkingLots: parkingLots
    });

    appendMessage("bot", "已為你查詢附近停車場，結果顯示在附近設施面板。");
}


// =====================================================
// 同時查詢廁所與停車場
// =====================================================
function searchAllFacilities() {
    if (!currentLocation) {
        alert("請先取得目前位置。");
        return;
    }

    const toilets = getMockNearbyToilets();
    const parkingLots = getMockNearbyParking();

    renderFacilities({
        toilets: toilets,
        parkingLots: parkingLots
    });

    appendMessage("bot", "已為你查詢附近廁所與停車場。");
}


// =====================================================
// 渲染附近設施卡片
// 已支援新版 toilet_processed.json 的 type 欄位。
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

        const toiletType = toilet.type || (toilet.accessibility ? "無障礙廁所" : "一般廁所");
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
// 模擬附近廁所資料
// 格式已改成接近 toilet_processed.json：name、address、lat、lon、type。
// =====================================================
function getMockNearbyToilets() {
    return [
        {
            name: "臺中市立圖書館總館 D棟1F 無障礙廁",
            address: "臺中市西屯區港尾里中科路2201號",
            lat: 24.192872,
            lon: 120.655102,
            type: "無障礙廁所",
            distance: 180
        },
        {
            name: "益民商圈地下停車場女廁",
            address: "臺中市北區新北里錦南街17號",
            lat: 24.153330,
            lon: 120.687046,
            type: "女廁所",
            distance: 350
        }
    ];
}


// =====================================================
// 模擬附近停車場資料
// =====================================================
function getMockNearbyParking() {
    return [
        {
            name: "市民停車場",
            distance: 220,
            availableSpaces: "尚未提供",
            address: "目前位置附近 220 公尺"
        },
        {
            name: "地下收費停車場",
            distance: 480,
            availableSpaces: "尚未提供",
            address: "目前位置附近 480 公尺"
        }
    ];
}


// =====================================================
// 新增花費
// =====================================================
function addExpense() {
    const tripNameInput = document.getElementById("expense-trip-name");
    const payerInput = document.getElementById("expense-payer");
    const amountInput = document.getElementById("expense-amount");
    const descriptionInput = document.getElementById("expense-description");
    const participantsInput = document.getElementById("expense-participants");

    const tripName = tripNameInput.value.trim();
    const payer = payerInput.value.trim();
    const amount = Number(amountInput.value);
    const description = descriptionInput.value.trim();
    const participantsText = participantsInput.value.trim();

    if (!tripName || !payer || !amount || !description || !participantsText) {
        alert("請完整輸入旅程名稱、付款人、金額、用途與分帳人員。");
        return;
    }

    if (amount <= 0) {
        alert("金額必須大於 0。");
        return;
    }

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
        tripName: tripName,
        payer: payer,
        amount: amount,
        description: description,
        participants: participants
    };

    expenses.push(expense);

    tripNameInput.value = "";
    payerInput.value = "";
    amountInput.value = "";
    descriptionInput.value = "";
    participantsInput.value = "";

    renderExpenses();
    calculateSplit();

    appendMessage("bot", `已新增一筆花費：${description}，金額 ${amount} 元。`);
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
            <p>旅程：${escapeHtml(expense.tripName)}</p>
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
// =====================================================
function deleteExpense(expenseId) {
    expenses = expenses.filter((expense) => {
        return expense.id !== expenseId;
    });

    renderExpenses();
    calculateSplit();

    appendMessage("bot", "已刪除一筆花費。");
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