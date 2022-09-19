/* Copyright(c) 2015-2017 TOSHIBA TEC CORPORATION, All Rights Reserved. */
App.Util = (function (global, $, undefined) {

    // For beep sound
    var _isEwb = (typeof __ewb__ !== "undefined");

    var soundBeep = function () {
        if (_isEwb) {
            __ewb__.beep("normal");
        }
    };

    /* ------------------------------------------------- */
    /* SSE SUBSCRIPTION */
    /* ------------------------------------------------- */
    // 监听打印机状态（打印中、打印完毕等）
    var subscribeSSE = function () {
        console.log('Subscribing for SSE');
        console.log('添加监听打印机状态的事件！')
        global.EventManager = new cAPIEventManager(App.appId, App.appToken['X-WebAPI-AccessToken']);
        //打印事件
        global.EventManager.addEventListener(App.EventReceiver.eventReceiver);
        //USB事件
        global.EventManager.addEventListener(App.EventReceiver.eventReceiver1);
        global.EventManager.startAPIEvents();
    };

    /* ------------------------------------------------- */
    /* AJAX REQUEST */
    /* ------------------------------------------------- */

    var serverRequest = function (URL, method, asyncStatus, callback, jsonData) {
        console.log("Request URL: " + URL + ", Method: " + method);
        
        if (jsonData) {
            jsonData = JSON.stringify(jsonData);
            console.log("POST Data : " + jsonData);
        }

        $.ajax({
            url: URL,
            type: method,
            async: asyncStatus,
            headers: App.appToken,
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            cache: true,
            success: function (response) {
                console.log("Response Data: " + JSON.stringify(response));
                callback(response);
            },
            error: function (xhr, status, error) {
                console.error(xhr.status + ', ' + status + ', ' + error);
                console.error(xhr.responseText);
                callback(null);
            }
        });
    };

    return {
        serverRequest: serverRequest,
        subscribeSSE: subscribeSSE,
        soundBeep: soundBeep,
    };

})(window, jQuery);