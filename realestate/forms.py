from django import forms
from .models import TourRequest

class TourRequestForm(forms.ModelForm):
    class Meta:
        model = TourRequest
        fields = ['name','phone','monthly_gross_income','has_been_evicted','years_renting','move_in_date','reason_for_moving','funds_to_secure']
        widgets = {
            'move_in_date': forms.DateInput(attrs={'type':'date'}),
            'monthly_gross_income': forms.NumberInput(attrs={'step':'0.01','min':'0'}),
            'years_renting': forms.NumberInput(attrs={'step':'0.5','min':'0'}),
            'funds_to_secure': forms.NumberInput(attrs={'step':'0.01','min':'0'}),
            'reason_for_moving': forms.Textarea(attrs={'rows':4}),
        }
        labels = {
            'monthly_gross_income':'Monthly gross income',
            'has_been_evicted':'Have you ever been evicted before?',
            'years_renting':'How many years have you been renting?',
            'move_in_date':'Desired move-in date',
            'reason_for_moving':'Reason for moving out of current residence',
            'funds_to_secure':'How much do you currently have available to secure the house?',
        }
