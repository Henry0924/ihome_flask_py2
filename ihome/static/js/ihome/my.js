function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
            url: "api/v1_0/session",
            type: "delete",
            dataType: "json",
            headers: {"X-CSRFToken": getCookie("csrf_token")}
        }).done(function (resp) {
             if (resp.error_code == 0){
                // 注册成功,引导到主页面
                location.href = '/';
            } else{
                alert(resp.errmsg);
            }
        });


    // $.get("/api/logout", function(data){
    //     if (0 == data.errno) {
    //         location.href = "/";
    //     }
    // })
}

$(document).ready(function(){
});