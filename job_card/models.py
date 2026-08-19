from dataclasses import dataclass
from typing import Optional, List

@dataclass
class JobPost:
    job_id: str
    title: str
    company_name: str
    company_logo: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    workplace_type: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    vacancies: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    application_url: Optional[str] = None

    def __post_init__(self):
        if self.skills is None:
            self.skills = []
