$(function () {
            var ref = "";
            $.ajax({
                url:"/update/progress",
                success:function (data) {
                    var pro = parseInt(data.progress*10000)/100;  //舍去两位小数后面的小数
                    $('#pro').text(pro+"%");
                    $('#proBack').css("width",pro+"%");
                    if(data.progress){
                        $("#start").attr("disabled", true);
                        ref = setInterval(function(){
                            update();
                        },1000);
                    }else {
                        // $("#stop").attr("disabled", true);
                    }
                }
            })
            function update() {    //更新进度条
                $.ajax({
                    url:"/update/progress",
                    success:function (data) {
                        var pro = parseInt(data.progress*10000)/100;  //舍去两位小数后面的小数
                        $('#pro').text(pro+"%");
                        $('#proBack').css("width",pro+"%");
                        if(data.progress == 1){
                            clearInterval(ref);
                            $("#stop").attr("disabled", true);
                            $("#start").attr("disabled", false);
                        }
                    }
                })
            }
            $("#start").click(function () {
                $.ajax({
                    url:"/update/start",
                    beforeSend: function () {
                                     // 发送前响应
                        $('#pro').text("正在连接......");
                    },
                    success:function () {
                        $("#start").attr("disabled", true);
                        $("#stop").attr("disabled", false);
                        ref = setInterval(function(){
                            update();
                        },1000);
                    }
                });
            });
            $("#stop").click(function () {
                $.ajax({
                    url:"/update/stop",
                    success:function(){
                        $("#stop").attr("disabled", true);
                        $("#start").attr("disabled", false);
                        clearInterval(ref);
                    }
                });
            });
})