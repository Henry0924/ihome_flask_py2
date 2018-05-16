function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 向后端获取城区信息
    $.get("/api/v1_0/areas", function (resp) {
        if (resp.error_code == 0) {
            // 获取到了城区信息
            // var areas = resp.data.areas;
            // for (var i = 0; i < areas.length; i++) {
            //     var area = areas[i];
            //     $("#area-id").append('<option value="'+area.aid+'">'+area.aname+'</option>');
            // }
            // 使用前端模板渲染页面
            area_html = template("area-tmp", {areas: resp.data.areas});
            $("#area-id").html(area_html);
        } else {
            alert(resp.errmsg);
        }
    })
});