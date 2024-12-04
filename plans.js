
document.addEventListener('DOMContentLoaded', function () {
    const exerciseTable = document.getElementById('exerciseTable');
    const today = new Date();
    let currentExerciseIndex = 0;
    let exercises = [];
    let isPaused = false;
    let interval, restInterval;
    let remainingSeconds = 60;

    fetch('/get-plan-status', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (data.completed) {
                exerciseTable.innerHTML = `<div class="complete-message">今日計畫已完成！</div>`;
            } else {
                loadProfileData();
            }
        })
        .catch(error => {
            console.error('獲取用戶計劃狀態時出錯:', error);
            exerciseTable.innerHTML = `<tr><td>未能加載健身計劃，請稍後再試</td></tr>`;
        });

        document.addEventListener('DOMContentLoaded', function () {
            const addExerciseButton = document.getElementById('addExerciseButton');
            if (addExerciseButton) {
                addExerciseButton.addEventListener('click', handleAddExercise);
            } else {
                console.error('addExerciseButton 未找到，請檢查 HTML 是否包含該元素');
            }
        });
        
        
        
        
        
        
        
        
        

    // 加載使用者資料，判斷 BMI 與 WHR
function loadProfileData() {
    const dayOfWeekEnglish = today.toLocaleString('en-US', { weekday: 'long' });
    const dayOfWeekMap = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日'
    };
    const dayOfWeek = dayOfWeekMap[dayOfWeekEnglish];

    fetch('/get-profile-data')
        .then(response => response.json())
        .then(data => {
            const { height, weight_today: weight, waist, hip } = data;

            if (!height || !weight || !waist || !hip) {
                exerciseTable.innerHTML = `<tr><td>請到個人頁面輸入完整的今日數據（包含腰圍與臀圍）</td></tr>`;
            } else {
                const bodyType = calculateBodyType(height, weight, waist, hip);
                loadExercisePlan(bodyType, dayOfWeek);
            }
        })
        .catch(error => {
            console.error("獲取使用者資料時發生錯誤:", error);
            exerciseTable.innerHTML = `<tr><td>無法加載健身計畫，請稍後再試。</td></tr>`;
        });
}

