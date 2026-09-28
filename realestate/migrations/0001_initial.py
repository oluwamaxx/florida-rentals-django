from django.db import migrations, models
import django.core.validators
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='Listing', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=180)), ('slug', models.SlugField(blank=True, unique=True)),
            ('address', models.CharField(max_length=255)), ('city', models.CharField(max_length=100)), ('state', models.CharField(default='FL', max_length=40)), ('zip_code', models.CharField(max_length=20)),
            ('rent', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
            ('bedrooms', models.DecimalField(decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(0)])),
            ('bathrooms', models.DecimalField(decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(0)])),
            ('square_feet', models.PositiveIntegerField()), ('description', models.TextField(blank=True)),
            ('status', models.CharField(choices=[('available','Available'),('pending','Pending'),('rented','Rented')], default='available', max_length=20)),
            ('featured', models.BooleanField(default=False)), ('map_url', models.URLField(blank=True)),
            ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)), ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
        ], options={'ordering':['-featured','-created_at'] }),
        migrations.CreateModel(name='SiteSettings', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('company_name', models.CharField(default='SunCoast Rentals', max_length=120)), ('tagline', models.CharField(default='Quality Homes. Better Living.', max_length=180)), ('logo_text', models.CharField(blank=True, default='SunCoast Rentals', max_length=80)),
            ('hero_eyebrow', models.CharField(default='PREMIUM RENTALS IN FLORIDA', max_length=120)), ('hero_title', models.CharField(default='Your Next Home Is Closer Than You Think', max_length=200)), ('hero_subtitle', models.TextField(default='Discover beautiful, comfortable, and affordable rental homes across Florida. Find the perfect home for your lifestyle.')), ('hero_image', models.ImageField(blank=True, null=True, upload_to='site/')),
            ('contact_phone', models.CharField(blank=True, max_length=40)), ('contact_email', models.EmailField(blank=True, max_length=254)), ('contact_address', models.CharField(blank=True, max_length=255)), ('self_tour_phone', models.CharField(blank=True, max_length=40)), ('self_tour_intro', models.TextField(blank=True, default='Complete the quick form and we will direct you to call our self-tour team.')), ('footer_text', models.TextField(blank=True, default='Quality Homes. Better Living.')), ('map_default_lat', models.DecimalField(decimal_places=6, default=27.994402, max_digits=9)), ('map_default_lng', models.DecimalField(decimal_places=6, default=-81.760254, max_digits=9)), ('updated_at', models.DateTimeField(auto_now=True)),
        ]),
        migrations.CreateModel(name='SMTPSettings', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('host', models.CharField(blank=True, max_length=255)), ('port', models.PositiveIntegerField(default=587)), ('username', models.CharField(blank=True, max_length=255)), ('password', models.CharField(blank=True, help_text='Stored in the database. Use a protected admin account in production.', max_length=255)), ('use_tls', models.BooleanField(default=True)), ('use_ssl', models.BooleanField(default=False)), ('from_email', models.EmailField(blank=True, max_length=254)), ('from_name', models.CharField(default='Rental Website', max_length=120)), ('notification_email', models.EmailField(blank=True, help_text='Email address that receives new Schedule Self Tour notifications.', max_length=254)), ('enabled', models.BooleanField(default=False)),
        ]),
        migrations.CreateModel(name='Feature', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=120)), ('icon', models.CharField(blank=True, default='✓', max_length=40)), ('order', models.PositiveIntegerField(default=1)), ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='realestate.listing'))]),
        migrations.CreateModel(name='Fee', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=160)), ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])), ('order', models.PositiveIntegerField(default=1)), ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='realestate.listing'))]),
        migrations.CreateModel(name='ListingPhoto', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('image', models.ImageField(blank=True, null=True, upload_to='listings/%Y/%m/')), ('image_url', models.URLField(blank=True)), ('caption', models.CharField(blank=True, max_length=160)), ('order', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(20)])), ('is_main', models.BooleanField(default=False)), ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='realestate.listing'))]),
        migrations.CreateModel(name='TourRequest', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=160)), ('phone', models.CharField(max_length=40)), ('monthly_gross_income', models.DecimalField(decimal_places=2, max_digits=12)), ('has_been_evicted', models.BooleanField()), ('years_renting', models.DecimalField(decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(0)])), ('move_in_date', models.DateField()), ('reason_for_moving', models.TextField()), ('funds_to_secure', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])), ('created_at', models.DateTimeField(auto_now_add=True)), ('email_sent', models.BooleanField(default=False)), ('email_error', models.TextField(blank=True)), ('listing', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tour_requests', to='realestate.listing'))]),
        migrations.AddConstraint(model_name='listingphoto', constraint=models.UniqueConstraint(fields=('listing','order'), name='unique_listing_photo_order')),
        migrations.AddIndex(model_name='listing', index=models.Index(fields=['status','city','rent'], name='realestate_l_status_9efae2_idx')),
        migrations.AddIndex(model_name='listing', index=models.Index(fields=['bedrooms','bathrooms'], name='realestate_l_bedroom_6e2d95_idx')),
    ]
