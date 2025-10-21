from django.db import models


class BlockchainTransaction(models.Model):
    transaction_hash = models.CharField(max_length=66, unique=True)
    submission_id = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash}"
