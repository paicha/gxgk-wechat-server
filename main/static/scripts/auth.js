$(function() {

    function get_auth_result() {
        var intervalId = setInterval(function() {
            $.get(window.location.href + '/result',
            function(res) {
                clearInterval(intervalId);
                $('#loadingToast').fadeOut(100);
                if (res.errmsg === 'ok') {
                    $('.page.msg').show();
                    // 绑定成功3秒后关闭窗口
                    setTimeout(function() {
                        wx.closeWindow();
                    },
                    3000);
                } else {
                    // 绑定失败，显示后端信息
                    $('#err_msg').text(res.errmsg);
                    $('#iosDialog1').fadeIn(200);
                }
            });
        },
        1000);
    }

    $('#submit').tap(function() {
        // 如果正在查询中，则不发起请求
        if ($('#loadingToast').css('display') != 'none') return;
        // 如果正在显示错误信息，则不发起请求
        if ($('.js_tooltips').css('display') != 'none') return;
        var username = $('#username').val().replace(/\s+/g, '');
        var password = $('#password').val().replace(/\s+/g, '');
        // 验证各项信息不为空
        if ( !! username && !!password) {
            $('#loadingToast').fadeIn(100);
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
            $.post(window.location.href, data,
            function(res) {
                if (res.errmsg === 'ok') {
                    get_auth_result();
                }
            });
        } else {
            // 提示输入格式不正确
            $('.js_tooltips').css('display', 'block');
            setTimeout(function() {
                $('.js_tooltips').css('display', 'none');
            },
            3000);
        }
    });
    // 关闭错误弹框
    $('.weui-dialog__btn.weui-dialog__btn_primary').tap(function() {
        $('#iosDialog1').fadeOut(200);
    });
});