// 計算 BMI 和 WHR 來判斷體型
function calculateBodyType(height, weight, waist, hip) {
    const bmi = weight / ((height / 100) ** 2);
    const whr = waist / hip;

    if (bmi < 18.5 && whr < 0.9) {
        return 'thin'; // 過輕計畫
    } else if (bmi >= 18.5 && bmi <= 25 && whr < 0.9) {
        return 'average'; // 適中計畫
    } else if (bmi > 25 || whr > 0.9) {
        return 'overweight'; // 過重計畫
    } else {
        console.warn("BMI 與 WHR 的組合無法識別，預設為適中計畫。");
        return 'average';
    }
}


    // 加載對應的健身計劃
    function loadExercisePlan(bodyType, dayOfWeek) {
        console.log(`加載健身計劃，Body Type: ${bodyType}, Day of Week: ${dayOfWeek}`);
        const fitnessPlans = {
            thin: {
                星期一: [
                    { exercise: '俯臥撐', image: '俯臥撐.png' ,video: '登山跑.mp4'},
                    { exercise: '仰臥起坐', image: '仰臥起坐.png' ,video: '臀橋.mp4'},
                    { exercise: '登山跑', image: '登山跑.png' ,video: '深蹲.mp4'}
                ],
                星期二: [
                    { exercise: '深蹲', image: '深蹲.png', video: '深蹲.mp4' },
                    { exercise: '跳躍深蹲', image: '跳躍深蹲.png' ,video: '跳躍深蹲.mp4'},
                    { exercise: '臀橋', image: '臀橋.png' ,video: '臀橋.mp4'}
                ],
                星期三: [
                    { exercise: '平板支撐', image: '平板支撐.png' ,video: '平板支撐.mp4'},
                    { exercise: '高抬腿', image: '高抬腿.png' ,video: '登山跑.mp4'},
                    { exercise: '仰臥自行車', image: '仰臥自行車.png' ,video: '深蹲.mp4'}
                ],
                星期四: [
                    { exercise: '弓步蹲', image: '弓箭步.png' ,video: '登山跑.mp4'},
                    { exercise: '單腳硬拉', image: '單腳硬拉.png' ,video: '波比跳.mp4'},
                    { exercise: '跳躍深蹲', image: '跳躍深蹲.png' ,video: '跳躍深蹲.mp4'}
                ],
                星期五: [
                    { exercise: '波比跳', image: '波比跳.png' ,video: '波比跳.mp4'},
                    { exercise: '臀橋', image: '臀橋.png' ,video: '臀橋.mp4'},
                    { exercise: '跳躍深蹲', image: '跳躍深蹲.png' ,video: '跳躍深蹲.mp4'}
                ],
                星期六: [
                    { exercise: '開合跳', image: '開合跳.png' ,video: '登山跑.mp4'},
                    { exercise: '仰臥腿舉', image: '仰臥腿舉.png' ,video: '深蹲.mp4'},
                    { exercise: '臀橋', image: '臀橋.png' ,video: '臀橋.mp4'}
                ],
                星期日: [
                    { exercise: '休息日：放鬆並進行輕度伸展', image: null }
                ]
            },
            average: {
                星期一: [
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' ,video: '登山跑.mp4'},
                    { exercise: '俯臥撐', image: '俯臥撐.png' ,video: '登山跑.mp4'},
                    { exercise: '跳繩', image: '跳繩.png' ,video: '登山跑.mp4'}
                ],
                星期二: [
                    { exercise: '波比跳', image: '波比跳.png' , video: '波比跳.mp4'},
                    { exercise: '俯臥撐', image: '俯臥撐.png' , video: '俯臥撐.mp4'},
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' , video: '凳上臂屈伸.mp4'}
                ],
                星期三: [
                    { exercise: '高抬腿', image: '高抬腿.png' ,video: '登山跑.mp4'},
                    { exercise: '深蹲', image: '深蹲.png' ,video: '登山跑.mp4'},
                    { exercise: '俯臥撐', image: '俯臥撐.png' ,video: '登山跑.mp4'}
                ],
                星期四: [
                    { exercise: '俯臥撐', image: '俯臥撐.png' ,video: '登山跑.mp4'},
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' ,video: '登山跑.mp4'},
                    { exercise: '仰臥自行車', image: '仰臥自行車.png' ,video: '登山跑.mp4'}
                ],
                星期五: [
                    { exercise: '登山跑', image: '登山跑.png' ,video: '登山跑.mp4'},
                    { exercise: '俯臥撐', image: '俯臥撐.png' ,video: '俯臥撐.mp4'},
                    { exercise: '平板支撐', image: '平板支撐.png' ,video: '平板支撐.mp4'}
                ],
                星期六: [
                    { exercise: '高抬腿', image: '高抬腿.png' ,video: '登山跑.mp4'},
                    { exercise: '開合跳', image: '開合跳.png' ,video: '登山跑.mp4'},
                    { exercise: '肩膀挺舉', image: '肩膀挺舉.png' ,video: '登山跑.mp4'}
                ],
                星期日: [
                    { exercise: '休息日：放鬆並進行輕度伸展', image: null }
                ]
            },
            overweight: {
                星期一: [
                    { exercise: '步行', image: '步行.png' },
                    { exercise: '牽拉運動', image: '牽拉運動.png' },
                    { exercise: '高抬腿', image: '高抬腿.png' }
                ],
                星期二: [
                    { exercise: '靠牆深蹲', image: '深蹲.png' , video: '深蹲.mp4'},
                    { exercise: '臀橋', image: '臀橋.png' , video: '臀橋.mp4'},
                    { exercise: '波比跳', image: '波比跳.png' , video: '波比跳.mp4'}
                ],
                星期三: [
                    { exercise: '登山跑', image: '登山跑.png' ,video: '登山跑.mp4'},
                    { exercise: '深蹲', image: '深蹲.png' ,video: '登山跑.mp4'},
                    { exercise: '側步蹲', image: '側步蹲.png' ,video: '登山跑.mp4'}
                ],
                星期四: [
                    { exercise: '跪姿俯臥撐', image: '俯臥撐.png' ,video: '俯臥撐.mp4'},
                    { exercise: '平板支撐', image: '平板支撐.png' ,video: '平板支撐.mp4'},
                    { exercise: '臀橋', image: '臀橋.png' ,video: '臀橋.mp4'}
                ],
                星期五: [
                    { exercise: '深蹲', image: '深蹲.png' ,video: '深蹲.mp4'},
                    { exercise: '登山跑', image: '登山跑.png' ,video: '登山跑.mp4'},
                    { exercise: '開合跳', image: '開合跳.png' ,video: '開合跳.mp4'}
                ],
                星期六: [
                    { exercise: '登山跑', image: '登山跑.png' ,video: '登山跑.mp4'},
                    { exercise: '跳繩', image: '跳繩.png' ,video: '登山跑.mp4'},
                    { exercise: '側棒式支撐', image: '側棒式支撐.png' ,video: '登山跑.mp4'}
                ],
                星期日: [
                    { exercise: '休息日：放鬆並進行輕度伸展', image: null }
                ]
            }
        };

        const todayExercises = fitnessPlans[bodyType]?.[dayOfWeek];

        if (dayOfWeek === '星期日') {
            // 如果是星期天，顯示休息日
            exerciseTable.innerHTML = `
                <tr>
                    <th>日期</th>
                    <th>訓練計畫</th>
                </tr>
                <tr>
                    <td>${dayOfWeek}</td>
                    <td>休息日：放鬆並進行輕度伸展</td>
                </tr>`;
            return;  // 不繼續執行後續的邏輯
        }
        if (todayExercises) {
            exercises = [...todayExercises]; // 初始化 exercises
            displayExercise(todayExercises[0], dayOfWeek);
        } else {
            console.error("未找到相應的健身計劃。");
            exerciseTable.innerHTML = `<tr><td>未找到適合的健身計劃</td></tr>`;
        }
    }

    // 顯示當天的動作並添加計時功能
    function displayExercise(exerciseObj, dayOfWeek) {
        const exerciseTable = document.getElementById('exerciseTable');
        exerciseTable.innerHTML = `
            <tr>
                <th>日期</th>
                <th>訓練計畫</th>
            </tr>
            <tr>
                <td>${dayOfWeek}</td>
                <td>
                    <div class="exercise-container" style="text-align: center;">
                        <h3 id="exerciseName">${exerciseObj.exercise}</h3>
                        <video id="exerciseVideo" controls width="600">
                            <source src="/static/videos/${exerciseObj.video}" type="video/mp4">
                            您的瀏覽器不支援此影片。
                        </video>
                        <div id="timerDisplay-${dayOfWeek}" class="timer-display">00:00</div>
                    </div>
                </td>
            </tr>
        `;
    
    
        
        const startButton = document.createElement('button');
        startButton.id = `startTimer-${dayOfWeek}`;
        startButton.classList.add('start-timer');
        startButton.textContent = '開始計時';
        exerciseTable.appendChild(startButton);

        const pauseButton = document.createElement('button');
        pauseButton.id = "pauseButton";
        pauseButton.textContent = '暫停';
        pauseButton.classList.add('start-timer');  // 使樣式與開始計時按鈕一致
        pauseButton.style.display = 'none';  // 初始隱藏
        exerciseTable.appendChild(pauseButton);

        startButton.addEventListener('click', function () {
            startButton.style.display = 'none';  // 隱藏開始按鈕
            pauseButton.style.display = 'inline';  // 顯示暫停按鈕
            startCountdown(dayOfWeek);
        });

        pauseButton.addEventListener('click', function () {
            const video = document.getElementById("exerciseVideo");
            if (isPaused) {
                pauseButton.textContent = '暫停';  // 設置為暫停
                video.play();  // 繼續播放影片
                startTimer(dayOfWeek, remainingSeconds);  // 繼續計時
            } else {
                pauseButton.textContent = '繼續';  // 改為繼續
                video.pause();  // 暫停影片
                clearInterval(interval);  // 暫停計時
            }
            isPaused = !isPaused;  // 切換狀態
        });
    }

    // 倒數計時
    function startCountdown(dayOfWeek) {
        let countdown = 3;
        const display = document.getElementById(`timerDisplay-${dayOfWeek}`);
        display.textContent = `即將開始: ${countdown}秒`;

        const countdownInterval = setInterval(() => {
            countdown--;
            display.textContent = `即將開始: ${countdown}秒`;

            if (countdown === 0) {
                clearInterval(countdownInterval);
                remainingSeconds = 60;  // 倒數結束後設置剩餘時間為 60 秒
                startTimer(dayOfWeek, remainingSeconds);  // 開始1分鐘計時
            }
        }, 1000);
    }


    // 主要計時與影片同步功能
    function startTimer(dayOfWeek, seconds) {
        const display = document.getElementById(`timerDisplay-${dayOfWeek}`);
        const video = document.getElementById("exerciseVideo");
    
        video.play();  // 播放影片
        display.textContent = `剩餘時間: ${seconds}秒`;
    
        interval = setInterval(() => {
            seconds--;
            remainingSeconds = seconds;  // 保存剩餘時間
            display.textContent = `剩餘時間: ${seconds}秒`;
    
            if (seconds <= 0) {  // 計時結束
                clearInterval(interval);  // 停止計時器
                remainingSeconds = 60;  // 重設剩餘時間為 60
                video.pause();  // 暫停影片
                startRestTimer(dayOfWeek);  // 開始休息倒數並進入下一個動作
            }
        }, 1000);
    }
    



    // 休息時間倒數並顯示下一個動作
    function startRestTimer(dayOfWeek) {
        currentExerciseIndex++;
    
        if (currentExerciseIndex < exercises.length) {
            const nextExerciseObj = exercises[currentExerciseIndex];  // 獲取下一個動作
    
            // 隱藏暫停按鈕
            const pauseButton = document.getElementById('pauseButton');
            pauseButton.style.display = 'none';  // 在休息期間隱藏暫停按鈕
    
            // 顯示休息提示和下一個動作名稱
            let restSeconds = 30;
            const display = document.getElementById(`timerDisplay-${dayOfWeek}`);
            display.textContent = `休息 ${restSeconds} 秒 - 下一個動作為：${nextExerciseObj.exercise}`;
    
            restInterval = setInterval(() => {
                restSeconds--;
                display.textContent = `休息 ${restSeconds} 秒 - 下一個動作為：${nextExerciseObj.exercise}`;
    
                if (restSeconds <= 0) {
                    clearInterval(restInterval);
                    pauseButton.style.display = 'inline';  // 顯示暫停按鈕
    
                    // 更新動作名稱
                    const exerciseName = document.getElementById('exerciseName');
                    exerciseName.textContent = nextExerciseObj.exercise;
    
                    // 更新影片
                    const video = document.getElementById('exerciseVideo');
                    const videoSource = video.querySelector('source'); // 找到 <video> 裡的 <source>
                    if (videoSource) {
                        videoSource.src = `/static/videos/${nextExerciseObj.video}`;
                        video.load();  // 加載新影片
                    } else {
                        console.error("未找到 <source> 元素，無法更新影片");
                    }
    
                    // 開始下一個動作的計時
                    startTimer(dayOfWeek, 60);  // 開始下一個動作的計時，從 60 秒開始
                }
            }, 1000);
        } else {
            completeWorkout();  // 所有動作完成後的處理
        }
    }
    
    
    
    





    // 計劃完成後的處理
    function completeWorkout() {
        exerciseTable.innerHTML = `<div class="complete-message">今日計畫已完成！</div>`;

        // 更新後端的完成狀態
        fetch('/complete-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ completed: true }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('計劃狀態已更新至後端。');
            }
        })
        .catch(error => {
            console.error('更新計劃狀態時出錯:', error);
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById("exerciseChart");

    if (!chartCanvas) {
        console.error("Canvas element with ID #exerciseChart not found.");
        return;
    }

    const ctx = chartCanvas.getContext("2d");

    // 向後端請求數據
    fetch("/get-exercise-stats")
    .then(response => {
        if (!response.ok) throw new Error("後端回傳錯誤");
        return response.json();
    })
    .then(data => {
        if (!data.stats || !Array.isArray(data.stats)) {
            throw new Error("返回的數據格式不正確");
        }

        // 翻譯動作名稱
        const translations = {
            "pushup": "伏地挺身",
            "squat": "深蹲",
            "plank": "平板支撐"
        };

        // 獲取所有日期和動作
        const labels = [...new Set(data.stats.map(stat => stat.date))];
        const exercises = [...new Set(data.stats.map(stat => translations[stat.exercise_name] || stat.exercise_name))];

        // 為每個動作生成數據集
        const datasets = exercises.map(exercise => {
            return {
                label: exercise,
                data: labels.map(date => {
                    const stat = data.stats.find(s => s.date === date && translations[s.exercise_name] === exercise);
                    return stat ? stat.total_reps : 0;
                }),
                borderColor: getRandomColor(),
                tension: 0.2, // 平滑折線
                fill: false,
            };
        });

        // 初始化圖表
        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            color: "#333", // 圖例文字顏色
                        }
                    },
                    title: {
                        display: true,
                        text: "訓練量圖表",
                        color: "#333", // 標題文字顏色
                        font: {
                            size: 18, // 標題字體大小
                            weight: "bold" // 標題字體加粗
                        },
                        padding: {
                            top: 10, // 調整與上方的距離
                            bottom: 10 // 調整與圖表的距離
                        },
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "日期",
                            color: "#333", // X軸標題文字顏色
                        },
                        ticks: {
                            color: "#333", // X軸標籤文字顏色
                        },
                        grid: {
                            color: "#e0e0e0" // X軸網格線顏色
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "訓練量",
                            color: "#333", // Y軸標題文字顏色
                        },
                        ticks: {
                            color: "#333", // Y軸標籤文字顏色
                        },
                        grid: {
                            color: "#e0e0e0" // Y軸網格線顏色
                        }
                    }
                }
            }
        });
        
    })
    .catch(error => console.error("加載訓練數據時出錯:", error));

