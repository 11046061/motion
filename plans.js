
document.addEventListener('DOMContentLoaded', function () {
    const exerciseTable = document.getElementById('exerciseTable');
    const today = new Date();
    let currentExerciseIndex = 0;
    let exercises = [];
    let isPaused = false;
    let interval, restInterval;
    let remainingSeconds = 60;
    

// 加載對應的健身計劃
    window.loadExercisePlan = function (bodyType, dayOfWeek) {
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
                    { exercise: '步行', image: '步行.png' ,video: '深蹲.mp4'},
                    { exercise: '牽拉運動', image: '牽拉運動.png' ,video: '俯臥撐.mp4'},
                    { exercise: '高抬腿', image: '高抬腿.png' ,video: '平板支撐.mp4'}
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
            },
            thin_high_whr: {
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
                    { exercise: '高抬腿', image: '高抬腿.png' ,video: '波比跳.mp4'},
                    { exercise: '深蹲', image: '深蹲.png' ,video: '波比跳.mp4'},
                    { exercise: '俯臥撐', image: '俯臥撐.png' ,video: '波比跳.mp4'}
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
            average_high_whr: {
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


    
        // 檢查計畫狀態
    function checkPlanStatus() {
        fetch('/get-plan-status')
            .then(response => response.json())
            .then(data => {
                if (data.completed) {
                    exerciseTable.innerHTML = `<div class="complete-message">今日計畫已完成！</div>`;
                } else {
                    loadProfileData(); // 加載動作清單
                }
            })
            .catch(error => {
                console.error('獲取計畫狀態失敗:', error);
                exerciseTable.innerHTML = `<tr><td>無法加載健身計畫，請稍後重試。</td></tr>`;
            });
    }

    // 初始化檢查
    checkPlanStatus();
        
        
        
        
        
        
        
        

// 確保在加載用戶數據時，函數已正確引用
function loadProfileData() {
    const dayOfWeekEnglish = today.toLocaleString('en-US', { weekday: 'long' });
    const dayOfWeekMap = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日',
    };
    const dayOfWeek = dayOfWeekMap[dayOfWeekEnglish];

    fetch('/get-profile-data')
        .then(response => response.json())
        .then(data => {
            const { height, weight_today: weight, waist, hip } = data;
            if (!height || !weight || !waist || !hip) {
                exerciseTable.innerHTML = `<tr><td>請到個人頁面輸入完整數據</td></tr>`;
            } else {
                const bodyType = calculateBodyType(height, weight, waist, hip);
                loadExercisePlan(bodyType, dayOfWeek); // 在獲取最新數據後，更新推薦清單
            }
        })
        .catch(error => {
            console.error("獲取用戶數據時發生錯誤:", error);
        });
}


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

        
    // 計算 BMI 和 WHR 來判斷體型
    function calculateBodyType(height, weight, waist, hip) {
        const bmi = weight / ((height / 100) ** 2);
        const whr = waist / hip;
    
        if (bmi < 18.5) {
            if (whr > 0.9) {
                return 'thin_high_whr'; // 過輕但 WHR 高
            }
            return 'thin'; // 過輕
        } else if (bmi >= 18.5 && bmi <= 25) {
            if (whr > 0.9) {
                return 'average_high_whr'; // 適中但 WHR 高
            }
            return 'average'; // 適中
        } else if (bmi > 25 || whr > 0.9) {
            return 'overweight'; // 過重
        }
        return 'average'; // 預設為適中
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
                        <video id="exerciseVideo" controls loop width="600">
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
            const nextExerciseObj = exercises[currentExerciseIndex]; // 獲取下一個動作
    
            // 隱藏暫停按鈕
            const pauseButton = document.getElementById('pauseButton');
            pauseButton.style.display = 'none'; // 在休息期間隱藏暫停按鈕
    
            // 顯示休息提示和下一個動作名稱
            let restSeconds = 30;
            const display = document.getElementById(`timerDisplay-${dayOfWeek}`);
            display.textContent = `休息 ${restSeconds} 秒 - 下一個動作為：${nextExerciseObj.exercise}`;
    
            const restInterval = setInterval(() => {
                restSeconds--;
                display.textContent = `休息 ${restSeconds} 秒 - 下一個動作為：${nextExerciseObj.exercise}`;
    
                if (restSeconds <= 0) {
                    clearInterval(restInterval);
    
                    // 更新動作名稱
                    const exerciseName = document.getElementById('exerciseName');
                    exerciseName.textContent = nextExerciseObj.exercise;
    
                    // 更新影片
                    const video = document.getElementById('exerciseVideo');
                    const videoSource = video.querySelector('source');
    
                    if (videoSource) {
                        videoSource.src = `/static/videos/${nextExerciseObj.video}`; // 更新影片路徑
                        video.load(); // 加載新影片
    
                        // 確保影片加載完成後自動播放
                        video.onloadeddata = function () {
                            video.play();
                        };
                    } else {
                        console.error("未找到 <source> 元素，無法更新影片");
                    }
    
                    // 顯示暫停按鈕
                    pauseButton.style.display = 'inline';
    
                    // 開始下一個動作的計時
                    startTimer(dayOfWeek, 60); // 下一個動作計時從 60 秒開始
                }
            }, 1000);
        } else {
            completeWorkout(); // 所有動作完成後的處理
        }
    }
    
    
    
    
    
    





    // 計劃完成後的處理
    function completeWorkout() {
        exerciseTable.innerHTML = `<div class="complete-message">今日計畫已完成！</div>`;
    
        fetch('/complete-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ completed: true }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                console.log('計劃狀態已更新至後端。');
            } else if (data.status === 'already_completed') {
                console.log('計劃已經完成。');
            } else {
                console.error('未知錯誤:', data.error);
            }
        })
        .catch(error => {
            console.error('更新計劃狀態時出錯:', error);
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const exerciseSelect = document.getElementById('exerciseSelect');
    const chartCanvas = document.getElementById("exerciseChart");
    


    if (!chartCanvas) {
        console.error("Canvas element with ID #exerciseChart not found.");
        return;
    }

    const ctx = chartCanvas.getContext("2d");

    // 確保函式已定義在全域作用域
    fetch('/get-today-exercises')
        .then(response => response.json())
        .then(data => {
            if (data.exercises) {
                const { bodyType, dayOfWeek } = data;
                loadExercisePlan(bodyType, dayOfWeek); // 確保此時 loadExercisePlan 可用
            } else {
                console.error("無法獲取每日推薦清單:", data.error || "未知錯誤");
            }
        })
        .catch(error => console.error("獲取每日推薦清單時出錯:", error));



    // 向後端請求統計數據
    fetch('/get-exercise-stats')
        .then(response => response.json())
        .then(data => {
            if (!data.stats || !Array.isArray(data.stats)) {
                console.error("返回的數據格式不正確:", data);
                throw new Error("數據格式錯誤或為空");
            }

            const formattedData = formatExerciseStats(data.stats);
            if (!formattedData.labels || !formattedData.datasets) {
                console.error("格式化後的數據有誤:", formattedData);
                throw new Error("格式化後數據錯誤");
            }

            updateMultiDayChart(formattedData);
        })
    .catch(error => console.error("加載訓練數據時出錯:", error));
});

        

    // 隨機顏色生成器
    function getRandomColor() {
        return `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.8)`;
    }

    /**
     * 更新每日推薦清單的選項
     */
    function updateExerciseSelectOptions(exercises) {
        exerciseSelect.innerHTML = ''; // 清空舊的選項
        exercises.forEach(exercise => {
            const option = document.createElement('option');
            option.value = exercise.exercise_name;
            option.textContent = exercise.exercise_name;
            exerciseSelect.appendChild(option);
        });
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
        // 嘗試獲取元素
        const exerciseNameInput = document.getElementById('exerciseNameInput');
        const setsInput = document.getElementById('setsInput');
        const repsInput = document.getElementById('repsInput');
    
        // 檢查所有元素是否正確加載
        if (!exerciseNameInput || !setsInput || !repsInput) {
            console.error('表單元素未找到，請檢查 HTML 結構是否正確');
            Swal.fire('錯誤', '無法找到表單元素，請檢查頁面結構', 'error');
            return;
        }
    
        // 獲取輸入值
        const exerciseName = exerciseNameInput.value.trim();
        const sets = parseInt(setsInput.value, 10);
        const reps = parseInt(repsInput.value, 10);
    
        // 驗證輸入值
        if (!exerciseName || isNaN(sets) || isNaN(reps) || sets <= 0 || reps <= 0) {
            Swal.fire('錯誤', '請填寫有效的動作名稱、組數和次數', 'error');
            return;
        }
    
        // 前端計算每個動作的卡路里消耗
        const calorieData = {
            pushup: 5,
            squat: 6,
            plank: 4,
            burpee: 10,
            mountain_climber: 8,
            jumping_jack: 7,
            jump_squat: 9
        };
        const caloriesBurned = sets * reps * (calorieData[exerciseName] || 0);
    
        // 發送請求到後端
        fetch('/add-exercise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                exercise_name: exerciseName,
                sets: sets,
                reps: reps,
                calories: caloriesBurned // 將卡路里消耗發送到後端
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('動作已成功新增');
                fetchAndRenderExercises(); // 更新表格和多日圖表
                fetchAndRenderDailyCalorieChart(); // 更新每日卡路里圖表
            } else {
                alert('新增失敗');
            }
        })
        
        .catch(error => {
            Swal.fire('錯誤', '無法新增動作，請稍後再試', 'error');
            console.error('新增動作時發生錯誤:', error);
        });
    }
    
    
    // 綁定按鈕事件
    document.addEventListener('DOMContentLoaded', function () {
        const addExerciseButton = document.getElementById('addExerciseButton');
        if (addExerciseButton) {
            addExerciseButton.addEventListener('click', handleAddExercise);
        } else {
            console.error('新增動作按鈕未找到，請檢查 HTML 結構');
        }
    });
    
    

    /**
     * 從後端獲取資料並渲染表格和圖表
     */
    function fetchAndRenderExercises() {
        const chartCanvas = document.getElementById('exerciseChart'); // 修改 ID 為 exerciseChart
        if (!chartCanvas) {
            console.error('找不到圖表元素，請檢查 HTML 結構是否正確。');
            return;
        }
    
        const ctx = chartCanvas.getContext('2d'); // 獲取上下文
    
        fetch('/get-exercises') // 從後端獲取當日動作
        .then(response => response.json())
        .then(data => {
            if (!data.exercises || data.exercises.length === 0) {
                console.warn('無法獲取當日動作或數據為空，顯示空白表格');
                renderExerciseTable([]); // 清空表格
                return;
            }

            renderExerciseTable(data.exercises); // 渲染表格
        })
        .catch(error => {
            console.error('獲取當日動作列表時發生錯誤:', error);
            renderExerciseTable([]); // 清空表格
        });
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
                <td>${translateExerciseName(exercise.exercise_name)}</td>
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
                    fetchAndRenderExercises(); // 更新表格和多日圖表
                    fetchAndRenderDailyCalorieChart(); // 更新每日卡路里圖表
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

    
    function translateExerciseName(name) {
        const translations = {
            pushup: '伏地挺身',
            squat: '深蹲',
            plank: '平板支撐',
            burpee: '波比跳',
            mountain_climber: '登山跑',
            jumping_jack: '開合跳',
            jump_squat: '跳躍深蹲',
            // 可以在此添加其他動作名稱
        };
        return translations[name] || name; // 如果找不到翻譯，返回原名稱
    }
    
    function updateMultiDayChart(data) {
        if (!data.labels || !data.datasets) {
            console.error("圖表數據格式錯誤: labels 或 datasets 為空", data);
            return;
        }
    
        const chartCanvas = document.getElementById("exerciseChart");
        if (!chartCanvas || !(chartCanvas instanceof HTMLCanvasElement)) {
            console.error("找不到圖表元素");
            return;
        }
        
        const ctx = chartCanvas.getContext("2d");
    
        // 銷毀舊圖表（如果存在）
        if (window.exerciseChart instanceof Chart) {
            try {
                window.exerciseChart.destroy();
            } catch (error) {
                console.error("銷毀圖表時發生錯誤:", error);
            }
        }
    
        // 更新 datasets 的標籤為中文
        const translatedDatasets = data.datasets.map(dataset => ({
            ...dataset,
            label: translateExerciseName(dataset.label), // 將標籤翻譯成中文
        }));
    
        console.log("更新圖表的數據:", data);
        // 確保 datasets 和 labels 正確映射
    window.exerciseChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: data.datasets.map(dataset => ({
                label: translateExerciseName(dataset.label),
                data: dataset.data || [], // 防止數據為 undefined
                borderColor: dataset.borderColor || getRandomColor(),
                tension: 0.4,
            }))
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: "日期" } },
                y: { title: { display: true, text: "總訓練量（次數）" }, beginAtZero: true }
            }
            },
        });
    }
    
    
    
    
    
    
    
    
    
    
    
    function formatExerciseStats(stats) {
        const labels = [...new Set(stats.map(stat => stat.date))];
        const exercises = [...new Set(stats.map(stat => stat.exercise_name))];
    
        const datasets = exercises.map(exercise => ({
            label: exercise,
            data: labels.map(date => {
                const stat = stats.find(s => s.date === date && s.exercise_name === exercise);
                return stat ? stat.total_reps : 0;
            }),
            borderColor: getRandomColor(),
            tension: 0.4,
        }));
    
        return { labels, datasets };
    }
    
      
    // 頁面加載時自動調用
    document.addEventListener('DOMContentLoaded', fetchAndRenderDailyCalorieChart);
      
    
    window.dailyCalorieChart = null;
    function fetchAndRenderDailyCalorieChart() {
        const dailyCalorieChartCanvas = document.getElementById('dailyCalorieChart');
        if (!dailyCalorieChartCanvas) {
            console.error('未找到每日卡路里圖表的 Canvas 元素');
            return;
        }
    
        const ctx = dailyCalorieChartCanvas.getContext('2d');
    
        // 銷毀舊圖表（如果存在）
        if (window.dailyCalorieChart && typeof window.dailyCalorieChart.destroy === 'function') {
            try {
                window.dailyCalorieChart.destroy();
            } catch (error) {
                console.error('銷毀舊圖表時發生錯誤:', error);
            }
        }
    
        fetch('/get-daily-calorie-summary')
            .then(response => response.json())
            .then(data => {
                if (!data.dates || !data.calories || data.dates.length === 0) {
                    console.warn("每日卡路里數據為空，顯示空圖表");
                    data.dates = ["無記錄"];
                    data.calories = [0];
                }
    
                // 初始化新圖表
                window.dailyCalorieChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.dates,
                        datasets: [{
                            label: '每日卡路里消耗 (卡)',
                            data: data.calories,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            }
                        },
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: '日期'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: '卡路里'
                                },
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('獲取每日卡路里數據時發生錯誤:', error);
                Swal.fire('錯誤', '無法加載每日卡路里數據', 'error');
            });
    }




