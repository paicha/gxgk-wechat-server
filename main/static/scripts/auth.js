$(function() {

    function get_auth_result() {
        var intervalId = setInterval(function() {
            $.get(window.location.href + '/result', function(res) {
                clearInterval(intervalId);
                $('#loadingToast').hide();
                if (res.errmsg === 'ok') {
                    $('.page.msg').show();
                    // 绑定成功3秒后关闭窗口
                    setTimeout(function() {
                        wx.closeWindow();
                    }, 3000);
                } else {
                    // 绑定失败，显示后端信息
                    $('#err_msg').text(res.errmsg);
                    $('.weui_dialog_alert').show();
                }
            });
        }, 1000);
    }

    $('#submit').tap(function() {
        var username = $('#username').val().replace(/\s+/g, '');
        var password = $('#password').val().replace(/\s+/g, '');
        // 验证各项信息不为空
        if (!!username && !!password) {
            $('#loadingToast').show();
            // 判断绑定类型
            var data;
            if ($('.page_title').text() === '微信查成绩') {
                data = {
                    studentid: username,
                    studentpwd: password
                };
            } else {
                data = {
                    libraryid: username,
                    librarypwd: password
                };
            }
            // 提交绑定信息
            $.post(window.location.href, data, function(res) {
                if (res.errmsg === 'ok') {
                    get_auth_result();
                }
            });
        } else {
            // 提示输入格式不正确
            $('.js_tooltips').show();
            setTimeout(function() {
                $('.js_tooltips').hide();
            }, 3000);
        }
    });
    // 关闭错误弹框
    $('.weui_btn_dialog.primary').tap(function() {
        $('.weui_dialog_alert').hide();
    });
});
