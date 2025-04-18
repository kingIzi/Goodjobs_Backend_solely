from django.utils import timezone
from django.db import models
from myauthentication.models import CustomUser as User
from django.db.models.signals import pre_save
from django.dispatch import receiver


class MonetizationOn(models.Model):
    monetization_on = models.BooleanField(default=False)


# Create your models here.


class Plan(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.IntegerField()  # Duration in days or any other unit you prefer
    description = models.CharField(max_length=1000)

    # Additional fields as needed

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True, blank=True)
    end_date = models.DateField(blank=True)
    is_free_trial = models.BooleanField(default=False)
    active = models.BooleanField(default=False)  # Default value is set to True

    # Additional fields as needed

    @property
    def is_active(self):
        current_date = timezone.now().date()
        return self.active and self.end_date >= current_date

    @property
    def remaining_days(self):
        current_date = timezone.now().date()
        remaining = self.end_date - current_date
        return max(remaining.days, 0)

    def __str__(self):
        return f'{self.user.username}--{self.plan}--{self.active}'
    # Additional fields as needed


@receiver(pre_save, sender=Subscription)
def update_subscription_status(sender, instance, **kwargs):
    current_date = timezone.now().date()
    print(f'UPDATE SUBSCRIPTION DATE {instance.end_date}')
    if current_date > instance.end_date:
        instance.active = True
