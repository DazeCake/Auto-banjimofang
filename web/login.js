var login = function () {
    var phone = $('#phone').val();
    var passwd = $('#password').val();
    console.log(phone, passwd)
    $.post("http://127.0.0.1:8888/add",
        {
            // 提交时携带的参数
            phone: phone,
            passwd: passwd,
        },
        // 回调函数,data是服务器返回的数据
        function (data, status) {
            console.log(data)
            alert(data.msg);
    });
}