function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    // 设置用户头像
    $("#form-avatar").submit(function (e) {
        e.preventDefault();

        $(this).ajaxSubmit({
            url: "/api/v1_0/users/avatar",
            type: "post",
            dataType: "json",
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            success: function (resp) {
                if (resp.error_code == 0) {
                    $("#user-avatar").attr("src", resp.data.avatar_url);
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });

    // 设置用户名
    $("#form-name").submit(function (e) {
        e.preventDefault();
        var username = $("#user-name").val();
        // alert(username);
        $.ajax({
            url: "/api/v1_0/users/name",
            type: "put",
            data: JSON.stringify({username: username}),
            contentType: "application/json",
            dataType: "json",
            headers: {"X-CSRFToken": getCookie("csrf_token")},
            success: function (resp) {
                if (resp.error_code == 0) {
                    alert(resp.errmsg);
                    location.href = '/my.html';
                } else if (resp.error_code == 4103){
                    alert(resp.errmsg);
                } else if (resp.error_code == 4001){
                    alert(resp.errmsg);
                }
            }
        })
    });


});
