from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
 user = models.OneToOneField(User, on_delete=models.CASCADE)
 is_onboarded = models.BooleanField(default=False)

 def __str__(self):
  return self.user.username
 
class Wallet(models.Model):
 user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
 name = models.CharField(max_length=100)
 initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
 created_at = models.DateTimeField(auto_now_add=True)

 def __str__(self):
  return self.name

class Category(models.Model):
 CATEGORY_TYPES = (
  ('income', 'Income'),
  ('expense', 'Expense'),
 )

 user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
 name = models.CharField(max_length=100)
 type = models.CharField(max_length=7, choices=CATEGORY_TYPES)

 def __str__(self):
  return f"{self.name} ({self.type})"

class Transaction(models.Model):
 TRANSACTION_TYPES = (
     ('income', 'Income'),
     ('expense', 'Expense'),
 )

 user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
 wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
 category = models.ForeignKey(Category, on_delete=models.CASCADE)
 type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
 amount = models.DecimalField(max_digits=15, decimal_places=2)
 date = models.DateField()
 note = models.TextField(blank=True, null=True)
 created_at = models.DateTimeField(auto_now_add=True)