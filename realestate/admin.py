from django import forms
from django.contrib import admin, messages
from django.core.mail import EmailMessage, get_connection
from django.db.models import Count
from django.utils.html import format_html
from .models import SiteSettings, SMTPSettings, Listing, ListingPhoto, Feature, Fee, TourRequest

class PhotoUploadWidget(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [super().clean(item, initial) for item in data]
        return [super().clean(data, initial)]

class ListingAdminForm(forms.ModelForm):
    photo_uploads = MultipleFileField(required=False, widget=PhotoUploadWidget(attrs={'accept':'image/*','multiple':True}), help_text='Primary photo method: select multiple photos from your phone/computer. Maximum 20 photos total. The first uploaded photo becomes the main photo unless you already have photos.')
    class Meta:
        model = Listing
        fields = '__all__'

class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 0
    max_num = 20
    fields = ('preview','image','image_url','caption','order','is_main')
    readonly_fields = ('preview',)
    ordering = ('order','id')
    classes = ('photo-inline',)

    class Media:
        js = ('realestate/js/admin_photos.js',)

    def preview(self, obj):
        src = obj.image.url if obj.image else obj.image_url
        return format_html('<img src="{}" style="width:100px;height:70px;object-fit:cover;border-radius:8px;background:#111;" />', src) if src else '—'
    preview.short_description = 'Preview'

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1
    fields = ('name','icon','order')

class FeeInline(admin.TabularInline):
    model = Fee
    extra = 1
    fields = ('name','amount','order')

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    list_display = ('title','city','rent','bedrooms','bathrooms','square_feet','status','featured','photo_count','created_at')
    list_filter = ('status','featured','city','state')
    search_fields = ('title','address','city','zip_code')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status','featured')
    readonly_fields = ('created_at','updated_at')
    inlines = [ListingPhotoInline, FeatureInline, FeeInline]
    fieldsets = (
        ('Basic listing information', {'fields': ('title','slug','description','status','featured')}),
        ('Property details', {'fields': ('rent','bedrooms','bathrooms','square_feet')}),
        ('Address & Google Maps', {'fields': ('address','city','state','zip_code','map_url'), 'description':'The address is used for the Google Maps link shown on the Schedule Self Tour form. Map URL is optional; if left blank, Google Maps will use the saved address.'}),
        ('Upload photos from device', {'fields': ('photo_uploads',)}),
        ('Timestamps', {'fields': ('created_at','updated_at'), 'classes': ('collapse',)}),
    )

    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        request._listing_photo_uploads = form.cleaned_data.get('photo_uploads') or []

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        uploads = getattr(request, '_listing_photo_uploads', [])
        existing = obj.photos.count()
        if existing + len(uploads) > 20:
            self.message_user(request, f'Only the first {max(0, 20-existing)} uploaded photo(s) were added because each listing supports a maximum of 20 photos.', messages.WARNING)
            uploads = uploads[:max(0, 20-existing)]
        next_order = obj.photos.order_by('-order').values_list('order', flat=True).first() or 0
        for image in uploads:
            next_order += 1
            ListingPhoto.objects.create(listing=obj, image=image, order=next_order, is_main=(obj.photos.count()==0 and next_order==1))
        if uploads and not obj.photos.filter(is_main=True).exists():
            first = obj.photos.order_by('order','id').first()
            if first: ListingPhoto.objects.filter(pk=first.pk).update(is_main=True)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Brand', {'fields': ('company_name','logo_text','tagline','footer_text')}),
        ('Homepage hero', {'fields': ('hero_eyebrow','hero_title','hero_subtitle','hero_image')}),
        ('Homepage — Why Choose Us photo', {'fields': ('why_choose_image',), 'description':'Upload the photo shown on the right side of the Why Choose Us section. You can select it directly from your computer or phone.'}),
        ('Footer contact — all optional', {'fields': ('contact_phone','contact_email','contact_address'), 'description':'Phone, email, and address are editable here. The footer address is optional.'}),
        ('Self-tour', {'fields': ('self_tour_phone','self_tour_intro'), 'description':'After a visitor submits Schedule Self Tour, the site uses self-tour phone for the call link.'}),
    )

    def has_add_permission(self, request): return not SiteSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('SMTP server', {'fields': ('enabled','host','port','username','password','use_tls','use_ssl')}),
        ('Outgoing email', {'fields': ('from_email','from_name')}),
        ('Notifications', {'fields': ('notification_email',), 'description':'New Schedule Self Tour submissions are emailed here.'}),
    )
    actions = ['send_test_email']
    def has_add_permission(self, request): return not SMTPSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False

    @admin.action(description='Send a test email using this SMTP configuration')
    def send_test_email(self, request, queryset):
        for smtp in queryset:
            if not smtp.notification_email:
                self.message_user(request, 'Set a notification email first.', messages.ERROR); continue
            try:
                connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend', host=smtp.host, port=smtp.port, username=smtp.username or None, password=smtp.password or None, use_tls=smtp.use_tls, use_ssl=smtp.use_ssl, fail_silently=False)
                email = EmailMessage('SMTP test — rental website', 'This is a test email from your Django rental website.', smtp.from_email or smtp.username, [smtp.notification_email], connection=connection)
                email.send(fail_silently=False)
                self.message_user(request, f'Test email sent to {smtp.notification_email}.', messages.SUCCESS)
            except Exception as exc:
                self.message_user(request, f'SMTP test failed: {exc}', messages.ERROR)

@admin.register(TourRequest)
class TourRequestAdmin(admin.ModelAdmin):
    list_display = ('name','listing','phone','move_in_date','monthly_gross_income','funds_to_secure','email_status','created_at')
    list_filter = ('has_been_evicted','email_sent','move_in_date','created_at')
    search_fields = ('name','phone','listing__title')
    readonly_fields = ('listing','name','phone','monthly_gross_income','has_been_evicted','years_renting','move_in_date','reason_for_moving','funds_to_secure','created_at','email_sent','email_error')
    def email_status(self, obj):
        return 'Sent' if obj.email_sent else ('Error' if obj.email_error else 'Not sent')
    email_status.short_description = 'Email'

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name','listing','order')
    search_fields = ('name','listing__title')

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('name','listing','amount','order')
    search_fields = ('name','listing__title')

admin.site.site_header = 'Rental Website Administration'
admin.site.site_title = 'Rental Website Admin'
admin.site.index_title = 'Manage listings, self-tour requests, email and website settings'
