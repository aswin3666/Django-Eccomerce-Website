from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
payment_choices=(
    ('C','Cash On Delivery'),
    ('S','Stripe')
)

class CheckoutForm(forms.Form):
    shipping_address=forms.CharField()
    country=CountryField(blank_label='select your country').formfield(
        required=False)
    zip=forms.CharField()
    mobilenumber=forms.DecimalField()
    #save_info=forms.BooleanField(widget=forms.CheckboxInput())
    payment_option=forms.ChoiceField(widget=forms.RadioSelect,choices=payment_choices)