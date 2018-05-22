var cur_page = 1;
var next_page = 1;
var total_page = 1;
var house_data_querying = true;

function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}

// action=renew 代表页面数据清空重新展示
function updateHouseData(action) {
    var areaId = $(".filter-area>li.active").attr("area-id")
    if (undefined==areaId) areaId = "";
    var starDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var sortKey = $(".filter-sort>li.active").attr("sort-key");
    var params = {
        aid:areaId,
        sd:starDate,
        ed:endDate,
        sk:sortKey,
        p:next_page
    };
    $.get("/api/v1_0/houses", params, function (resp) {
        house_data_querying = false;
        if (resp.error_code == 0){
            $(".house-comment-list").html("暂时没有你要查询的房屋信息")
        } else {
            total_page = resp.data.total_page;
            if ("renew" == action){
                cur_page = 1;
                $(".house-list").html(template("house-list-tmp", {house:resp.data.houses}));
            } else {
                cur_page = next_page;
                $(".houses-list").append(template("house-list-tmp", {house:resp.data.houses}));
            }
        }
    })

}


$(document).ready(function () {
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate);
    $("#end-date").val(endDate);
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);


    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function (e) {
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function (e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        cur_page = 1;
        next_page = 1;
        total_page = 1;
        updateHouseData("renew");

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function (e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function (e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    });

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
            var areaId = queryData["aid"];
            if (areaId) {
                area_html = template("area-tmp", {areas: resp.data.areas, aid:areaId});
                $(".filter-area").html(area_html);
            } else {
                area_html = template("area-tmp", {areas: resp.data.areas});
                $(".filter-area").html(area_html);
            }
            // 在页面添加好城区选项信息后，更新展示房屋列表信息
            updateHouseData("renew");

        } else {
            alert(resp.errmsg);
        }
    });
});