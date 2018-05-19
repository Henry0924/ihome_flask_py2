$(document).ready(function(){
    // 对于发布房源，只有认证后的用户才可以，所以先判断用户的实名认证状态
    $.get("/api/v1_0/users/real_name", function (resp) {
        if (resp.error_code == 4101){
            // 用户未登录
            location.href = "/login.html";
        } else if(resp.error_code == 0){
            // 若未认证，显示去认证
            if (!(resp.data.real_name && resp.data.id_card)){
                $(".auth-warn").show();
                return;
            }
            // 已认证，获取发布过的房屋信息
            $.get("/api/v1_0/user/houses", function (resp) {
                if (resp.error_code == 0){
                    $("#houses-list").html(template("houses-list-tmp", {houses:resp.data.houses}));
                } else {
                    $("#houses-list").html(template("houses-list-tmp", {houses:[]}));
                }
            })
        }
    })
});