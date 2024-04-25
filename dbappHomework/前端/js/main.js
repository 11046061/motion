let jsontext;
let sortmode="asc";
let data = [];
const host = 'https://dbappbackend.leedong.work';

//創建資料
function createData(){
    id=document.getElementById("userid");
    username=document.getElementById("username");
    email=document.getElementById("useremail");
    contact=document.getElementById("usercontact");
    if(id.value==="" || username.value=="" || email.value=="" || contact.value==""){
        alert("欄位不可為空");
    }else{
        let json_data = {'id': id.value, 'name': username.value, 'email': email.value , 'contact': contact.value };
        fetch(host+'/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(json_data)
        })
            .then(response => response.json())
            .then(data => {
                alert(data.result);
                id.value="";
                username.value="";
                email.value="";
                contact.value="";
                getAllData(sortmode);
            });
    }

}


//查詢全部資料
function getAllData(sortmode){
    fetch(host+'/get?'+ new URLSearchParams({sort: sortmode}), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            jsontext=data;
            showdata();
          });
}

//根據學號查詢資料
function findData(ids){
    fetch(host+'/get?'+ new URLSearchParams({id: ids}), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            jsontext=data;
            showdata();
        });
}

//更新前端顯示的資料
function showdata(){
    const obj = jsontext;
    data=[];

    var Content = document.getElementById('content')
    Content.innerHTML='';
    if(obj.data===null){
        alert("發生錯誤");
    }else if(obj.data.length===0){
        Content.innerHTML += `
        <div class="itemgroup">
            <p style="color: red; text-align: center;" >未有任何資料</p>
        </div>
        `;
    }else{ 
        for(i=0;i<obj.data.length;i++){
            data.push([obj.data[i].id,obj.data[i].name,obj.data[i].email,obj.data[i].contact])
            Content.innerHTML += `
            <div class="itemgroup">
                <div class="mainitem">
                    <p>序號: ${obj.data[i].sno}</p>
                    <p>學號: ${obj.data[i].id}</p>
                    <p>姓名: ${obj.data[i].name}</p>
                    <p>電子郵件: ${obj.data[i].email}</p>
                    <p>連絡電話: ${obj.data[i].contact}</p>
                    <div>
                        <button onclick="readData(${i})">帶入資料</button>
                        <button onclick="deleteData('${obj.data[i].id}')">刪除資料</button>
                    </div>
                </div>
            </div>
            `;        
        }
        console.log(data);
    }

}

function deleteData(id) {
    fetch(host+'/delete/'+id, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            alert(data.result);
            getAllData(sortmode);
        }
    );
}

//帶入資料到textbox
function readData(index){
    document.getElementById("Cuserid").value = data[index][0];
    document.getElementById("Cusername").value = data[index][1];
    document.getElementById("Cuseremail").value = data[index][2];
    document.getElementById("Cusercontact").value = data[index][3];  
}

//更新資料
function updateData(){
    id=document.getElementById("Cuserid");
    username=document.getElementById("Cusername");
    email=document.getElementById("Cuseremail");
    contact=document.getElementById("Cusercontact");
    if(id.value==="" || username.value=="" || email.value=="" || contact.value==""){
        alert("欄位不可為空");
    }else{
        ids = id.value
        let json_data = {'name': username.value, 'email': email.value , 'contact': contact.value };
        fetch(host+'/update/'+ids, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(json_data)
        })
            .then(response => response.json())
            .then(data => {
                alert(data.result);
                id.value="";
                username.value="";
                email.value="";
                contact.value="";
                getAllData(sortmode);
            }
        );
    }
}
function setSortMode(value){
    sortmode=value;
    getAllData(sortmode);
}
getAllData(sortmode);