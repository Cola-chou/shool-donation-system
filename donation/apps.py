from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig



class DonationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.donation'
    verbose_name = '捐赠模块'

    def ready(self):
        '''
        date：在您希望在某个特定时间仅运行一次作业时使用
        interval：当您要以固定的时间间隔运行作业时使用
        cron：以crontab的方式运行定时任务
        minutes：设置以分钟为单位的定时器
        seconds：设置以秒为单位的定时器
        '''
        # 创建后台任务调度器
        scheduler = BackgroundScheduler()
        # 添加任务:check_expired_projects 至后台调度器
        from apps.donation.views import check_expired_projects
        scheduler.add_job(check_expired_projects, 'cron', hour=0)
        # 开启任务调度器
        scheduler.start()
