from django.apps import AppConfig


class ItemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.item'
    verbose_name = '物资模块'

    # def ready(self):
    #     import apps.item.signals
