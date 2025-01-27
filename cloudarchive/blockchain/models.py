from django.db import models


class GraphicsCard(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    memory_size = models.PositiveIntegerField()  # В МБ
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    MH = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.brand} {self.name}"
    

class CardsUser(models.Model):
    user = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    memory_size = models.PositiveIntegerField()  # В МБ
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    MH = models.FloatField(default=0.0)


class Tokens(models.Model):
    id_user = models.CharField(max_length=1024)
    CLT = models.FloatField(default=300.00)
    NBM = models.FloatField(default=0.00)


class MiningStatus(models.Model):
    user = models.CharField(max_length=64)
    is_mining = models.BooleanField(default=False)


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('buy', 'Покупка'),
        ('sell', 'Продажа'),
    ]

    user = models.CharField(max_length=1024)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES)  # Тип ордера
    amount = models.FloatField()  # Количество монет
    price_per_unit = models.FloatField()  # Цена за монету
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    is_fulfilled = models.BooleanField(default=False)  # Выполнен ли ордер

    def __str__(self):
        return f"{self.user} ({self.order_type}) - {self.amount} монет по {self.price_per_unit} CLT"
