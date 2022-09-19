// Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

var App = (function () {
    // Public variables
    var appId = '319dc11f-67b2-11ec-acd2-b4692120322f';
    var appToken = {};

    var pre_url = 'http://embapp-local.toshibatec.co.jp:50187/v1.0/'
    var url = {
        copyFile: pre_url + "externaldevice/usb/files/actions/copy",
        copyDir: pre_url + "/externaldevice/usb/directories/actions/copy",
        usbInsertionSubcription: pre_url + "subscription/eventstream/externaldevice/usb",
        deviceStatusEventSubscriptionURL: pre_url + "subscription/eventstream/mfpdevice/status",
        jobEventSubscriptionURL: pre_url + "subscription/eventstream/jobs",
        usbStatus: pre_url + "/externaldevice/usb",

    };

    /* ------------------------------------------------- */
    /* APPLICATION INITIALIZATION */
    /* ------------------------------------------------- */
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }


    var init = function () {

        //绘制打印效果图
        App.drawSample.start('black', 'midlle')

        // 选择框样式
        $(function () {
            $("#select_color").selectable();
            // 默认选择黑色
            $(".ui-state-default").filter(function (index, item) {
                return item.dataset.color == "black";
            }.bind(this)).addClass("ui-selected");
        });

        // 如果改变选择，重新生成示例图
        $('input:radio[name="font_size"]').change(function () {

            console.log($("[name='font_size']:checked").val());
            console.log($(".ui-selected").data("color"));
            App.drawSample.start($(".ui-selected").data("color"), ($("[name='font_size']:checked").val()))

        })
        // 如果改变选择，重新生成示例图
        $("#select_color").selectable({
            selected: function (event, ui) {
                console.log($("[name='font_size']:checked").val());
                console.log($(".ui-selected").data("color"));
                App.drawSample.start($(".ui-selected").data("color"), ($("[name='font_size']:checked").val()))
            }
        });

        // Get Web API access token
        App.appToken['X-WebAPI-AccessToken'] = getCookie('accessToken');

        // Setup SSE receiver
        //监听订阅的事件
        App.Util.subscribeSSE();

        /* Event subscriptions */
        /* This section contains all the event subscriptions that the app needs */
        // Event subscription for USBinsertion event
        App.Util.serverRequest(App.url.usbInsertionSubcription, 'POST', true, function (response) {
            if (response) {
                console.log("USB事件订阅成功！")
            } else {
                console.log("USB事件订阅失败！")
            }
        }, { "event_names": [] });

        // Event subscription for device_adf_paper_changed event.
        App.Util.serverRequest(App.url.deviceStatusEventSubscriptionURL, 'POST', true, function (response) {
            if (response) {
                console.log('Subscription for event : device_adf_paper_changed : success');
            } else {
                console.error('Subscription for event : device_adf_paper_changed : fail');
            }
        }, {
            'event_names': ['device_adf_paper_changed']
        });

        // Event subscription for jobs.
        App.Util.serverRequest(App.url.jobEventSubscriptionURL, 'POST', true, function (response) {
            if (response) {
                console.log('Subscription for event : job : success');
            } else {
                console.error('Subscription for event : job : fail');
            }
        }, {
            "event_names": []
        });


        App.Util.serverRequest(App.url.usbStatus, "GET", true, function (response) {
            if (response) {
                // Set the text in the UI
                if (response.is_inserted) {
                    App.screen.usb_status = true;
                    // App.screen.usb_status("USB已插入！")
                } else {
                    App.screen.usb_status = false;
                    // App.screen.usb_status('USB已拔出！');
                }
            } else {
                console.error("Getting the USB status failed.");
            }
        });
    };


    return {
        appId: appId,
        appToken: appToken,
        url: url,
        init: init
    };
})();
