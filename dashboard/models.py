from django.db import models
from django.contrib.auth.models import User

class UserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='useraccount_set')
    account_number = models.CharField(max_length=20, unique=True)   

    def __str__(self):
        return self.user.username
    

class AccountData(models.Model):
    account_number = models.CharField(max_length=20)
    balance = models.FloatField()
    equity = models.FloatField()
    margin_percentage = models.FloatField()
    open_orders = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account_number
