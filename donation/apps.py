from django.apps import AppConfig


class DonationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.donation'
    verbose_name = '捐赠板块'

    # def ready(self):
    #     import apps.donation.signals
