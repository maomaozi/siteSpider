$(function () {
    loadList();

    $("#add").click(function () {
        if(!($("#domain").val() && $("#allow_domain").val() && $("#request_delay").val() && $("#start_url").val() && $("#name").val())){
            alert("请输入完整网址！");
        }else {
            $.ajax({
                url: "/capture/add_spider",
                data: {
                    "domain": $("#domain").val(),
                    "spider_name": $("#name").val(),
                    "spider_allow_domain": $("#allow_domain").val(),
                    "spider_start_url": $("#start_url").val(),
                    "request_delay": $("#request_delay").val()
                },
                success:function (data) {
                    if(data.success){
                        alert("添加成功");
                        loadList();
                    }
                    else{
                        alert("添加失败")
                    }
                }
            });
        }
    });

    $("#delete").click(function () {
        if(confirm("确定删除？")){
            $("input[name=chx]:checked").each(
                function(){
                    $.ajax({
                        url: "/capture/del_spider",
                        data: {
                            "spider_name": $(this).parent().prev().prev().html()
                        },
                        success:function (data) {
                            if(data.success){
                                console.log(data)
                                // alert("删除成功")
                            }else{
                                console.log(data)
                                // alert("删除失败")
                            }
                        }
                    });
                }
            );
            loadList();
        }
    });

    $("#startWeb").click(function () {
        $("input[name=chx]:checked").each(
            function(){
                $.ajax({
                    url: "/capture/start_spider",
                    data: {
                        "spider_name": $(this).parent().prev().prev().html()
                    },
                    success:function (data) {
                        if(data.success){
                            console.log(data)
                        }else{
                            console.log(data)
                        }
                    }
                });
            }
        );
        loadList();
    });

    $("#stopWeb").click(function () {
        $("input[name=chx]:checked").each(
            function(){
                $.ajax({
                    url: "/capture/stop_spider",
                    data: {
                        "spider_name": $(this).parent().prev().prev().html()
                    },
                    success:function (data) {
                        if(data.success){
                            console.log(data)
                        }else{
                            console.log(data)
                        }
                    }
                });
            }
        );
        loadList();
    });

    $("[id^='tipLog_']").each(function() {
        $(this).click(function() {
            alert("1");
        })
    });
    // $("#tipLog"+).click(function(){
    //     alert($(this).html());
    // });
});

function checkAll() {
    $("input[name=chx]").each(
        function(){
            $(this).attr("checked",'true');
        }
    )
}

function checkNo() {
    $("input[name=chx]").each(
        function(){
            $(this).removeAttr("checked");
        }
    )
}


function showLog() {
    $(this).html()
    // $.ajax({
    //     url: "/capture/get_spider_log",
    //     data: {
    //         "spider_name": $(this).html()
    //     },
    //     success:function (data) {
    //         if(data.success){
    //             alert(data);
    //             console.log(data)
    //         }else{
    //             console.log(data)
    //         }
    //     }
    // });
}

function loadList() {
    $.ajax({
        url: "/capture/list_spiders",
        success:function (data) {
            var tableBodyHtml = new Array();
            for(var i=0;i<data.length;i++){
                // var imgUrl;
                var char;
                if(data[i].status){                             //spider is running
                    // imgUrl = "../images/running.gif";
                    char = "running"
                }else{                                          //spider is not running
                    // imgUrl ="../images/running.gif";
                    char = "waiting"
                }
                tableBodyHtml.push("<tr style='height: 30px'>");
                //domain
                tableBodyHtml.push("<td style=\"padding-left: 20px;padding-right: 20px;width: 230px;\">");
                tableBodyHtml.push("<label>" + data[i].domain + "</label>");
                tableBodyHtml.push("</td>");

                //spider_name
                tableBodyHtml.push("<td id='tipLog_" + i +"' style='padding-left: 20px;padding-right: 20px;width: 220px;color: #3975ea;cursor: pointer;'>");
                tableBodyHtml.push( data[i].spider_name );
                tableBodyHtml.push("</td>");

                //status
                tableBodyHtml.push("<td style='padding-left: 20px;padding-right: 20px;width: 150px;'>");
                // tableBodyHtml.push("<label>" + char + "</label><img width='25px' height='25px' src=\""+imgUrl+"\">");
                tableBodyHtml.push("<label>" + char + "</label>");
                tableBodyHtml.push("</td>");

                //check-box
                tableBodyHtml.push("<td style=\"\">");
                // tableBodyHtml.push("<td style=\"display:inline\">");
                tableBodyHtml.push("<input type='checkbox' name='chx'>");
                tableBodyHtml.push("</td>");
                tableBodyHtml.push(" </tr>");
            }
            $("#spiderList").html(tableBodyHtml.join(""));
        }
    });
}