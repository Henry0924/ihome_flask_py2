function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 获取图片验证码
    // 生成验证码编号 uuid
    imageCodeId = generateUUID();
    // 将uuid拼接成url设置到html页面中
    var url = "/api/v1_0/image_codes/" + imageCodeId;
    $(".image-code").children("img").attr("src", url);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    // $.get("/api/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId},
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg);
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒");
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码');
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60);
    //         }
    // }, 'json');
    var reg_data = {image_code_id: imageCodeId, image_code: imageCode};
    $.get("/api/v1_0/sms_codes/"+mobile, reg_data, function (resp) {
        if (resp.error_code == 4004 || resp.error_code == 4002){
            // 图片验证码的错误
            $("#image-code-err span").html(resp.errmsg);
            $("#image-code-err").show();
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        } else if (resp.error_code == 0){
            // 发送短信成功
            var $time = $(".phonecode-a");
            var duration = 60;
            // 设置定时器
            var intervalid = setInterval(function () {
                $time.html(duration + "秒");
                if (duration === 1){
                    // 清除定时器
                    clearInterval(intervalid);
                    $time.html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                }
                duration = duration - 1;
            }, 1000, 60);
        }
    });
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }


        var req_data = {
            mobile: mobile,
            sms_code: phoneCode,
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
            url: "api/v1_0/users",
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