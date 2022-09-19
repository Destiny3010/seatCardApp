/* Copyright(c) 2015-2017 TOSHIBA TEC CORPORATION, All Rights Reserved. */
App.EventReceiver = (function (global, $, undefined) {
    
    var eventReceiver = function (data) {
        console.log("打印机状态监听" + JSON.stringify(data));
        // Event received in print screen when input processing completes.
        if (data.event_name === "jobs_input_processing_completed") {
            console.log("打印输入处理完成！");
        }
        // Event received in print screen when printing suspended.
        else if (data.event_name === "jobs_suspended") {
            App.screen.log('打印作业暂停！请查看是否缺纸');
            console.log("打印暂停！");
        }
        // Event received in print screen when printing suspended.
        else if (data.job_status.job_type === "print_job" && data.job_status.status === "completed" && data.job_status.status_reason === "success") {
            App.screen.log('打印作业完成！');
            console.log("打印任务完成！");
            App.printJob.show()
        }
    };

    var eventReceiver1 = function (data) {
        //USB状态监听
        if (data.event_name === 'usb_inserted') {
            console.log('USB drive inserted');
            // Set the text in the UI
            // App.screen.usb_status('USB已插入！');
            App.screen.usb_status = true;
        } else if (data.event_name === 'usb_removed') {
            console.log('USB drive removed');
            // Set the text in the UI
            // App.screen.usb_status('USB已拔出！');
            App.screen.usb_status = false;
        }
    };

    return {
        eventReceiver: eventReceiver,
        eventReceiver1: eventReceiver1
    };

})(window, jQuery);