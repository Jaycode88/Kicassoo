from django import forms
from .models import Order

from django_countries.widgets import CountrySelectWidget


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number',
            'street_address1', 'street_address2','town_or_city',   
            'county', 'postcode', 'country',
        )
        # Use the standard widget, no need for flags
        widgets = {
            'country': forms.Select(attrs={'class': 'stripe-style-input', 'disabled': True}),
        }

    def __init__(self, *args, **kwargs):
        """
        Customize form field attributes, labels, and placeholders
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County or Locality',
        }

        # Set autofocus on the first field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder

            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False

        # Disable the country field and set it to 'GB'
        self.fields['country'].disabled = True
        self.fields['country'].initial = 'GB'