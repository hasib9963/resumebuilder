import os
import spacy
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from .forms import ResumeForm
from .models import Resume, ResumeAnalysis
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import models
nlp = spacy.load("en_core_web_sm")

def home(request):
    return render(request, 'resumes/home.html')

@login_required
def build_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resume = form.save(commit=False)
                resume.user = request.user
                
                # Handle file upload
                if 'profile_image' in request.FILES:
                    resume.profile_image = request.FILES['profile_image']
                
                resume.save()
                
                # Analyze resume
                analysis = analyze_resume(resume)
                ResumeAnalysis.objects.create(resume=resume, **analysis)
                
                # Generate PDF
                generate_pdf(request, resume)
                
                messages.success(request, "Resume created successfully!")
                return redirect('download_resume', resume_id=resume.id)
                
            except Exception as e:
                messages.error(request, f"Error processing your resume: {str(e)}")
        else:
            # Print form errors to console for debugging
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ResumeForm()
    
    return render(request, 'resumes/build.html', {'form': form})

def analyze_resume(resume):
    text = f"{resume.summary} {resume.skills} {resume.expertise} {resume.languages} {resume.experience} {resume.education}"
    
    # Simple analysis (you can enhance this with proper NLP)
    action_verbs = ['managed', 'led', 'developed', 'created', 'implemented', 'improved', 'achieved', 'optimized']
    words = text.lower().split()
    verb_count = sum(1 for word in words if word in action_verbs)
    
    has_metrics = any(char.isdigit() for char in text)
    
    suggestions = []
    if verb_count < 3:
        suggestions.append("Add more action verbs to strengthen your experience section.")
    if not has_metrics:
        suggestions.append("Include quantifiable achievements (e.g., 'increased sales by 20%').")
    if len(resume.summary.split()) < 30:
        suggestions.append("Consider expanding your summary to better highlight your qualifications.")
    if not resume.profile_image:
        suggestions.append("Add a professional profile photo to make your resume more personal.")
    if not resume.expertise:
        suggestions.append("Add your areas of expertise to showcase your specialized skills.")
    if not resume.languages:
        suggestions.append("Include languages you speak to demonstrate additional capabilities.")
    
    return {
        'score': min(100, verb_count * 10 + (20 if has_metrics else 0) + (10 if resume.profile_image else 0) + (5 if resume.expertise else 0) + (5 if resume.languages else 0)),
        'suggestions': "\n".join(suggestions)
    }

def parse_resume_data(resume):
    """Parse resume data into structured format for the template"""
    # Parse skills
    skills_data = []
    if resume.skills:
        skills_list = []
        for skill_line in resume.skills.splitlines():
            if skill_line.strip():
                skills = [s.strip() for s in skill_line.split(',') if s.strip()]
                skills_list.extend(skills)
        
        if skills_list:
            skills_data.append({
                'category': 'Technical Skills',
                'skills': skills_list
            })
    
    # Parse expertise
    expertise_data = []
    if resume.expertise:
        expertise_list = []
        for expertise_line in resume.expertise.splitlines():
            if expertise_line.strip():
                expertise_items = [e.strip() for e in expertise_line.split(',') if e.strip()]
                expertise_list.extend(expertise_items)
        
        if expertise_list:
            expertise_data.append({
                'category': 'Areas of Expertise',
                'expertise': expertise_list
            })
    
    # Parse languages
    languages_data = []
    if resume.languages:
        for lang_line in resume.languages.splitlines():
            if lang_line.strip():
                parts = [part.strip() for part in lang_line.split('|')]
                if len(parts) >= 2:
                    languages_data.append({
                        'language': parts[0],
                        'proficiency': parts[1]
                    })
                else:
                    languages_data.append({
                        'language': lang_line.strip(),
                        'proficiency': 'Proficient'
                    })
    
    # Parse references
    references_data = []
    if resume.references:
        for ref_line in resume.references.splitlines():
            if ref_line.strip():
                parts = [part.strip() for part in ref_line.split('|')]
                if len(parts) >= 4:
                    references_data.append({
                        'name': parts[0],
                        'profession': parts[1],
                        'phone': parts[2],
                        'email': parts[3]
                    })
                elif len(parts) >= 2:
                    references_data.append({
                        'name': parts[0],
                        'profession': parts[1] if len(parts) > 1 else '',
                        'phone': parts[2] if len(parts) > 2 else '',
                        'email': parts[3] if len(parts) > 3 else ''
                    })
    
    # Parse experience
    experience_data = []
    if resume.experience:
        for exp_line in resume.experience.splitlines():
            if exp_line.strip():
                parts = [part.strip() for part in exp_line.split('|')]
                if len(parts) >= 3:
                    experience_data.append({
                        'title': parts[0],
                        'company': parts[1],
                        'date': parts[2],
                        'description': parts[3] if len(parts) > 3 else '',
                    })
                else:
                    experience_data.append({
                        'title': 'Professional Experience',
                        'description': exp_line.strip()
                    })
    
    # Parse education
    education_data = []
    if resume.education:
        for edu_line in resume.education.splitlines():
            if edu_line.strip():
                parts = [part.strip() for part in edu_line.split('|')]
                if len(parts) >= 3:
                    education_data.append({
                        'degree': parts[0],
                        'institution': parts[1],
                        'date': parts[2],
                        'details': parts[3] if len(parts) > 3 else ''
                    })
                else:
                    education_data.append({
                        'degree': 'Education',
                        'details': edu_line.strip()
                    })
    
    return {
        'skills_data': skills_data,
        'expertise_data': expertise_data,
        'languages_data': languages_data,
        'references_data': references_data,
        'experience_data': experience_data,
        'education_data': education_data
    }

