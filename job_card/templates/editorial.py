"""
Template 1: Editorial Corporate
================================
Aesthetic: High-end business magazine layout.
- Pure white canvas
- Massive black typography
- Thin mustard-yellow horizontal rules
- Generous whitespace, editorial spacing
- Two-column metadata grid
- Clean skill chips
"""
from PIL import Image, ImageDraw
from .base import BaseTemplate
from ..components import (
    draw_header, draw_hiring_badge, draw_job_title, draw_company_name,
    draw_rule, draw_metadata_grid, draw_skill_chips, draw_description,
    draw_deadline, draw_cta_button, draw_qr_block, draw_section_label,
)
from ..typography import get_font
from ..utils.text import text_width, text_height


class EditorialTemplate(BaseTemplate):

    MARGIN = 80

    def render(self) -> Image.Image:
        canvas, draw = self.create_canvas()
        W, H = self.width, self.height
        M = self.MARGIN
        job = self.job
        theme = self.theme

        # ── 1. HEADER ────────────────────────────────────────────────
        y = 64
        y = draw_header(
            canvas, draw, W, y,
            company_name=job.company_name,
            portal_name=self.PORTAL_NAME,
            logo_path=job.company_logo,
            theme=theme,
            margin=M,
        )
        y += 40

        # ── 2. ACCENT RULE ───────────────────────────────────────────
        draw.rectangle([M, y, M + 80, y + 4], fill=theme.primary)
        y += 4 + 44

        # ── 3. "WE ARE HIRING" BADGE ─────────────────────────────────
        y = draw_hiring_badge(draw, W, y, theme, align="left")
        y += 36

        # ── 4. JOB TITLE ─────────────────────────────────────────────
        y = draw_job_title(
            draw, W, y, job.title, theme,
            margin=M, align="left",
            max_font_size=72, min_font_size=36,
        )
        y += 16

        # ── 5. COMPANY NAME ──────────────────────────────────────────
        y = draw_company_name(draw, W, y, job.company_name, theme, margin=M, align="left")
        y += 36

        # ── 6. RULE ──────────────────────────────────────────────────
        y = draw_rule(draw, W, y, theme.accent_light, margin=M, thickness=1)
        y += 36

        # ── 7. METADATA GRID ─────────────────────────────────────────
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

        y = draw_metadata_grid(draw, W, y, meta_items, theme, margin=M, columns=2, row_gap=28)
        y += 28

        # ── 8. RULE ──────────────────────────────────────────────────
        y = draw_rule(draw, W, y, theme.accent_light, margin=M, thickness=1)
        y += 28

        # ── 9. DESCRIPTION ───────────────────────────────────────────
        if job.description:
            y = draw_description(draw, W, y, job.description, theme, margin=M, max_lines=3)
            y += 28

        # ── 10. KEY SKILLS ───────────────────────────────────────────
        if job.skills:
            y = draw_section_label(draw, M, y, "Key Skills", theme)
            y += 8
            y = draw_skill_chips(draw, canvas, W, y, job.skills, theme, margin=M, max_rows=2)
            y += 32

        # ── 11. RULE ─────────────────────────────────────────────────
        y = draw_rule(draw, W, y, theme.accent_light, margin=M, thickness=1)
        y += 36

        # ── 12. DEADLINE ─────────────────────────────────────────────
        if job.deadline:
            y = draw_deadline(draw, W, y, job.deadline, theme, margin=M)
            y += 40

        # ── 13. CTA BUTTON ───────────────────────────────────────────
        y = draw_cta_button(draw, W, y, theme, style="black")
        y += 48

        # ── 14. FOOTER: PORTAL URL + QR ──────────────────────────────
        url_font = get_font('Regular', 18)
        portal_url = job.application_url or f"https://jobbee.com/jobs/{job.job_id}"
        draw.text((M, H - M - 20), portal_url, font=url_font, fill=theme.text_secondary)

        if self.show_qr:
            draw_qr_block(canvas, W, H, portal_url, theme, qr_size=100, margin=M)

        # ── BOTTOM ACCENT LINE ────────────────────────────────────────
        draw.rectangle([0, H - 8, W, H], fill=theme.primary)

        return canvas
