document.addEventListener('DOMContentLoaded', function () {
    const profileForm = document.getElementById('profileForm');
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    const saveButton = document.querySelector('#profileForm button');
    const weightChartCanvas = document.getElementById('weightChart');
    const bmiStatusChartCanvas = document.getElementById('bmiStatusChart');
    const weightHistoryChartCanvas = document.getElementById('weightHistoryChart');

    let weightChartContext = weightChartCanvas.getContext('2d');
    let bmiStatusChartContext = bmiStatusChartCanvas.getContext('2d');
    let weightHistoryChartContext = weightHistoryChartCanvas.getContext('2d');

    let bmiChartInstance, bmiStatusChart, weightHistoryChart;

    // 加載個人資料
    fetch('/get-profile-data')
        .then(response => response.json())
        .then(data => {
            if (data.height) heightInput.value = data.height;
            if (data.weight_today) weightInput.value = data.weight_today;
            if (data.waist) document.getElementById('waist').value = data.waist;
            if (data.hip) document.getElementById('hip').value = data.hip;
            loadBMIHistory();
            loadWeightHistory();
            updateTargetWeight();
        })
        .catch(error => {
            Swal.fire('錯誤', '無法加載個人數據', 'error');
        });

    // 儲存按鈕事件
    saveButton.addEventListener('click', function (event) {
        event.preventDefault();
    
        const height = parseFloat(heightInput.value);
        const weight_today = parseFloat(weightInput.value);
        const waist = parseFloat(document.getElementById('waist').value);
        const hip = parseFloat(document.getElementById('hip').value);
    
        if (!height || !weight_today || !waist || !hip) {
            Swal.fire('錯誤', '請正確輸入所有數據', 'error');
            return;
        }
    
        fetch('/update-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ height, weight_today, waist, hip }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('成功', '資料已更新', 'success');
                    // 重新加載數據
                    fetch('/get-profile-data')
                        .then(response => response.json())
                        .then(updatedData => {
                            if (updatedData.height) heightInput.value = updatedData.height;
                            if (updatedData.weight_today) weightInput.value = updatedData.weight_today;
                            if (updatedData.waist) document.getElementById('waist').value = updatedData.waist;
                            if (updatedData.hip) document.getElementById('hip').value = updatedData.hip;
    
                            fetchAndRenderWaistHipChart(); // 更新腰臀比圖表
                            loadBMIHistory(); // 更新 BMI 圖表
                            loadWeightHistory(); // 更新體重圖表
                            updateTargetWeight(); // 更新目標體重
                        });
                } else {
                    Swal.fire('錯誤', data.error || '資料更新失敗', 'error');
                }
            })
            .catch(error => {
                Swal.fire('錯誤', '無法更新資料，請稍後再試', 'error');
            });
    });
    
    
    
    

    // 加載 BMI 歷史
    function loadBMIHistory() {
        const height = parseFloat(heightInput.value);
        if (!height) return;

        fetch('/get-weight-history')
            .then(response => response.json())
            .then(data => {
                const dates = data.dates;
                const weights = data.weights;
                const bmis = weights.map(weight => (weight / ((height / 100) ** 2)).toFixed(2));

                // 銷毀舊的 BMI 圖表
                if (bmiChartInstance) bmiChartInstance.destroy();

                // 初始化新的 BMI 圖表
                bmiChartInstance = new Chart(weightChartContext, {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [{
                            label: 'BMI',
                            data: bmis,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            fill: false
                        }]
                    }
                });

                // 更新 BMI 狀態橫條圖
                updateBMIStatus(bmis[bmis.length - 1]);
            })
            .catch(error => {
                Swal.fire('錯誤', '無法加載 BMI 歷史', 'error');
            });
    }

    // 加載體重歷史
    function loadWeightHistory() {
        fetch('/get-weight-history')
            .then(response => response.json())
            .then(data => {
                const dates = data.dates;
                const weights = data.weights;

                // 銷毀舊的體重歷史圖表
                if (weightHistoryChart) weightHistoryChart.destroy();

                // 初始化新的體重歷史圖表
                weightHistoryChart = new Chart(weightHistoryChartContext, {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [{
                            label: '體重',
                            data: weights,
                            borderColor: 'rgba(153, 102, 255, 1)',
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true
                    }
                });
            })
            .catch(error => {
                Swal.fire('錯誤', '無法加載體重歷史: ' + error.message, 'error');
            });
    }

    // 更新 BMI 狀態圖表
    function updateBMIStatus(currentBMI) {
        // 銷毀舊的 BMI 狀態圖表
        if (bmiStatusChart) bmiStatusChart.destroy();

        // 初始化新的 BMI 狀態圖表
        bmiStatusChart = new Chart(bmiStatusChartContext, {
            type: 'bar',
            data: {
                labels: ['過輕', '正常', '過重'],
                datasets: [{
                    label: '當前 BMI',
                    data: [
                        currentBMI < 18.5 ? currentBMI : 0,
                        currentBMI >= 18.5 && currentBMI <= 25 ? currentBMI : 0,
                        currentBMI > 25 ? currentBMI : 0
                    ],
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 30
                    }
                }
            }
        });
    }

    // 計算並顯示目標體重
    function updateTargetWeight() {
        const height = parseFloat(heightInput.value);
        const targetWeightSpan = document.getElementById('targetWeight');

        if (height) {
            const targetWeight = ((height - 80) * 0.7).toFixed(1);  // 計算目標體重
            targetWeightSpan.innerText = `${targetWeight} 公斤`;
        }
    }
});