def generate_pdf(request, resume):
    try:
        # Parse the resume data first
        parsed_data = parse_resume_data(resume)
        
        # Create context with both resume object and parsed data
        context = {
            'resume': resume,
            'skills_data': parsed_data['skills_data'],
            'expertise_data': parsed_data['expertise_data'],
            'languages_data': parsed_data['languages_data'],
            'references_data': parsed_data['references_data'],
            'experience_data': parsed_data['experience_data'],
            'education_data': parsed_data['education_data'],
            'MEDIA_URL': settings.MEDIA_URL
        }
        
        html_string = render_to_string('resumes/resume_pdf.html', context)
        
        # CSS for PDF generation
        css_string = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
        }
        """
        
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf_file = f"resume_{resume.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'resumes', pdf_file)
        
        # Create media/resumes directory if it doesn't exist
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        html.write_pdf(target=pdf_path, stylesheets=[CSS(string=css_string)])
        resume.pdf_file = f'resumes/{pdf_file}'
        resume.save()
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        # Create a simple PDF fallback or handle the error as needed

def download_resume(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id)
        if resume.pdf_file and os.path.exists(resume.pdf_file.path):
            response = FileResponse(
                open(resume.pdf_file.path, 'rb'),
                content_type='application/pdf',
                filename=f"{resume.full_name.replace(' ', '_')}_Resume.pdf"
            )
            resume.download_count += 1
            resume.save()
            
            # Store resume_id in session to show success message on dashboard
            request.session['downloaded_resume_id'] = resume_id
            
            # Set response to force download and redirect after download starts
            response['Content-Disposition'] = f'attachment; filename="{resume.full_name.replace(" ", "_")}_Resume.pdf"'
            
            # Use JavaScript to redirect after download starts
            response['X-Redirect-After-Download'] = '/dashboard/'
            
            return response
        else:
            messages.error(request, "PDF file not found. Please regenerate your resume.")
            return redirect('build_resume')
    except Resume.DoesNotExist:
        messages.error(request, "Resume not found.")
        return redirect('build_resume')

@login_required
def dashboard(request):
    user_resumes = Resume.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate total downloads
    total_downloads = user_resumes.aggregate(total_downloads=models.Sum('download_count'))['total_downloads'] or 0
    
    # Calculate average score
    avg_score = 0
    resumes_with_analysis = user_resumes.filter(resumeanalysis__isnull=False)
    if resumes_with_analysis.exists():
        avg_score = resumes_with_analysis.aggregate(avg_score=models.Avg('resumeanalysis__score'))['avg_score']
        avg_score = round(avg_score)
    
    # Check if we just downloaded a resume to show success message
    downloaded_resume_id = request.session.pop('downloaded_resume_id', None)
    if downloaded_resume_id:
        try:
            downloaded_resume = Resume.objects.get(id=downloaded_resume_id)
            messages.success(request, f"Resume '{downloaded_resume.title}' downloaded successfully!")
        except Resume.DoesNotExist:
            pass
    
    return render(request, 'resumes/dashboard.html', {
        'resumes': user_resumes,
        'total_downloads': total_downloads,
        'avg_score': avg_score
    })

@require_POST
def track_download(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        resume.download_count += 1
        resume.save()
        return JsonResponse({'download_count': resume.download_count})
    except Resume.DoesNotExist:
        return JsonResponse({'error': 'Resume not found'}, status=404)

@login_required
def edit_resume(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        
        if request.method == 'POST':
            form = ResumeForm(request.POST, request.FILES, instance=resume)
            if form.is_valid():
                resume = form.save()
                
                # Re-analyze resume
                analysis = analyze_resume(resume)
                ResumeAnalysis.objects.update_or_create(
                    resume=resume,
                    defaults={'score': analysis['score'], 'suggestions': analysis['suggestions']}
                )
                
                # Regenerate PDF
                generate_pdf(request, resume)
                
                messages.success(request, "Resume updated successfully!")
                return redirect('dashboard')
        else:
            form = ResumeForm(instance=resume)
        
        return render(request, 'resumes/build.html', {'form': form, 'editing': True, 'resume': resume})
    
    except Resume.DoesNotExist:
        messages.error(request, "Resume not found.")
        return redirect('dashboard')

@require_POST
@login_required
def delete_resume(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        resume_title = resume.title
        
        # Delete associated files
        if resume.profile_image:
            if os.path.exists(resume.profile_image.path):
                os.remove(resume.profile_image.path)
        if resume.pdf_file:
            if os.path.exists(resume.pdf_file.path):
                os.remove(resume.pdf_file.path)
        
        # Delete the resume
        resume.delete()
        return JsonResponse({'success': True, 'message': f'Resume "{resume_title}" deleted successfully'})
    except Resume.DoesNotExist:
        return JsonResponse({'error': 'Resume not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error deleting resume: {str(e)}'}, status=500)