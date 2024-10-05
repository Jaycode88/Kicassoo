from django import forms

class DeliveryForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(max_length=100, required=True, label="Email Address")
    phone_number = forms.CharField(max_length=20, required=True, label="Phone Number")
    address_line_1 = forms.CharField(max_length=255, required=True, label="Address Line 1")
    address_line_2 = forms.CharField(max_length=255, required=False, label="Address Line 2")
    city = forms.CharField(max_length=100, required=True, label="City")
    postcode = forms.CharField(max_length=20, required=True, label="Postcode")
    country = forms.CharField(max_length=50, required=True, label="Country")
