// Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

App.printJob = (function () {

    var show = function () {
        // 显示打印开始按钮
        $("#print_button").removeClass("disabled");
    }

    var hide = function () {
        // 禁止点击打印按钮
        $("#print_button").addClass("disabled");
    };

    // Public functions
    var start = function (sets, paper_size, color_mode, font_size, font_color) {
        // 执行复制，将文件复制到App目录里面
        console.log("将USB中的‘zxk.csv’文件复制到app的数据中")

        App.Util.serverRequest(App.url.copyFile, "POST", true, function (response) {
            if (response) {
                App.screen.log('成功读取到CSV文件！');
                // Start a new print job
                App.ajax.post('/print/jobs', {
                    sets: sets,
                    paper_size: paper_size,
                    color_mode: color_mode,
                    font_size: font_size,
                    font_color: font_color,
                }).then(function () {
                    // Print job is dispatched to background
                    console.log('调用App.printJob.log成功！')
                    App.screen.log('打印作业将在后台启动！');
                    // setTimeout('App.screen.log("")', 2000);
                }).fail(function (error) {
                    // Failed to start a print job
                    console.log('调用App.printJob.start失败！错误内容：' + JSON.stringify(error))
                    var response = error.responseJSON;
                    if (response.error_code === App.errors.printJobCannotStarted) {
                        // Print job cannot be started by some reasons
                        App.screen.log('无法启动打印作业，错误原因："' + response.error_details.error_type + '".');
                    } else {
                        // Unexpected error

                        App.screen.log('启动打印作业时发生意外错误！' + JSON.stringify(response));
                    }
                }).always(function () {

                });
            } else {
                App.screen.log('CSV文件没有找到！');
                App.printJob.show()
            }
        }, {
            "from_path": "zxk.csv",
            "to_path": "documents",
            "operation_type": "usbtoapp"
        });

    };

    return {
        start: start,
        show: show,
        hide: hide,
    };
})();
