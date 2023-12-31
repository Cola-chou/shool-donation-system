from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from alipay import AliPay, AliPayConfig
import time
from django.conf import settings

from apps.item.models import DonationItem


def pay(request, item_id):
    # 支付宝网页下载的证书不能直接被使用，需要加上头尾
    # 你可以在此处找到例子： tests/certs/ali/ali_private_key.pem
    app_private_key_string = open(r"E:\DJANGO\universityDonationSystem\mysystem\keys\应用私钥RSA2048-敏感数据，请妥善保管.txt").read()
    alipay_public_key_string = open(r"E:\DJANGO\universityDonationSystem\mysystem\keys\应用公钥RSA2048.txt").read()
    print(reverse('alipay:pay_result'))
    alipay = AliPay(
        appid="2021000122689626",
        app_notify_url=None,  # 默认回调 url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认 False
    )
    order_item = DonationItem.objects.get(id=item_id)
    order = str(order_item.donation_record)
    print(order_item)
    # 生成登录支付宝连接
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_item.id,
        total_amount=str(order_item.price * order_item.quantity),
        subject=f"捐赠清单：{order}",
        return_url='http://127.0.0.1:8000' + reverse('alipay:pay_result')  # 回调路由
    )

    # 沙箱环境电脑网站支付网关：
    alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
    return redirect(alipay_url)


def pay_result(request):
    """
    支付完成后，跳转回的地址
    :param request:
    :return:
    """
    query_dict = request.GET
    data = query_dict.dict()
    # 获取并从请求参数中剔除signature
    signature = data.pop('sign')

    app_private_key_string = open(r"E:\DJANGO\universityDonationSystem\mysystem\keys\应用私钥RSA2048-敏感数据，请妥善保管.txt").read()
    alipay_public_key_string = open(r"E:\DJANGO\universityDonationSystem\mysystem\keys\应用公钥RSA2048.txt").read()

    # 创建支付宝支付对象
    alipay = AliPay(
        appid="2021000122689626",
        app_notify_url=None,  # 默认回调 url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认 False
    )

    # 校验请求是否从支付宝发出
    success = alipay.verify(data, signature)
    if success:
        id = data.get('out_trade_no')
        # print(id)
        # 修改记录状态并保存
        DonationItem.objects.filter(id=id).update(status='1')
        item = DonationItem.objects.get(id=id)
        project_id = item.donation_record.donation_project_id
        item.save()
        request.session['payment_success'] = 'success'
    else:
        request.session['payment_success'] = 'failed'
    return redirect(reverse('donation:project_detail', kwargs={'pk': project_id}))
