// Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.
App.screen = (function () {

    var log = function (message) {
        $('#log').text(message);
    };

    // var usb_status = function (message) {
    //     $('#usb_status').text(message)
    // }

    var usb_status = false;

    // DOM event handlers
    $('#print_button').click(function () {
        console.log('打印按钮点击成功！');
        if (App.screen.usb_status) {
            // hideContents();
            var sets = 1;
            var paper_size = 'a4';
            var color_mode = 'full_color';
            var font_size = $("[name='font_size']:checked").val()
            var font_color = $(".ui-selected").data("color");

            if (!$("#print_button").hasClass("disabled")) {
                // 隐藏按钮
                App.printJob.hide()
                App.printJob.start(sets, paper_size, color_mode, font_size, font_color);
            }
        }else{
            App.screen.log("请插入USB再试！");
        }
    });


    // 测试拷贝文件是否成功按钮
    $('#check_button').click(function () {
        console.log('查看按钮点击成功！');
        App.checkJob.start();
    });

    //下载按钮
    $('#download_button').click(function () {
        console.log('下载按钮点击成功！');
        App.downloadFile.start();
    });

    return {
        log: log,
        usb_status: usb_status
    };
})();
