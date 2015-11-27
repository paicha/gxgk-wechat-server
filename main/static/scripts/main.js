$(function() {
    $('#submit').tap(function() {
        var username = $('#username').val().replace(/\s+/g, '');
        var password = $('#password').val().replace(/\s+/g, '');
        var openid = $('#openid').val();
        // 验证各项信息不为空
        if (!!username && !!password && !!openid) {
            $('#loadingToast').show();
            // 判断绑定类型
            if ($('.page_title').text() == '微信查成绩') {
                post_url = '/auth-score';
                data = {
                    studentid: username,
                    studentpwd: password,
                    openid: openid
                };
            } else {
                post_url = '/auth-library';
                data = {
                    libraryid: username,
                    librarypwd: password,
                    openid: openid
                };
            }
            // 提交绑定信息
            $.post(post_url, data, function(res) {
                $('#loadingToast').hide();
                if (res.errcode === 0 && res.errmsg === 'ok') {
                    $('.page.msg').show()
                        // 绑定成功3秒后关闭窗口
                    setTimeout(function() {
                        wx.closeWindow();
                    }, 3000);
                } else {
                    // 绑定失败，显示后端信息
                    $('#err_msg').text(res.errmsg);
                    $('.weui_dialog_alert').show();
                }
            })
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
