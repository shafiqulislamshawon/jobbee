"""
Template 3: Minimal Luxury
============================
Aesthetic: Extreme cleanliness, asymmetric elegance, maximum negative space.
- Mostly white canvas
- Black typography dominates
- Mustard yellow ONLY for CTA and deadline date
- Very thin borders
- Asymmetric corner accent (small top-right square)
- Extremely refined typography hierarchy
"""
from PIL import Image, ImageDraw
from .base import BaseTemplate
from ..components import (
    draw_header, draw_job_title, draw_company_name,
    draw_rule, draw_metadata_grid, draw_skill_chips,
    draw_deadline, draw_cta_button, draw_qr_block, draw_section_label,
)
from ..typography import get_font
from ..utils.text import text_width, text_height


class LuxuryTemplate(BaseTemplate):

    MARGIN = 90

    def render(self) -> Image.Image:
        canvas, draw = self.create_canvas()
        W, H = self.width, self.height
        M = self.MARGIN
        job = self.job
        theme = self.theme

        # ── ASYMMETRIC CORNER ACCENT (top-right) ──────────────────────
        accent_sq = 40
        draw.rectangle([W - accent_sq, 0, W, accent_sq], fill=theme.primary)

        # ── HEADER ───────────────────────────────────────────────────
        y = 60
        y = draw_header(
            canvas, draw, W, y,
            company_name=job.company_name,
            portal_name=self.PORTAL_NAME,
            logo_path=job.company_logo,
            theme=theme,
            margin=M,
        )
        y += 56

        # ── THIN TOP RULE ─────────────────────────────────────────────
        draw.line([(M, y), (W - M, y)], fill=theme.text_primary, width=1)
        y += 48

        # ── HIRING LABEL (no badge, just clean text) ──────────────────
        hire_font = get_font('Medium', 18)
        hire_text = "— WE ARE HIRING —"
        hire_w = text_width(hire_text, hire_font)
        draw.text((M, y), hire_text, font=hire_font, fill=theme.text_secondary)
        y += text_height(hire_text, hire_font) + 28

        # ── JOB TITLE (left-aligned, very large) ─────────────────────
        y = draw_job_title(
            draw, W, y, job.title, theme,
            margin=M, align="left",
            max_font_size=76, min_font_size=38,
        )
        y += 20

        # ── COMPANY ───────────────────────────────────────────────────
        y = draw_company_name(draw, W, y, job.company_name, theme, margin=M, align="left")
        y += 52

        # ── THIN SEPARATOR ────────────────────────────────────────────
        draw.line([(M, y), (M + 200, y)], fill=theme.accent_light, width=1)
        y += 40

        # ── METADATA (sparse, left-aligned) ───────────────────────────
        meta_items = [
            ('location',   'Location',        job.location),
            ('salary',     'Salary',           job.salary),
            ('experience', 'Experience',       job.experience),
            ('employment', 'Employment Type',  job.employment_type),
            ('workplace',  'Workplace',        job.workplace_type),
            ('education',  'Education',        job.education),
        ]
        if job.vacancies:
            meta_items.append(('vacancies', 'Vacancies', job.vacancies))

        y = draw_metadata_grid(draw, W, y, meta_items, theme, margin=M, columns=2, row_gap=24)
        y += 32

        # ── KEY SKILLS (minimal styling) ──────────────────────────────
        if job.skills:
            y = draw_section_label(draw, M, y, "Key Skills", theme)
            y += 8
            y = draw_skill_chips(draw, canvas, W, y, job.skills, theme, margin=M, max_rows=2)
            y += 40

        # ── LONG THIN RULE ────────────────────────────────────────────
        draw.line([(M, y), (W - M, y)], fill=theme.accent_light, width=1)
        y += 44

        # ── DEADLINE ─────────────────────────────────────────────────
        if job.deadline:
            y = draw_deadline(draw, W, y, job.deadline, theme)
            y += 44

        # ── CTA (black + mustard) ─────────────────────────────────────
        y = draw_cta_button(draw, W, y, theme, style="black")
        y += 52

        # ── FOOTER ───────────────────────────────────────────────────
        url_font = get_font('Regular', 17)
        portal_url = job.application_url or f"https://jobbee.com/jobs/{job.job_id}"
        draw.text((M, H - M - 20), portal_url, font=url_font, fill=theme.text_secondary)

        if self.show_qr:
            draw_qr_block(canvas, W, H, portal_url, theme, qr_size=90, margin=M)

        # ── BOTTOM THIN RULE ─────────────────────────────────────────
        draw.line([(0, H - 1), (W, H - 1)], fill=theme.text_primary, width=3)

        return canvas
