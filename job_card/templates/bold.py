"""
Template 2: Bold Recruitment
==============================
Aesthetic: High visual impact, scroll-stopping Facebook design.
- White background
- Large mustard-yellow left accent stripe
- Prominent "WE ARE HIRING" badge (centered)
- Giant black job title
- Clean centered layout
- Strong, readable metadata
"""
from PIL import Image, ImageDraw
from .base import BaseTemplate
from ..components import (
    draw_header, draw_hiring_badge, draw_job_title, draw_company_name,
    draw_rule, draw_metadata_grid, draw_skill_chips,
    draw_deadline, draw_cta_button, draw_qr_block, draw_section_label,
)
from ..typography import get_font
from ..utils.text import text_width, text_height
from ..utils.image import hex_to_rgb


class BoldTemplate(BaseTemplate):

    MARGIN = 100
    STRIPE_WIDTH = 16

    def render(self) -> Image.Image:
        canvas, draw = self.create_canvas()
        W, H = self.width, self.height
        M = self.MARGIN
        job = self.job
        theme = self.theme

        # ── LEFT ACCENT STRIPE (full height) ─────────────────────────
        draw.rectangle([0, 0, self.STRIPE_WIDTH, H], fill=theme.primary)

        # ── TOP-LEFT CORNER BLOCK ─────────────────────────────────────
        draw.rectangle([0, 0, M, M], fill=theme.primary)

        # ── HEADER ───────────────────────────────────────────────────
        y = 52
        y = draw_header(
            canvas, draw, W, y,
            company_name=job.company_name,
            portal_name=self.PORTAL_NAME,
            logo_path=job.company_logo,
            theme=theme,
            margin=M,
        )
        y += 48

        # ── "WE ARE HIRING" BADGE (centered, large) ──────────────────
        font_badge = get_font('ExtraBold', 26)
        badge_label = "◆  WE ARE HIRING  ◆"
        y = draw_hiring_badge(draw, W, y, theme, label=badge_label, align="center")
        y += 40

        # ── MUSTARD ACCENT RULE ───────────────────────────────────────
        accent_x = (W - 160) // 2
        draw.rectangle([accent_x, y, accent_x + 160, y + 5], fill=theme.primary)
        y += 5 + 40

        # ── JOB TITLE (centered) ──────────────────────────────────────
        y = draw_job_title(
            draw, W, y, job.title, theme,
            margin=M, align="center",
            max_font_size=80, min_font_size=40,
        )
        y += 20

        # ── COMPANY NAME (centered) ───────────────────────────────────
        y = draw_company_name(draw, W, y, job.company_name, theme, margin=M, align="center")
        y += 40

        # ── METADATA GRID ─────────────────────────────────────────────
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
        y += 24

        # ── KEY SKILLS ───────────────────────────────────────────────
        if job.skills:
            y = draw_section_label(draw, M, y, "Key Skills", theme)
            y += 8
            y = draw_skill_chips(draw, canvas, W, y, job.skills, theme, margin=M, max_rows=2)
            y += 32

        # ── FULL-WIDTH SEPARATOR ──────────────────────────────────────
        draw.rectangle([M, y, W - M, y + 1], fill=theme.accent_light)
        y += 1 + 32

        # ── DEADLINE ─────────────────────────────────────────────────
        if job.deadline:
            y = draw_deadline(draw, W, y, job.deadline, theme)
            y += 40

        # ── CTA BUTTON ───────────────────────────────────────────────
        y = draw_cta_button(draw, W, y, theme, style="yellow")
        y += 48

        # ── FOOTER ───────────────────────────────────────────────────
        url_font = get_font('Regular', 18)
        portal_url = job.application_url or f"https://jobbee.com/jobs/{job.job_id}"
        portal_w = text_width(portal_url, url_font)
        draw.text(((W - portal_w) // 2, H - M - 20), portal_url, font=url_font, fill=theme.text_secondary)

        if self.show_qr:
            draw_qr_block(canvas, W, H, portal_url, theme, qr_size=100, margin=M)

        # ── BOTTOM STRIPE ─────────────────────────────────────────────
        draw.rectangle([0, H - self.STRIPE_WIDTH, W, H], fill=theme.primary)

        return canvas
