// Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

//下载说明文档到U盘
App.downloadFile = (function () {
    // Public functions
    var start = function () {
        console.log("下载按钮点击成功！");
        App.screen.log('下载中！');
        // 判断USB状态
        if (App.screen.usb_status) {

            App.Util.serverRequest(App.url.copyDir, "POST", true, function (response) {
                if (response) {
                    App.screen.log('参考文件下载成功！请查看USB！');
                } else {
                    App.screen.log('参考文件下载失败！');
                }
            }, {
                "from_path": "坐席卡打印参考",
                "to_path": "",
                "operation_type": "apptousb"
            });


            //下载说明文档
            // App.Util.serverRequest(App.url.copyFile, "POST", true, function (response) {
            //     if (response) {
            //         App.screen.log('参考文件下载成功！请查看USB！');
            //     } else {
            //         App.screen.log('参考文件下载失败！请确认USB中是否已经有文件！');
            //     }
            // }, {
            //     "from_path": "坐席卡打印使用说明.pdf",
            //     "to_path": "",
            //     "operation_type": "apptousb"
            // });

            //下载示例CSV
            // App.Util.serverRequest(App.url.copyFile, "POST", true, function (response) {
            //     if (response) {
            //         App.screen.log('示例文件下载成功，请查看USB！');
            //     } else {
            //         App.screen.log('示例文件下载失败！');
            //     }
            // }, {
            //     "from_path": "zxk.csv",
            //     "to_path": "",
            //     "operation_type": "apptousb"
            // });


        } else {
            App.screen.log("请插入USB再试！")
        }
    };

    return {
        start: start,
    };
})();
