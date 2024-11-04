from django import forms
from django_countries.fields import CountryField

class DeliveryForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(max_length=100, required=True, label="Email Address")
    phone_number = forms.CharField(max_length=20, required=True, label="Phone Number")
    address_line_1 = forms.CharField(max_length=255, required=True, label="Address Line 1")
    address_line_2 = forms.CharField(max_length=255, required=False, label="Address Line 2")
    city = forms.CharField(max_length=100, required=True, label="City")
    county = forms.CharField(max_length=100, required=False, label="County/State")
    postcode = forms.CharField(max_length=20, required=True, label="Postcode")
    country = CountryField(blank_label='(Select country)').formfield()  # Use CountryField to get country code