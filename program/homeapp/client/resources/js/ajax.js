// Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

App.ajax = (function() {
    // Constants
    var _TIMEOUT = 15000;

    var request = function(method, url, data, timeout) {
        return $.ajax({
            url: '/server/' + App.appId + url,
            type: method,
            async: true,
            contentType: 'application/json',
            dataType: 'json',
            data: data,
            cache: false,
            timeout: timeout || _TIMEOUT,
            headers: {'X-WebAPI-AccessToken': App.appToken['X-WebAPI-AccessToken']},
        });
    };

    var get = function(url, queries, timeout) {
        return request('GET', url, queries, timeout);
    };

    var post = function(url, payloads, timeout) {
        return request('POST', url, JSON.stringify(payloads), timeout);
    };

    var put = function(url, payloads, timeout) {
        return request('PUT', url, JSON.stringify(payloads), timeout);
    };

    var patch = function(url, payloads, timeout) {
        return request('PATCH', url, JSON.stringify(payloads), timeout);
    };

    var delete_ = function(url, queries, timeout) {
        return request('DELETE', url, queries, timeout);
    };

    return {
        get: get,
        post: post,
        put: put,
        patch: patch,
        delete: delete_,
    };
})();
