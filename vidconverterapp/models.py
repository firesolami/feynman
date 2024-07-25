from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Summary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summary_title = models.CharField(max_length=300)
    generated_content = models.TextField()

    def __str__(self):
        return self.summary_title
    
# 1:12:58