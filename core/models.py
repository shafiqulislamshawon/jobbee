from django.db import models

class HeroSectionSettings(models.Model):
    # Left Content
    badge_text = models.CharField(max_length=100, default="Platform v2.0 is Live", help_text="Small text badge at the top")
    heading_line_1 = models.CharField(max_length=100, default="Ship your", help_text="First line of the main heading")
    heading_line_2_colored = models.CharField(max_length=100, default="career.", help_text="Second colored line of the main heading")
    subheading = models.TextField(default="The ultra-fast, premium hiring infrastructure designed for top-tier engineers, designers, and innovators.")
    
    # Companies Section
    companies_section_title = models.CharField(max_length=100, default="Trusted by innovative companies", help_text="Title above the trusted company logos")
    
    # Search Form
    search_placeholder_1 = models.CharField(max_length=100, default="Search roles, skills or companies")
    search_placeholder_2 = models.CharField(max_length=100, default="Location or Remote")
    search_button_text = models.CharField(max_length=50, default="Find Roles")
    popular_tags = models.CharField(max_length=255, default="Remote, Design, Backend, Marketing, Data", help_text="Comma-separated popular search tags")
    
    # Right Content (Floating Graphics)
    card_1_number = models.CharField(max_length=20, default="10k+", help_text="e.g. 10k+")
    card_1_label = models.CharField(max_length=50, default="Active Jobs", help_text="e.g. Active Jobs")
    
    card_2_title = models.CharField(max_length=50, default="UX Designer", help_text="e.g. UX Designer")
    card_2_tag_1 = models.CharField(max_length=20, default="FULL TIME")
    card_2_tag_2 = models.CharField(max_length=20, default="REMOTE")
    
    card_3_number = models.CharField(max_length=20, default="5k+")
    card_3_label = models.CharField(max_length=50, default="Employers")
    
    card_4_number = models.CharField(max_length=20, default="24h")
    card_4_label = models.CharField(max_length=50, default="Avg. Response")

    class Meta:
        verbose_name = "Hero Section Settings"
        verbose_name_plural = "Hero Section Settings"

    def __str__(self):
        return "Hero Section Settings"

    def get_popular_tags_list(self):
        if not self.popular_tags:
            return []
        return [tag.strip() for tag in self.popular_tags.split(',')]

class TrustedCompany(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='trusted_companies/', help_text="Upload a company logo")
    order = models.IntegerField(default=0, help_text="Order in which it appears")

    class Meta:
        verbose_name = "Trusted Company"
        verbose_name_plural = "Trusted Companies"
        ordering = ['order']

    def __str__(self):
        return self.name
