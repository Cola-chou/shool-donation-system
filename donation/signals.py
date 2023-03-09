from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.donation.models import DonationRecord


