from django.db import models

class UploadedImage(models.Model):
    original_image = models.ImageField(upload_to="uploads/")
    processed_image = models.ImageField(upload_to="processed/", blank=True, null=True)
    
