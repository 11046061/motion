document.addEventListener('DOMContentLoaded', function () {
    const profileForm = document.getElementById('profileForm');
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    const saveButton = document.querySelector('#profileForm button');
    const weightChartCanvas = document.getElementById('weightChart');
    const weightChartContext = weightChartCanvas.getContext('2d');

    let chartInstance;

    // 加載個人資料數據
    fetch('/get-profile-data')
        .then(response => response.json())
        .then(data => {
            if (data.height) {
                heightInput.value = data.height;  // 身高只需輸入一次
            }
            if (data.weight_today) {
                weightInput.value = data.weight_today;  // 當天體重
            }
            loadWeightHistory();  // 加載體重歷史數據
        })
        .catch(error => {
            Swal.fire('錯誤', '無法加載個人數據', 'error');
        });

    // 儲存資料
    saveButton.addEventListener('click', function (event) {
        event.preventDefault();  // 防止表單默認提交
        const height = parseFloat(heightInput.value);
        const weight = parseFloat(weightInput.value);

        if (!height || !weight) {
            Swal.fire('錯誤', '請正確輸入資料', 'error');
            return;
        }

        fetch('/update-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ height, weight_today: weight })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Invalid data');
            }
        })
        .then(data => {
            Swal.fire('成功', '資料已更新', 'success');
            loadWeightHistory();  // 更新體重歷史數據
        })
        .catch(error => {
            Swal.fire('錯誤', '無法更新資料，請稍後再試', 'error');
        });
    });

    // 加載體重歷史
    function loadWeightHistory() {
        fetch('/get-weight-history')
            .then(response => response.json())
            .then(data => {
                const dates = data.dates;
                const weights = data.weights;

                if (chartInstance) {
                    chartInstance.destroy();  // 重建圖表
                }

                chartInstance = new Chart(weightChartContext, {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [{
                            label: '體重 (kg)',
                            data: weights,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            fill: false
                        }]
                    }
                });
            })
            .catch(error => {
                Swal.fire('錯誤', '無法加載體重歷史', 'error');
            });
    }


    // 插入登入頁面的按鈕
    const loginButton = document.createElement('button');
    loginButton.textContent = '前往登入頁面';
    loginButton.classList.add('login-btn'); // 你可以添加這個類來自定義樣式
    document.body.appendChild(loginButton); // 你可以選擇將按鈕插入到適當的位置

    // 設定點擊事件，跳轉到 login.html
    loginButton.addEventListener('click', function() {
        window.location.href = '/login'; // 跳轉到登入頁面，Flask 會自動尋找 templates/login.html
    });
});
