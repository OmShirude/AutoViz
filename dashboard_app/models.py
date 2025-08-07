from django.db import models
from django.contrib.auth.models import User

class UserMappedData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to Django's User model
    query = models.TextField()  # Store long user queries
    chart_id = models.IntegerField()  # Store chart ID reference
    image = models.ImageField(upload_to="charts/", null=True, blank=True)  # Store images (optional)

    def __str__(self):
        return f"Data for {self.user.username}"

class DBMappedData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to Django's User model
    db_type = models.TextField()
    password = models.TextField()  
    host = models.TextField()
    port = models.IntegerField()  
    db_name = models.TextField()

    def __str__(self):
        return f"Data for {self.user.username}"