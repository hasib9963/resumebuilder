from django.db import models
from django.contrib.auth.models import User
import os

def resume_upload_path(instance, filename):
    return f'resumes/user_{instance.user.id}/{filename}'

def profile_image_upload_path(instance, filename):
    return f'profile_images/user_{instance.user.id}/{filename}'

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to=profile_image_upload_path, null=True, blank=True)
    summary = models.TextField()
    skills = models.TextField(help_text="Enter skills separated by commas or new lines")
    expertise = models.TextField(help_text="Enter your areas of expertise separated by commas or new lines", blank=True)
    languages = models.TextField(help_text="Format: Language | Proficiency Level (e.g., English | Fluent)", blank=True)
    references = models.TextField(help_text="Format: Name | Profession | Phone | Email (one per line)", blank=True)
    experience = models.TextField(help_text="Format: Job Title | Company | Dates | Description")
    education = models.TextField(help_text="Format: Degree | Institution | Dates | Details")
    address = models.CharField(max_length=200, blank=True)
    linkedin = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(upload_to=resume_upload_path, null=True, blank=True)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.full_name} - {self.title}"

class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE)
    score = models.IntegerField()
    suggestions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.resume.title}"