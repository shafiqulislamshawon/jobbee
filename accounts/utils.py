def analyze_resume(seeker_profile):
    score = 0
    missing = []
    suggestions = []
    
    if seeker_profile.resume:
        score += 25
    else:
        missing.append("Resume Document")
        suggestions.append("Upload a PDF resume to improve visibility.")
        
    if seeker_profile.skills:
        skills_list = [s.strip() for s in seeker_profile.skills.split(',') if s.strip()]
        if len(skills_list) >= 3:
            score += 25
        elif len(skills_list) > 0:
            score += 10
            suggestions.append("List at least 3 skills to get better job matches.")
    else:
        missing.append("Skills")
        suggestions.append("Add skills to improve your match score.")
        
    if seeker_profile.experience.exists():
        score += 25
    else:
        missing.append("Experience")
        suggestions.append("Add your work experience to stand out to employers.")
        
    if seeker_profile.education.exists():
        score += 25
    else:
        missing.append("Education")
        suggestions.append("Add your educational background.")
        
    if not seeker_profile.portfolio_url:
        suggestions.append("Consider adding a portfolio or LinkedIn URL.")
        
    seeker_profile.resume_score = min(score, 100)
    seeker_profile.missing_skills = ", ".join(missing)
    seeker_profile.resume_suggestions = "\n".join(suggestions)
    seeker_profile.save()
