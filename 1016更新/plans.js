document.addEventListener('DOMContentLoaded', function () {
    const exerciseTable = document.getElementById('exerciseTable');
    const today = new Date();
    let currentExerciseIndex = 0;
    let exercises = []; // 在這裡初始化 exercises 變數

    // 檢查後端是否有完成的狀態
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

// 加載用戶資料並檢查當天體重
function loadProfileData() {
    const dayOfWeek = today.toLocaleString('en-US', { weekday: 'long' });

    // 檢查是否是星期天，如果是，直接顯示休息日計畫
    if (dayOfWeek === 'Sunday') {
        loadExercisePlan(null, dayOfWeek); // 傳遞 null 作為 bodyType，因為休息日不需要計算BMI
        return;
    }

    // 如果不是星期天，則檢查體重和身高
    fetch('/get-profile-data')
        .then(response => response.json())
        .then(data => {
            const height = data.height;
            const weight = data.weight_today;  // 從後端獲取當天的體重

            if (!weight || !height) {
                exerciseTable.innerHTML = `<tr><td>請到個人頁面輸入今日體重</td></tr>`;
            } else {
                const bodyType = calculateBMI(height, weight);
                loadExercisePlan(bodyType, dayOfWeek);
            }
        })
        .catch(error => {
            console.error("獲取用戶數據時出錯:", error);
            exerciseTable.innerHTML = `<tr><td>未能加載健身計劃，請稍後再試</td></tr>`;
        });
}


    // 計算 BMI
    function calculateBMI(height, weight) {
        const bmi = weight / ((height / 100) ** 2);
        console.log(`計算出的 BMI: ${bmi}`);

        if (bmi < 18.5) {
            return 'thin';
        } else if (bmi >= 18.5 && bmi < 25) {
            return 'average';
        } else {
            return 'overweight';
        }
    }

    // 加載對應的健身計劃
    function loadExercisePlan(bodyType, dayOfWeek) {
        console.log(`加載健身計劃，Body Type: ${bodyType}, Day of Week: ${dayOfWeek}`);
        const fitnessPlans = {
            thin: {
                Monday: [
                    { exercise: '俯臥撐', image: '俯臥撐.png' },
                    { exercise: '仰臥起坐', image: '仰臥起坐.png' },
                    { exercise: '登山跑', image: '登山跑.png' }
                ],
                Tuesday: [
                    { exercise: '深蹲', image: '深蹲.png' },
                    { exercise: '弓步蹲', image: '弓步蹲.png' },
                    { exercise: '側棒式支撐', image: '側棒式支撐.png' }
                ],
                Wednesday: [
                    { exercise: '平板支撐', image: '平板支撐.png' },
                    { exercise: '高抬腿', image: '高抬腿.png' },
                    { exercise: '仰臥自行車', image: '仰臥自行車.png' }
                ],
                Thursday: [
                    { exercise: '弓步蹲', image: '弓箭步.png' },
                    { exercise: '單腳硬拉', image: '單腳硬拉.png' },
                    { exercise: '跳躍深蹲', image: '跳躍深蹲.png' }
                ],
                Friday: [
                    { exercise: '波比跳', image: '波比跳.png' },
                    { exercise: '側步蹲', image: '側步蹲.png' },
                    { exercise: '肩膀挺舉', image: '肩膀挺舉.png' }
                ],
                Saturday: [
                    { exercise: '開合跳', image: '開合跳.png' },
                    { exercise: '仰臥腿舉', image: '仰臥腿舉.png' },
                    { exercise: '臀橋', image: '臀橋.png' }
                ],
                Sunday: [
                    { exercise: '休息日：放鬆並進行輕度伸展', image: null }
                ]
            },
            average: {
                Monday: [
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' },
                    { exercise: '俯臥撐', image: '俯臥撐.png' },
                    { exercise: '跳繩', image: '跳繩.png' }
                ],
                Tuesday: [
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' },
                    { exercise: '單臂啞鈴推舉', image: '單臂啞鈴推舉.png' },
                    { exercise: '側棒式支撐', image: '側棒式支撐.png' }
                ],
                Wednesday: [
                    { exercise: '高抬腿', image: '高抬腿.png' },
                    { exercise: '深蹲', image: '深蹲.png' },
                    { exercise: '俯臥撐', image: '俯臥撐.png' }
                ],
                Thursday: [
                    { exercise: '俯臥撐', image: '俯臥撐.png' },
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' },
                    { exercise: '仰臥自行車', image: '仰臥自行車.png' }
                ],
                Friday: [
                    { exercise: '深蹲', image: '深蹲.png' },
                    { exercise: '弓步蹲', image: '弓步蹲.png' },
                    { exercise: '平板支撐', image: '平板支撐.png' }
                ],
                Saturday: [
                    { exercise: '高抬腿', image: '高抬腿.png' },
                    { exercise: '開合跳', image: '開合跳.png' },
                    { exercise: '肩膀挺舉', image: '肩膀挺舉.png' }
                ],
                Sunday: [
                    { exercise: '休息日：放鬆並進行輕度伸展', image: null }
                ]
            },
            overweight: {
                Monday: [
                    { exercise: '步行', image: '步行.png' },
                    { exercise: '牽拉運動', image: '牽拉運動.png' },
                    { exercise: '高抬腿', image: '高抬腿.png' }
                ],
                Tuesday: [
                    { exercise: '靠牆深蹲', image: '深蹲.png' },
                    { exercise: '臀橋', image: '臀橋.png' },
                    { exercise: '仰臥腿舉', image: '仰臥腿舉.png' }
                ],
                Wednesday: [
                    { exercise: '爬樓梯', image: '爬樓梯.png' },
                    { exercise: '深蹲', image: '深蹲.png' },
                    { exercise: '側步蹲', image: '側步蹲.png' }
                ],
                Thursday: [
                    { exercise: '跪姿俯臥撐', image: '俯臥撐.png' },
                    { exercise: '平板支撐', image: '平板支撐.png' },
                    { exercise: '臀橋', image: '臀橋.png' }
                ],
                Friday: [
                    { exercise: '凳上臂屈伸', image: '凳上臂屈伸.png' },
                    { exercise: '仰臥腿舉', image: '仰臥腿舉.png' },
                    { exercise: '爬樓梯', image: '爬樓梯.png' }
                ],
                Saturday: [
                    { exercise: '登山跑', image: '登山跑.png' },
                    { exercise: '跳繩', image: '跳繩.png' },
                    { exercise: '側棒式支撐', image: '側棒式支撐.png' }
                ],
                Sunday: [
                    { exercise: '休息日：放鬆並進行輕度伸展', image: null }
                ]
            }
        };

        const todayExercises = fitnessPlans[bodyType]?.[dayOfWeek];

        if (dayOfWeek === 'Sunday') {
            // 如果是星期天，顯示休息日
            exerciseTable.innerHTML = `
                <tr>
                    <th>Day</th>
                    <th>Exercise</th>
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
        exerciseTable.innerHTML = `
            <tr>
                <th>Day</th>
                <th>Exercise</th>
            </tr>
            <tr>
                <td>${dayOfWeek}</td>
                <td>
                    ${exerciseObj.exercise}
                    <br>
                    <img src="/static/images/${exerciseObj.image}" alt="${exerciseObj.exercise}" id="img-${dayOfWeek}">
                    <br><br>
                    <div id="timerDisplay-${dayOfWeek}" class="timer-display">00:00</div>
                </td>
            </tr>
        `;

        if (currentExerciseIndex === 0) {
            const startButton = document.createElement('button');
            startButton.id = `startTimer-${dayOfWeek}`;
            startButton.classList.add('start-timer');
            startButton.textContent = '開始計時';
            exerciseTable.appendChild(startButton);

            startButton.addEventListener('click', function () {
                startButton.style.display = 'none'; // 按下後隱藏按鈕
                startTimer(dayOfWeek);
            });
        }
    }

    // 計時器功能，並顯示休息時間及完成訊息
    function startTimer(dayOfWeek) {
        const display = document.getElementById(`timerDisplay-${dayOfWeek}`);
        let seconds = 60;
        display.textContent = `開始動作，剩餘時間: ${seconds}s`;

        interval = setInterval(() => {
            seconds--;
            display.textContent = `剩餘時間: ${seconds}s`;

            if (seconds === 0) {
                clearInterval(interval);
                startRestTimer(dayOfWeek);
            }
        }, 1000);
    }

    // 休息時間倒數並顯示下一個動作
    function startRestTimer(dayOfWeek) {
        currentExerciseIndex++;

        if (currentExerciseIndex < exercises.length) {
            displayExercise(exercises[currentExerciseIndex], dayOfWeek);

            let restSeconds = 30;
            const display = document.getElementById(`timerDisplay-${dayOfWeek}`);
            display.textContent = `休息 ${restSeconds} 秒`;

            restInterval = setInterval(() => {
                restSeconds--;
                display.textContent = `休息 ${restSeconds} 秒`;

                if (restSeconds <= 0) {
                    clearInterval(restInterval);
                    startTimer(dayOfWeek);  // 休息結束後，開始下一個動作的計時
                }
            }, 1000);
        } else {
            completeWorkout();
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