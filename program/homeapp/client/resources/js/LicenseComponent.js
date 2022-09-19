var LicenseComponent = (function() {

    var pchtml = '<div id="divLicense" style="z-index:9998;position:fixed;top:0;left:0;margin:0px;height:100%;width:100%;background-color: #eee;display:none;">\
    <div style="z-index:9999;position:absolute;top:0;left:0;margin:10px;height:300px;width:700px;background-color: #3E3F44;">\
    <div style="width:100%;height:50px;text-align:center;background-color:#1A1A1A;color:#F1F1F2;font-size: 20px;position:absolute;top:0;left:0;">\
		<label style="position:relative; top: 10px;">应用授权</label>\
	</div>\
	<div style="width:100%;height:250px;position:absolute;top:50px;left:0;">\
        <div style="width:50%;height:100%;position:absolute;top:0;left:0;">\
			<div id="divSolutionWebQr" style="position:absolute;top:5%;left:20%">\
			</div>\
		</div>\
		<div style="width:50%;height:100%;position:absolute;top:0;left:50%;color:#F1F1F2;">\
            <label style="position:absolute;top:5%;left:2%;font-size:20px;color:#F1F1F2;">请扫描二维码或点击获取授权码</label>\
			<input id="txtLicenseCode" type="text" placeholder="请输入7位授权码" style="input::-webkit-input-placeholder: #888;position: absolute;top: 24%;left: 2%;font-size: 20px;line-height: 40px;background-color: #1A1A1A;border: 2px #F1F1F2 solid;color: #F1F1F2;text-align: center;width: 94.5%;"/>\
			<button id="btnLicenseAuthrize" style="position: absolute;top: 52%;left: 2%;font-size: 20px;background-color: #5E606A;line-height: 40px;width: 94.5%;color: #F1F1F2;border: 2px #ddd solid;border-radius: 3px;">授权</button>\
			<label id="lblLicenseValidateMsg" style="position:absolute;top:77%;left:2%;font-size:20px;color:#DC143C;"></label>\
            <a id="aSolutionWeb" target="_blank" href="" style="position:absolute;top:77%;left:67%;font-size:20px;color:#6699cc;">获取授权码</a>\
		</div>\
	</div>\
</div></div>';

    var html = '<div id="divLicense" style="z-index:9999;position:fixed;top:0;left:0;margin:1%;height:97%;width:98%;background-color: #3E3F44;display:none;">\
	<div style="width:100%;height:10%;text-align:center;background-color:#1A1A1A;color:#F1F1F2;font-size: 3vw;position:absolute;top:0;left:0;">\
		<label style="position:relative; top: 1vh;">应用授权</label>\
	</div>\
	<div style="width:100%;height:90%;position:absolute;top:10%;left:0;">\
		<div style="width:50%;height:100%;position:absolute;top:0;left:0;">\
			<label style="position:absolute;top:15%;left:11%;font-size:2.5vw;color:#F1F1F2;">请扫描二维码或访问网址获取授权码</label>\
			<div id="divSolutionWebQr" style="height:40vh;width:40vh;position:absolute;top:27%;left:28%">\
			</div>\
			<label style="color:#ddd;position:absolute;top:78%;left:7%;font-size:1.8vw;">https://solution.toshiba-tec.com.cn/license/embedded</label>\
		</div>\
		<div style="width:50%;height:100%;position:absolute;top:0;left:50%;color:#F1F1F2;">\
			<input id="txtLicenseCode" type="text" placeholder="请输入7位授权码" style="input::-webkit-input-placeholder: #888;position: absolute;top: 25%;left: 2%;font-size: 3.5vw;line-height: 8vw;background-color: #1A1A1A;border: 2px #F1F1F2 solid;color: #F1F1F2;text-align: center;width: 94%;"/>\
			<button id="btnLicenseAuthrize" style="position: absolute;top: 47%;left: 2%;font-size: 3.5vw;background-color: #5E606A;line-height: 8vw;width: 94.5%;color: #F1F1F2;border: 2px #ddd solid;border-radius: 3px;">授权</button>\
			<label id="lblLicenseValidateMsg" style="position:absolute;top:68%;left:2%;font-size:2.5vw;color:#DC143C;"></label>\
		</div>\
	</div>\
</div>';

    var show = function() {
        $("#divLicense").show();
    };

    var hide = function() {
        $("#divLicense").hide();
    };

    var errMsg = function(msg) {
        $("#lblLicenseValidateMsg").text(msg);
    };

    var appendHtml2Body = function() {
        if (isMfpClient())
            $("body").append(html);
        else
            $("body").append(pchtml);
    };

    var appId = "";

    var getCookie = function(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2)
            return parts.pop().split(";").shift();
    };

    var isMfpClient = function() {
        return navigator.userAgent.indexOf("EWB/") > -1;
    }

    var request = function(method, url, data, timeout, isClientApi) {

        var baseUrl = isClientApi ? "http://embapp-local.toshibatec.co.jp:50187/v1.0" : ('/server/' + appId);
        // 如果不是复合机端，则是SettingsApp
        if (!isMfpClient())
            var baseUrl = "/aplpx/server/" + appId;
        return $.ajax({
            url: baseUrl + url,
            type: method,
            async: true,
            contentType: 'application/json',
            dataType: 'json',
            data: data,
            cache: false,
            timeout: timeout || 15000,
            headers: { 'X-WebAPI-AccessToken': getCookie("accessToken") },
        });
    };
    var get = function(url, queries, timeout, isClientApi) {
        return request('GET', url, queries, timeout, isClientApi);
    };
    var post = function(url, payloads, timeout, isClientApi) {
        return request('POST', url, JSON.stringify(payloads), timeout, isClientApi);
    };
    var put = function(url, payloads, timeout, isClientApi) {
        return request('PUT', url, JSON.stringify(payloads), timeout, isClientApi);
    };
    var patch = function(url, payloads, timeout, isClientApi) {
        return request('PATCH', url, JSON.stringify(payloads), timeout, isClientApi);
    };
    var del = function(url, queries, timeout, isClientApi) {
        return request('DELETE', url, queries, timeout, isClientApi);
    };

    var buildQr = function() {
        $.when(
            get('/mfpdevice/capability', {}, undefined, true),
            get('/app/context/self', {}, undefined, true)
        ).done(function(capability, appcontext) {
            console.log(capability);
            console.log(appcontext);
            var sn = capability[0]["serial_no"];
            var modelName = capability[0]["model_name"];
            var appId = appcontext[0]["app_id"]
            var appVersion = appcontext[0]["app_version"]
            var qrValue = 'https://solution.toshiba-tec.com.cn/license/embedded?sn=' + sn + '&mn=' + modelName + '&appid=' + appId + '&appv=' + appVersion
            var qrcode = new QRCode(document.getElementById('divSolutionWebQr'), {
                text: qrValue,
                typeNumber: 1,
                colorDark: '#F1F1F2',
                colorLight: '#3E3F44',
                correctLevel: QRCode.CorrectLevel.H,
            });
            if (isMfpClient()) {
                $("#divSolutionWebQr img").css('height', '40vh');
                $("#divSolutionWebQr img").css('width', '40vh');
            } else {
                $("#divSolutionWebQr img").css('height', '220px');
                $("#divSolutionWebQr img").css('width', '220px');
                $('#aSolutionWeb').attr('href', qrValue);
            }

        })
    };

    var verifyLicense = function() {
        return post("/app/license/verify", {
                "license_category": 1,
                "license_code": $("#txtLicenseCode").val()
            })
            .then(function(resp) {
                if (resp.is_valid) {
                    hide();
                    runAuthrizedEvents();
                } else
                    errMsg(resp.err_msg);
            });
    };

    var checkLicenseStatus = function() {
        return get("/app/license/status", {})
            .then(function(resp) {
                if (resp.is_valid) {
                    console.log("license已授权！");
                    hide();
                    runAuthrizedEvents();
                } else {
                    console.log("license未授权！");
                    show();
                }
            })
            .fail(function(error, t, e) {
                console.log(error);
                console.log(t);
                console.log(e);
            });
    };

    var removeLicense = function() {
        return del("/app/license/remove", {})
            .then(function(resp) {
                console.log("license已删除！");
            });
    };

    var eventBind = function() {
        $("#btnLicenseAuthrize").click(function() {
            var licenseCode = $("#txtLicenseCode").val();
            if (licenseCode.length == 7) {
                var licenceType = licenseCode.substring(0, 1);
                if (licenceType == '1' || licenceType == '2' || licenceType == '3' || licenceType == '9')
                    verifyLicense();
                else
                    errMsg("License码不合法！");
            } else
                errMsg("请输入7位License码！");
        });
    };

    var onAuthrizedEvents = [];
    var runAuthrizedEvents = function() {
        onAuthrizedEvents.forEach(function(eventFunc) {
            eventFunc();
        });
    };

    // 返回promise
    var load = function(appid) {
        var def = $.Deferred();
        // 订阅验证成功事件
        onAuthrizedEvents.push(function() {
            def.resolve(true);
        });
        // Settings App须传入AppId
        if (appid) {
            appId = appid;
            appendHtml2Body();
            buildQr();
            eventBind();
            checkLicenseStatus();
        }
        // Home App不需要传入AppId
        else
            get('/app/context/self', {}, undefined, true)
            .then(function(resp) {
                appId = resp["app_id"];
                appendHtml2Body();
                buildQr();
                eventBind();
                checkLicenseStatus();
            });
        return def;
    };

    return {
        Load: load
    }

})();

// 使用说明：

// HomeApp依赖库：jquery2.1.3，qrcode.min.js
// SettingsApp依赖库：jquery2.1.3

// 调用：

// HomeApp:
// LicenseComponent.Load()
//  .then(function(){
//      ……
//   });

// SettingsApp:
// LicenseComponent.Load("df59d370-7b4a-41da-be74-7cabc26bfefd")
//  .then(function(){
//      ……
//   });

// 注1：SettingsApp须传入参数“当前APPID”
// 注2：Load方法返回jquery promise对象，then将在验证已授权时，或用户输入授权码验证成功时执行。