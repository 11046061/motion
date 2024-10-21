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
            loadBMIHistory();  // 加載 BMI 歷史數據
        })
        .catch(error => {
            Swal.fire('錯誤', '無法加載個人數據', 'error');
        });

    // 儲存資料
    saveButton.addEventListener('click', function (event) {
        event.preventDefault();
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
        .then(response => response.json())
        .then(data => {
            Swal.fire('成功', '資料已更新', 'success');
            loadBMIHistory();  // 更新 BMI 歷史數據
        })
        .catch(error => {
            Swal.fire('錯誤', '無法更新資料，請稍後再試', 'error');
        });
    });

    // 加載 BMI 歷史
    function loadBMIHistory() {
        fetch('/get-weight-history')
            .then(response => response.json())
            .then(data => {
                const dates = data.dates;
                const weights = data.weights;
                const height = parseFloat(heightInput.value);

                if (!height) {
                    Swal.fire('錯誤', '請先輸入有效的身高', 'error');
                    return;
                }

                const bmis = weights.map(weight => {
                    const bmi = weight / ((height / 100) ** 2);
                    return bmi.toFixed(2);
                });

                if (chartInstance) {
                    chartInstance.destroy();
                }

                chartInstance = new Chart(weightChartContext, {
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
            })
            .catch(error => {
                Swal.fire('錯誤', '無法加載 BMI 歷史', 'error');
            });
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
