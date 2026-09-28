from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .email_utils import send_tour_notification
from .forms import TourRequestForm
from .models import Listing, SiteSettings, TourRequest


def _filtered_listings(request):
    qs = Listing.objects.filter(status='available').prefetch_related('photos','features','fees')
    q = request.GET.get('q','').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q)|Q(address__icontains=q)|Q(city__icontains=q)|Q(zip_code__icontains=q))
    for field, key, op in [('bedrooms','bed_min','gte'),('bathrooms','bath_min','gte'),('rent','rent_max','lte')]:
        value = request.GET.get(key,'').strip()
        if value:
            try:
                val = Decimal(value)
                qs = qs.filter(**{f'{field}__{op}': val})
            except InvalidOperation:
                pass
    feature = request.GET.get('feature','').strip()
    if feature:
        qs = qs.filter(features__name__icontains=feature)
    city = request.GET.get('city','').strip()
    if city:
        qs = qs.filter(city__icontains=city)
    return qs.distinct()



def home(request):
    listings = _filtered_listings(request)
    featured = listings.filter(featured=True)[:4]
    if not featured:
        featured = listings[:4]
    return render(request, 'realestate/home.html', {'featured': featured})


def properties(request):
    listings = _filtered_listings(request)
    sort = request.GET.get('sort','newest')
    if sort == 'rent_low': listings = listings.order_by('rent')
    elif sort == 'rent_high': listings = listings.order_by('-rent')
    elif sort == 'sqft': listings = listings.order_by('-square_feet')
    elif sort == 'bedrooms': listings = listings.order_by('-bedrooms')
    else: listings = listings.order_by('-featured','-created_at')
    return render(request, 'realestate/properties.html', {'listings': listings, 'filters': request.GET})


def property_detail(request, slug):
    listing = get_object_or_404(Listing.objects.prefetch_related('photos','features','fees'), slug=slug)
    return render(request, 'realestate/detail.html', {'listing': listing, 'form': TourRequestForm()})


def tour_request(request, slug):
    listing = get_object_or_404(Listing, slug=slug, status='available')
    if request.method != 'POST':
        return redirect('property_detail', slug=slug)

    form = TourRequestForm(request.POST)
    if form.is_valid():
        tour = form.save(commit=False)
        tour.listing = listing
        tour.save()

        try:
            ok, err = send_tour_notification(tour)
            tour.email_sent = ok
            tour.email_error = err
            tour.save(update_fields=['email_sent', 'email_error'])
        except Exception as exc:
            tour.email_error = str(exc)
            tour.save(update_fields=['email_error'])

        # Do NOT redirect to tel:. The visitor must see a confirmation/next-steps
        # page first with the clickable call button.
        return redirect('tour_success', slug=listing.slug, tour_id=tour.pk)

    return render(request, 'realestate/detail.html', {'listing': listing, 'form': form})


def tour_success(request, slug, tour_id):
    tour = get_object_or_404(TourRequest.objects.select_related('listing'), pk=tour_id, listing__slug=slug)
    return render(request, 'realestate/tour_success.html', {'tour': tour, 'listing': tour.listing})
