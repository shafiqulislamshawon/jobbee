def analyze_resume(seeker_profile):
    score = 0
    missing = []
    suggestions = []
    
    if not seeker_profile.profile_picture:
        missing.append("Profile Picture")
        suggestions.append("Upload a professional headshot.")
        
    if not seeker_profile.full_name or not seeker_profile.phone_number or not seeker_profile.location:
        missing.append("Basic Info")
        suggestions.append("Complete your basic contact details (Name, Phone, Location).")
        
    if seeker_profile.career_summary:
        pass
    else:
        missing.append("Career Summary")
        suggestions.append("Add a career summary to introduce yourself to employers.")
        
    if seeker_profile.skills:
        skills_list = [s.strip() for s in seeker_profile.skills.split(',') if s.strip()]
        if len(skills_list) < 3:
            suggestions.append("List at least 3 skills to get better job matches.")
    else:
        missing.append("Skills")
        suggestions.append("Add skills to improve your match score.")
        
    has_education = seeker_profile.education.exists()
    has_experience = seeker_profile.experience.exists()
    
    if not has_education and not has_experience:
        missing.append("Background")
        suggestions.append("Add your education or work experience.")
        
    if not seeker_profile.portfolio_url and not seeker_profile.linkedin_url and not seeker_profile.github_url:
        missing.append("Social Links")
        suggestions.append("Add a LinkedIn, GitHub, or Portfolio URL.")
        
    if not seeker_profile.languages:
        missing.append("Languages")
        suggestions.append("Add languages you speak.")
        
    if not seeker_profile.extracurricular_activities:
        missing.append("Extracurricular Activities")
        suggestions.append("Add extracurricular activities to show your well-roundedness.")
        
    if not seeker_profile.certifications.exists():
        missing.append("Certifications")
        suggestions.append("Add certifications to validate your skills.")
        
    if not seeker_profile.references.exists():
        missing.append("References")
        suggestions.append("Add references to build credibility.")
        
    seeker_profile.resume_score = seeker_profile.get_completion_percentage()
    seeker_profile.missing_skills = ", ".join(missing)
    seeker_profile.resume_suggestions = "\n".join(suggestions)
    seeker_profile.save()
