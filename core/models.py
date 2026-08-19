from django.db import models

class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, unique=True, help_text="e.g. USD, EUR, GBP")
    rate_to_base = models.DecimalField(max_digits=10, decimal_places=4, help_text="How much of this currency equals 1 Base Currency")
    
    class Meta:
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"

    def __str__(self):
        return f"{self.currency} (Rate: {self.rate_to_base})"

class CurrencySettings(models.Model):
    base_currency = models.CharField(max_length=10, default="USD", help_text="e.g. USD")
    base_currency_symbol = models.CharField(max_length=5, default="$", help_text="e.g. $")
    display_currency = models.CharField(max_length=10, default="BDT", help_text="e.g. BDT")
    display_currency_symbol = models.CharField(max_length=5, default="৳", help_text="e.g. ৳")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=120.0000, help_text="1 Base = X Display")
    enable_conversion = models.BooleanField(default=True, help_text="Turn currency conversion on or off globally")

    class Meta:
        verbose_name = "Currency Settings"
        verbose_name_plural = "Currency Settings"

    def __str__(self):
        return f"{self.base_currency} to {self.display_currency} Configuration"

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

class Testimonial(models.Model):
    quote = models.TextField(help_text="The testimonial text")
    author_name = models.CharField(max_length=100)
    author_title = models.CharField(max_length=100, help_text="e.g. Product Designer at Airbnb")
    author_avatar = models.ImageField(upload_to='testimonials/', null=True, blank=True, help_text="Upload an avatar. If empty, a generated avatar will be used.")
    
    # Hired Card Badge
    badge_initial = models.CharField(max_length=5, default="a", help_text="Initial for the hired badge (e.g. 'a')")
    hired_role = models.CharField(max_length=100, default="Product Designer")
    
    is_active = models.BooleanField(default=True, help_text="Show this testimonial on the homepage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_name} - {self.author_title}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
