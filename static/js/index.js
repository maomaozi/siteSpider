$(document).ready(function() {
    $("#search").click(function () {
       window.location.href="search/?key="+$("#text").val();
    })
    $("#update").click(function () {
        window.location.href="update";
    })
    $("#capture").click(function () {
        window.location.href="capture";
    })
    $("#InputDiv").bind('keypress', function (event) {
                if (event.keyCode == "13") {
                    window.location.href = "search/?key=" + $("#text").val();
                }
    });
})
