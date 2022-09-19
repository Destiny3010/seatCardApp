// Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

//检查Appstorage中有些什么文件。测试用！
App.checkJob = (function () {
    // Public functions
    var start = function () {
        //获取App目录中的文件列表
        var findFile = "http://embapp-local.toshibatec.co.jp:50187/v1.0/app/storage/self/files?is_recursive=false";
        // 获取USB中的文件列表
        var findFileUSB = "http://embapp-local.toshibatec.co.jp:50187/v1.0/externaldevice/usb/files?is_recursive=false";
        
        var AllFileList = "";

        App.Util.serverRequest(findFile, "GET", true, function (response) {
            if (response) {
                console.log("get file names");
                var fileList = response["storage_path_list"].map(function (element) {
                    var elementObj = {};
                    elementObj.name = element;
                    elementObj.type = "file";
                    return elementObj;
                })
                console.log("APP中的文件有" + JSON.stringify(fileList))
                // App.screen.log(JSON.stringify(fileList));
                AllFileList = "App中的文件有：" + JSON.stringify(fileList);
                
            }
        });

        App.Util.serverRequest(findFileUSB, "GET", true, function (response) {
            if (response) {
                console.log("get usbfile names");
                var fileList = response["storage_path_list"].map(function (element) {
                    var elementObj = {};
                    elementObj.name = element;
                    elementObj.type = "file";
                    return elementObj;
                })
                console.log("USB中的文件有" + JSON.stringify(fileList))
                // App.screen.log(JSON.stringify(fileList));
                AllFileList = AllFileList + "USB中的文件有" + JSON.stringify(fileList);
                
            }
        });
        console.log("控制台输出："+ AllFileList)
        App.screen.log(AllFileList)
    };

    return {
        start: start,
    };
})();
