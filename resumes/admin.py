from django.contrib import admin
from .models import Resume, ResumeAnalysis

class ResumeAnalysisInline(admin.StackedInline):
    model = ResumeAnalysis

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'email', 'created_at')
    inlines = [ResumeAnalysisInline]

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'score', 'created_at')