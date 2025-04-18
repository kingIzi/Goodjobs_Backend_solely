from django.db import models
from myauthentication.models import CustomUser as User


class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_date = models.DateField(auto_now_add=True, blank=True)
    azampay_transaction_id = models.CharField(max_length=1000, blank=True,null=True)
    provider = models.CharField(max_length=1000)
    is_success = models.BooleanField(default=False)
    order_id = models.CharField(max_length=1000)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_number = models.CharField(max_length=1000)

    class Meta:
        ordering = ['-transaction_date']
    def __str__(self):
        return self.user.username


