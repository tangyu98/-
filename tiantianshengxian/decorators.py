from django.shortcuts import redirect
from django.http.response import JsonResponse


def auto_session(func):
    """
    进行权限认证：
        如果用户登录，则正常返回，否则提示用户登录
    :param func:
    :return:
    """
    def auto_session_warpper(request, *args, **kwargs):

        # 获取登录标记
        user = request.session.get("LOGIN_LOCAL_FLAG")

        if user is None:
            return redirect(to="/login")
            # 获取请求对应的头信息
            # referer = request.headers.get("Referer", None)
            #
            # # 获取请求类型是 同步还是 异步
            # if "X-Requested-With" in request.headers:
            #     if referer is None:
            #         path = "/"
            #     else:
            #         path = referer
            #     # 异步请求, 如果未登录，设置状态码未 318
            #     return JsonResponse(data={"status": False, "msg": "用户未登录", "referer": path}, status=318)
            # else:
            #     if referer is None:
            #         return redirect(to="/?url=/")
            #     return redirect(to="/?url=" + referer)

        # 如果用户登录，则 调用 函数
        return func(request, *args, **kwargs)

    return auto_session_warpper
