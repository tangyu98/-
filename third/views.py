from django.http.response import HttpResponse
from django.shortcuts import render
from alipay.aop.api.domain.AlipayOpenAuthTokenAppModel import AlipayOpenAuthTokenAppModel
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipayOpenAuthTokenAppRequest import AlipayOpenAuthTokenAppRequest
from . import zfb_conf
from alipay.aop.api.response.AlipayOpenAuthTokenAppResponse import AlipayOpenAuthTokenAppResponse
from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest
from alipay.aop.api.response.AlipayTradeWapPayResponse import AlipayTradeWapPayResponse

from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.response.AlipayTradeQueryResponse import AlipayTradeQueryResponse


# Create your views here.
def zfb_callback_login(request):
    app_auto_code = request.GET.get("app_auto_code")

    model = AlipayOpenAuthTokenAppModel()
    model.grant_type = "authorization_code"
    model.code = app_auto_code

    client = DefaultAlipayClient(alipay_client_config=zfb_conf.alipay_client_config)

    request = AlipayOpenAuthTokenAppRequest(biz_model=model)

    response_content = client.execute(request)

    response = AlipayOpenAuthTokenAppResponse()

    response.parse_response_content(response_content)

    app_auto_token = response.app_auth_token
    expires = response.expires_in

    app_refresh_token = response.app_refresh_token
    re_expires = response.re_expires_in

    alipay_user_id = response.user_id

    return HttpResponse(response.body)


def order(request):
    from uuid import uuid4
    orderno = uuid4().hex
    subject = "生鲜超市"
    totalmany = 50
    client = DefaultAlipayClient(alipay_client_config=zfb_conf.alipay_client_config)
    model = AlipayTradeWapPayModel()
    model.out_trade_no = orderno
    model.subject = subject
    model.total_amount = totalmany

    req = AlipayTradeWapPayRequest(biz_model=model)
    req.return_url = zfb_conf.ALIPAY_TRADE_PAY_RETURN_URL

    response_content = client.page_execute(req)

    return HttpResponse(response_content)


def pay(request):
    pass