function confirmDelete() {
    return confirm("您確定要刪除您的帳戶嗎？此操作無法撤銷。");
}

function confirmLogout() {
    Swal.fire({
        title: 'Confirm Logout?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes',
        cancelButtonText: 'No'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "{{ url_for('logout') }}"; // 确保已正确定义此路由
        }
    })
}

function toggleDropdown() {
    var dropdown = document.getElementById("settingsDropdown");
    // 當前dropdown顯示則隱藏，隱藏則顯示
    if (dropdown.style.display === "block") {
        dropdown.style.display = "none";
    } else {
        dropdown.style.display = "block";
    }
}

// 當頁面載入時，確保 dropdown 選項默認隱藏
document.addEventListener('DOMContentLoaded', function() {
    var dropdown = document.getElementById("settingsDropdown");
    const saveButton = document.querySelector('#profileForm button');
    if (!saveButton) {
        console.error("按鈕未找到，請檢查 HTML 結構");
        return;
    }
    // 確保 dropdown 存在再操作
    if (dropdown) {
        dropdown.style.display = "none";
    } else {
        console.log("元素 'settingsDropdown' 不存在");
    }
});



let waistHipChartInstance; // 用於存儲圖表實例

function fetchAndRenderWaistHipChart() {
    fetch('/get-weight-history') // 從後端獲取數據
        .then((response) => response.json())
        .then((data) => {
            if (!data.dates || data.dates.length === 0) {
                console.warn('No data available for waist-hip chart');
                return;
            }

            const canvas = document.getElementById('waistHipChart');
            const ctx = canvas.getContext('2d');

            // 銷毀舊的圖表實例（如果存在）
            if (waistHipChartInstance) {
                waistHipChartInstance.destroy();
                waistHipChartInstance = null;
            }

            // 初始化新圖表
            waistHipChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates, // 日期數據
                    datasets: [
                        {
                            label: '腰臀比',
                            data: data.waist_hip_ratios, // 比例數據
                            borderColor: 'rgb(255, 99, 132)',
                            borderWidth: 2,
                            fill: false,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: '日期' } },
                        y: { title: { display: true, text: '腰臀比' } },
                    },
                },
            });
        })
        .catch((error) => console.error('Error fetching waist-hip data:', error));
}


// 初始化圖表
document.addEventListener('DOMContentLoaded', () => {
    fetchAndRenderWaistHipChart();
});


    
    


function showModal() {
    document.getElementById("settingsModal").style.display = "block";
}

function closeModal() {
    document.getElementById("settingsModal").style.display = "none";
}

function deleteAccount() {
    if (confirm("您確定要刪除帳戶嗎？")) {
        document.getElementById('delete-form').submit(); // 提交表單刪除帳戶
    }
}

function logout() {
    document.getElementById('logout-form').submit(); // 提交登出表單
}
