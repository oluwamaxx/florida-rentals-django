from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class SiteSettings(models.Model):
    company_name = models.CharField(max_length=120, default='SunCoast Rentals')
    tagline = models.CharField(max_length=180, default='Quality Homes. Better Living.')
    logo_text = models.CharField(max_length=80, default='SunCoast Rentals', blank=True)
    hero_eyebrow = models.CharField(max_length=120, default='PREMIUM RENTALS IN FLORIDA')
    hero_title = models.CharField(max_length=200, default='Your Next Home Is Closer Than You Think')
    hero_subtitle = models.TextField(default='Discover beautiful, comfortable, and affordable rental homes across Florida. Find the perfect home for your lifestyle.')
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    why_choose_image = models.ImageField(upload_to='site/', blank=True, null=True, help_text='Optional photo shown on the Why Choose Us section of the homepage.')
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_address = models.CharField(max_length=255, blank=True, help_text='Optional. Leave blank if you do not want an address in the footer.')
    self_tour_phone = models.CharField(max_length=40, blank=True, help_text='Phone number used after a Schedule Self Tour form is submitted.')
    self_tour_intro = models.TextField(default='Complete the quick form and we will direct you to call our self-tour team.', blank=True)
    footer_text = models.TextField(default='Quality Homes. Better Living.', blank=True)
    map_default_lat = models.DecimalField(max_digits=9, decimal_places=6, default=27.994402)
    map_default_lng = models.DecimalField(max_digits=9, decimal_places=6, default=-81.760254)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.company_name

class SMTPSettings(models.Model):
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True, help_text='Stored in the database. Use a protected admin account in production.')
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    from_email = models.EmailField(blank=True)
    from_name = models.CharField(max_length=120, default='Rental Website')
    notification_email = models.EmailField(blank=True, help_text='Email address that receives new Schedule Self Tour notifications.')
    enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'SMTP Email Settings'
        verbose_name_plural = 'SMTP Email Settings'

    def save(self, *args, **kwargs):
        if self.use_ssl:
            self.use_tls = False
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'SMTP configuration'

class Listing(models.Model):
    STATUS_CHOICES = [('available','Available'), ('pending','Pending'), ('rented','Rented')]
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=40, default='FL')
    zip_code = models.CharField(max_length=20)
    rent = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    bedrooms = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0'))])
    bathrooms = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0'))])
    square_feet = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    featured = models.BooleanField(default=False)
    map_url = models.URLField(blank=True, help_text='Optional custom Google Maps or map URL. Address remains the primary location.')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']
        indexes = [models.Index(fields=['status','city','rent']), models.Index(fields=['bedrooms','bathrooms'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.title) or 'property'
            slug = base
            n = 2
            while Listing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        return f'{self.address}, {self.city}, {self.state} {self.zip_code}'

    @property
    def primary_photo(self):
        return self.photos.filter(is_main=True).first() or self.photos.first()

    @property
    def maps_link(self):
        if self.map_url:
            return self.map_url
        from urllib.parse import quote_plus
        return f'https://www.google.com/maps/search/?api=1&query={quote_plus(self.full_address)}'

    def __str__(self):
        return self.title

class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/%Y/%m/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text='Optional alternative. Uploading a file is the primary method.')
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(20)])
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', 'id']
        constraints = [models.UniqueConstraint(fields=['listing','order'], name='unique_listing_photo_order')]

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.image and not self.image_url:
            raise ValidationError('Each photo needs an uploaded file or an image URL.')
        if self.order < 1 or self.order > 20:
            raise ValidationError('Photo order must be between 1 and 20.')
        if self.listing_id:
            qs = ListingPhoto.objects.filter(listing_id=self.listing_id).exclude(pk=self.pk)
            if qs.count() >= 20:
                raise ValidationError('A listing can have a maximum of 20 photos.')

    def save(self, *args, **kwargs):
        if self.is_main:
            ListingPhoto.objects.filter(listing=self.listing, is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.listing} photo {self.order}'

class Feature(models.Model):
    listing = models.ForeignKey(Listing, related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=40, default='✓', blank=True)
    order = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['order','id']
    def __str__(self): return self.name

class Fee(models.Model):
    listing = models.ForeignKey(Listing, related_name='fees', on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    order = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['order','id']
    def __str__(self): return f'{self.name} - ${self.amount}'

class TourRequest(models.Model):
    listing = models.ForeignKey(Listing, related_name='tour_requests', on_delete=models.PROTECT)
    name = models.CharField(max_length=160)
    phone = models.CharField(max_length=40)
    monthly_gross_income = models.DecimalField(max_digits=12, decimal_places=2)
    has_been_evicted = models.BooleanField()
    years_renting = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0'))])
    move_in_date = models.DateField()
    reason_for_moving = models.TextField()
    funds_to_secure = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self): return f'{self.name} — {self.listing.title}'
