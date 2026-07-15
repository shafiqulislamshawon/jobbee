def calculate_match_score(job, seeker_profile):
    score = 0
    
    # Skills Match (70%)
    job_skills = [s.strip().lower() for s in job.skills.split(',') if s.strip()]
    seeker_skills = [s.strip().lower() for s in seeker_profile.skills.split(',') if s.strip()]
    
    if job_skills:
        overlap = set(job_skills).intersection(set(seeker_skills))
        skills_score = (len(overlap) / len(job_skills)) * 70
        score += skills_score
    else:
        # If job has no specific skills required, give full skills points if seeker has any skills
        if seeker_skills:
            score += 70
        else:
            score += 35 # Neutral
            
    # Location/Remote Match (20%)
    if job.remote_status == 'REMOTE':
        score += 20
    else:
        score += 10 # Neutral score since seeker doesn't have a specific location preference field
        
    # Experience (10%)
    if seeker_profile.experience.exists():
        score += 10
        
    return min(int(score), 100)
