$(function () {
            $("#update").click(function () {
                window.location.href="../update";
            });

            var li = $(".pagination").children("li");
            if(GetQueryString("page")){
                li[GetQueryString("page")-1].firstChild.className = "active";
            }else {
                li[0].firstChild.className = "active";
            }


            var total = 10;    //显示在页面上的页码的格子数
            var n =$('.pagination li').length;
            var c=GetQueryString("page")-1;
            if(n>total){
                if(c>5){
                    if(c>n-5){
                        for (i=0;i<n-10;i++){
                            $(".pagination li:eq("+i+")").hide()
                        }
                    }else{
                        for (i=0;i<c-5;i++){
                            $(".pagination li:eq("+i+")").hide()
                        }
                    }
                    for (i=c+5;i<n;i++){
                        $(".pagination li:eq("+i+")").hide()
                    }
                }else {
                    for (i=total;i<n;i++){
                        $(".pagination li:eq("+i+")").hide()
                    }
                }
            }

            $("select[name='choose']").change(function(){
                var yes = $(this).next();
                var no = $(this).next().next();
                $.ajax({
                    url: "/model/",
                    data: {
                        "text": $(this).parent().children("a").attr('href'),
                        "classType": $(this).val()
                    },
                    success:function (data) {
                        if(data.success){
                            no.hide();
                            yes.show();
                        }
                        else{
                            yes.hide();
                            no.show();
                        }
                    }
                });
             });
});
        function GetQueryString(name)
        {
            var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if(r!=null)return  unescape(r[2]); return null;
        }