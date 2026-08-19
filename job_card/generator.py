"""
generator.py — Core orchestrator for the Job Card Image Generator.

Usage (standalone Python):
    from job_card.generator import generate_job_card
    from job_card.models import JobPost

    job = JobPost(job_id="123", title="Senior Software Engineer", ...)
    path = generate_job_card(job, template="editorial", show_qr=True)
    print(f"Image saved to: {path}")

Usage (Django integration):
    from job_card.generator import generate_job_card_from_django_job
    path = generate_job_card_from_django_job(job_instance, template="bold")
"""
import os
from PIL import Image

from .models import JobPost
from .themes import BRAND_THEME, ThemeColors

# Template sizes (width, height)
SIZES = {
    "portrait":   (1080, 1350),
    "square":     (1080, 1080),
    "tall":       (1200, 1500),
    "landscape":  (1200, 628),
}

TEMPLATE_NAMES = ("editorial", "bold", "luxury")


def _get_template_class(template_name: str):
    if template_name == "editorial":
        from .templates.editorial import EditorialTemplate
        return EditorialTemplate
    elif template_name == "bold":
        from .templates.bold import BoldTemplate
        return BoldTemplate
    elif template_name == "luxury":
        from .templates.luxury import LuxuryTemplate
        return LuxuryTemplate
    else:
        raise ValueError(f"Unknown template: '{template_name}'. Choose from: {TEMPLATE_NAMES}")


def generate_job_card(
    job: JobPost,
    template: str = "editorial",
    size: tuple[int, int] | str = "portrait",
    show_qr: bool = True,
    theme: ThemeColors = None,
    output_dir: str = None,
) -> str:
    """
    Generate a job card image and save it to disk.

    Args:
        job:        JobPost dataclass with all job details.
        template:   One of 'editorial', 'bold', 'luxury'.
        size:       Canvas size — named string ('portrait', 'square', 'tall', 'landscape')
                    or explicit tuple e.g. (1080, 1350).
        show_qr:    Whether to include a QR code.
        theme:      Optional custom ThemeColors. Defaults to brand theme.
        output_dir: Directory to save the output. Defaults to 'media/job_cards'.

    Returns:
        Absolute path to the saved PNG image.
    """
    # Resolve size
    if isinstance(size, str):
        canvas_size = SIZES.get(size, SIZES["portrait"])
    else:
        canvas_size = size

    # Resolve output directory
    if output_dir is None:
        # Try to use Django's MEDIA_ROOT if available
        try:
            from django.conf import settings
            output_dir = os.path.join(settings.MEDIA_ROOT, "job_cards")
        except Exception:
            output_dir = os.path.join(os.getcwd(), "media", "job_cards")

    os.makedirs(output_dir, exist_ok=True)

    # Resolve filename
    filename = f"job_{job.job_id}_{template}.png"
    output_path = os.path.join(output_dir, filename)

    # Instantiate and render
    TemplateClass = _get_template_class(template)
    renderer = TemplateClass(job=job, size=canvas_size, theme=theme or BRAND_THEME, show_qr=show_qr)
    image: Image.Image = renderer.render()

    # Save
    image.save(output_path, "PNG", optimize=True)
    return output_path


def generate_all_templates(
    job: JobPost,
    size: tuple[int, int] | str = "portrait",
    show_qr: bool = True,
    theme: ThemeColors = None,
    output_dir: str = None,
) -> dict[str, str]:
    """
    Generate all 3 templates for a job and return a dict of {template: path}.
    """
    return {
        name: generate_job_card(job, template=name, size=size, show_qr=show_qr, theme=theme, output_dir=output_dir)
        for name in TEMPLATE_NAMES
    }


def generate_job_card_from_django_job(django_job, template: str = "editorial", show_qr: bool = True) -> str:
    """
    Django integration helper. Converts a Django job model instance to a
    JobPost dataclass and generates the card.

    Expects the Django job model to have fields matching JobPost (or similar).
    """
    try:
        logo_path = None
        if hasattr(django_job, 'employer') and hasattr(django_job.employer, 'company_logo'):
            logo_field = django_job.employer.company_logo
            if logo_field:
                logo_path = logo_field.path
    except Exception:
        logo_path = None

    # Build the application URL
    try:
        from django.urls import reverse
        from django.conf import settings
        base = getattr(settings, 'SITE_URL', 'https://jobbee.com')
        app_url = f"{base}/jobs/{django_job.pk}/"
    except Exception:
        app_url = f"https://jobbee.com/jobs/{django_job.pk}/"

    job = JobPost(
        job_id=str(getattr(django_job, 'pk', 'unknown')),
        title=str(getattr(django_job, 'title', '') or ''),
        company_name=str(getattr(getattr(django_job, 'employer', None), 'company_name', '') or ''),
        company_logo=logo_path,
        location=_safe_str(getattr(django_job, 'location', None)),
        employment_type=_safe_str(
            getattr(django_job, 'get_employment_type_display', lambda: None)()
            or getattr(django_job, 'employment_type', None)
        ),
        workplace_type=_safe_str(
            getattr(django_job, 'get_workplace_type_display', lambda: None)()
            or getattr(django_job, 'workplace_type', None)
        ),
        salary=_format_salary(django_job),
        experience=_safe_str(getattr(django_job, 'experience', None)),
        education=_safe_str(getattr(django_job, 'education', None)),
        vacancies=str(django_job.vacancies) if getattr(django_job, 'vacancies', None) else None,
        category=_safe_str(getattr(django_job, 'category', None)),
        deadline=_safe_str(getattr(django_job, 'deadline', None)),
        description=_safe_str(getattr(django_job, 'description', None)),
        skills=_extract_skills(django_job),
        application_url=app_url,
    )

    return generate_job_card(job, template=template, show_qr=True)


def _safe_str(value) -> str | None:
    """Safely convert any Django field value to a plain Python string."""
    if value is None:
        return None
    try:
        s = str(value).strip()
        return s if s else None
    except Exception:
        return None


def _format_salary(job) -> str | None:
    """Try to build a nice salary string from a Django job model."""
    try:
        min_s = getattr(job, 'min_salary', None)
        max_s = getattr(job, 'max_salary', None)
        if min_s and max_s:
            return f"{min_s:,} – {max_s:,}"
        elif min_s:
            return f"From {min_s:,}"
        elif hasattr(job, 'salary'):
            return str(job.salary)
    except Exception:
        pass
    return None


def _extract_skills(job) -> list[str]:
    """Extract skills from a Django job model as a list of strings."""
    try:
        skills_field = getattr(job, 'skills', None)
        if skills_field is None:
            return []
        if isinstance(skills_field, str):
            return [s.strip() for s in skills_field.split(',') if s.strip()]
        if hasattr(skills_field, 'all'):
            return [str(s) for s in skills_field.all()]
        return list(skills_field)
    except Exception:
        return []