// 隨機顏色生成器
function getRandomColor() {
    return `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.8)`;
}

    
    // 初始化事件監聽器與功能
    initEventListeners();
    fetchAndRenderExercises();

    /**
     * 初始化事件監聽器
     */
    function initEventListeners() {
        if (addExerciseButton) {
            addExerciseButton.addEventListener('click', handleAddExercise);
        }

        const completePlanButton = document.getElementById('completePlanButton');
        if (completePlanButton) {
            completePlanButton.addEventListener('click', handleCompletePlan);
        }

        const queryButton = document.getElementById('queryButton');
        if (queryButton) {
            queryButton.addEventListener('click', handleQueryExercises);
        }
    }

    /**
     * 新增動作到清單
     */
    function handleAddExercise() {
        const exerciseSelect = document.getElementById('exerciseSelect');
        const setsInput = document.getElementById('setsInput');
        const repsInput = document.getElementById('repsInput');
    
        const exerciseName = exerciseSelect.value;
        const sets = parseInt(setsInput.value, 10);
        const reps = parseInt(repsInput.value, 10);
    
        if (!exerciseName || isNaN(sets) || isNaN(reps) || sets <= 0 || reps <= 0) {
            alert('請輸入有效的動作、組數和次數');
            return;
        }
    
        fetch('/add-exercise', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ exercise_name: exerciseName, sets, reps }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('動作新增成功');
                    fetchAndRenderExercises();
                } else {
                    alert(`新增失敗: ${data.error || '未知錯誤'}`);
                }
            })
            .catch(error => console.error('新增動作時發生錯誤:', error));
    }

    /**
     * 從後端獲取資料並渲染表格和圖表
     */
    function fetchAndRenderExercises() {
        fetch('/get-exercises')
            .then(response => response.json())
            .then(data => {
                if (data.exercises) {
                    renderExerciseTable(data.exercises);
                } else {
                    console.error('無法獲取動作列表:', data.error || '未知錯誤');
                }
            })
            .catch(error => console.error('獲取動作列表時發生錯誤:', error));
    }

    /**
     * 渲染動作表格
     */
    function renderExerciseTable(exercises) {
        const table = document.getElementById('recordedExerciseTable');
        table.innerHTML = `
            <tr>
                <th>動作</th>
                <th>組數</th>
                <th>次數</th>
                <th>操作</th>
            </tr>`;
        
        exercises.forEach(exercise => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${exercise.exercise_name}</td>
                <td>${exercise.sets}</td>
                <td>${exercise.reps}</td>
                <td>
                    <button class="delete-btn" data-id="${exercise.id}">刪除</button>
                </td>`;
            table.appendChild(row);
        });
    
        // 綁定刪除按鈕事件
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', () => {
                const exerciseId = button.dataset.id;
                handleDeleteExercise(exerciseId);
            });
        });
    }

    /**
     * 刪除動作
     */
    function handleDeleteExercise(exerciseId) {
        fetch(`/delete-exercise/${exerciseId}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('刪除成功');
                    fetchAndRenderExercises();
                } else {
                    alert('刪除失敗');
                }
            })
            .catch(error => console.error('刪除動作時發生錯誤:', error));
    }

    /**
     * 完成計劃
     */
    function handleCompletePlan() {
        fetch('/complete-exercises', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('訓練完成！');
                    updateMultiDayChart(data.chartData);
                    fetchAndRenderExercises();
                } else {
                    alert(`操作失敗：${data.error}`);
                }
            })
            .catch(error => console.error('操作失敗:', error));
    }

    /**
     * 查詢動作數據
     */
    function handleQueryExercises() {
        const queryDate = document.getElementById('queryDate').value;
        if (!queryDate) {
            console.error('請選擇日期');
            return;
        }

        fetch('/query-exercises', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date: queryDate }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.exercises) {
                    renderExerciseTable(data.exercises);
                    updateMultiDayChart(data);
                } else {
                    console.warn('查詢結果中沒有數據');
                }
            })
            .catch(error => console.error('查詢資料時發生錯誤:', error));
    }

    /**
     * 更新折線圖
     */
    function updateMultiDayChart(data) {
        const chartCanvas = document.getElementById('exerciseLineChart');
        const ctx = chartCanvas.getContext('2d');

        if (exerciseChart) {
            exerciseChart.destroy();
        }

        data.datasets.forEach(dataset => {
            dataset.label = translateExerciseName(dataset.label);
        });

        exerciseChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: '日期' },
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: '總訓練量（次數）' },
                    },
                },
                plugins: {
                    legend: { position: 'top' },
                },
            },
        });
    }

    /**
     * 翻譯動作名稱
     */
    function translateExerciseName(name) {
        const translations = {
            "pushup": "伏地挺身",
            "plank": "平板支撐",
            "squat": "深蹲",
        };
        return translations[name] || name;
    }
});


