import uuid

from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESSFUL = 'successful', 'Successful'
    FAILED = 'failed', 'Failed'


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        db_index=True,
    )
    transaction_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    provider_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'

    def __str__(self) -> str:
        return f'Payment {self.id} [{self.status}] order={self.order_id}'
