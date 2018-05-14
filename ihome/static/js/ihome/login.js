function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        var req_data = {
            mobile: mobile,
            password: passwd
        };
        // 将js对象转换成json字符串
        req_json = JSON.stringify(req_data);
        // $.post("api/v1_0/users", req_json, function (resp) {
        //     if (resp.error_code == 0){
        //         // 注册成功,引导到主页面
        //         location.href = '/';
        //     } else{
        //         alert(resp.errmsg);
        //     }
        // })

        $.ajax({
            url: "api/v1_0/session",
            type: "post",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {"X-CSRFToken": getCookie("csrf_token")}
        }).done(function (resp) {
             if (resp.error_code == 0){
                // 注册成功,引导到主页面
                location.href = '/';
            } else{
                alert(resp.errmsg);
            }
        })
    });
});