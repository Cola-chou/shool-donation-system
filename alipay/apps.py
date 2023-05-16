from django.apps import AppConfig


class AlipayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.alipay'
    verbose_name = '阿里支付网关'
