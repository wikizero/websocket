$(function () {

    var progressbar = $("#progressbar"),
        bar = progressbar.find('.uk-progress-bar'),
        settings = {
            param: 'files',

            action: '/listen', // upload url

//                {# allow: '*.(jpg|gif|png|jpeg|doc|txt|py|html|css|xlsx|xls|xlst|)', // allow only images#}

            loadstart: function () {
                bar.css("width", "0%").text("0%");
                progressbar.removeClass("uk-hidden");
            },

            progress: function (percent) {
                percent = Math.ceil(percent);
                bar.css("width", percent + "%").text(percent + "%");
            },

            allcomplete: function (response) {
                bar.css("width", "100%").text("100%");

                setTimeout(function () {
                    progressbar.addClass("uk-hidden");
                }, 250);
                if (response.status == 'success') {
                    UIkit.notify("<i class='uk-icon-paper-plane'></i> 文件上传成功了耶!", {status: 'success'});
                    // setTimeout(function () {
                    //     window.location.reload()
                    // }, 2000)

                } else {
                    UIkit.notify("<i class='uk-icon-exclamation-triangle'></i> response.status!", {status: 'danger'});
                }
            },
            type: 'json'
        };
    var select = UIkit.uploadSelect($("#upload-select"), settings),
        drop = UIkit.uploadDrop($("#upload-drop"), settings);
});


$(function () {
    var url = "http://" + document.domain + ':' + location.port;
    console.log(url);
    var io_client = io.connect(url);
    io_client.on('connect', function () {
        // 连接成功时的事件
        io_client.emit('login', {data: 'I\'m connected!'});
    });

    io_client.on("mes", function (resp) {
        // 绑定的事件, 对应py文件中的event参数的值
        var resp = JSON.parse(resp);
        var row = "<tr><td>" + resp.ip + "</td><td>" + resp.datetime + "</td><td>" + resp.type + "</td><td class='content'></td><td id='copy'><a class='uk-icon-hover uk-icon-clipboard'></a></td></tr>"
        console.log(resp.content);
        $("tbody").prepend(row);
        $("tbody tr:first-child .content").text(resp.content)
    });

    // 发送按钮事件
    $("#submit").click(function () {
        var text = $.trim($("#text").val());
        if (text == "") {
            // nothing...
        } else {
            $.post("/listen", {"data": text}, function (resp) {
                var resp = JSON.parse(resp);
                var status = resp['status'];
                console.log(status)
                if (status == "success") {
                    $("#text").val("");  // 清空输入内容
                } else {
                    console.log(status);
                }
            });
        }
    });

    // copy 函数
    function copy_to_clipboard(str) {
        var oInput = document.createElement('input')
        oInput.value = str
        document.body.appendChild(oInput)
        oInput.select()
        document.execCommand("Copy")
        oInput.style.display = 'none'
        document.body.removeChild(oInput)
        window.alert('复制成功')
    };


    $(document).on("click", '#copy', function () {
        copy_to_clipboard($(this).prev().text());
    });

});


















