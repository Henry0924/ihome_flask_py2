function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

$(function () {
    // 获取实名信息
    $.get("/api/v1_0/users/real_name", function (resp) {
        if (resp.error_code == 4102) {
            location.href = "/login.html";
        } else if (resp.error_code == 0) {
            if (resp.data.real_name && resp.data.id_card) {
                $("#real-name").val(resp.data.real_name);
                $("#id-card").val(resp.data.id_card);
                // 给input添加disabled属性，禁止用户修改
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                $(".btn-success").hide();
            }
        }
    });

    // 实名认证
    $("#form-auth").submit(function (e) {
        e.preventDefault();
        // 如果用户没有填写完整提示错误信息
        if ($("#real-name").val() == "" || $("#id-card").val() == "") {
            $(".error-msg").show();
        }

        var auth = {
            real_name: $("#real-name").val(),
            id_card: $("#id-card").val()
        };
        $.ajax({
            url: "/api/v1_0/users/real_name",
            type: "post",
            data: JSON.stringify(auth),
            contentType: "application/json",
            dataTyp: "json",
            headers:{"X-CSRFToken": getCookie("csrf_token")}
        }).done(function (resp) {
            if (resp.error_code == 4102) {
                location.href = "/login.html";
            } else if (resp.error_code == 0) {
                // 实名成功
                showSuccessMsg();
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                $(".btn-success").hide();
            }
        })
    })
});