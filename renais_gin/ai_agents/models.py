from django.db import models


class AIAnalysisLog(models.Model):
    submission_id = models.CharField(max_length=100)
    analysis_type = models.CharField(max_length=50)
    input_data = models.TextField()
    output_data = models.JSONField()
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Analysis for {self.submission_id}"
