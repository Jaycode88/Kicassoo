from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'id': 'name',
                                      'class':
                                      'form-control border border-1 rounded',
                                      'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'id': 'email',
                                       'class':
                                       'form-control border border-1 rounded',
                                       'placeholder': 'Your Email'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'id': 'message',
                                     'class':
                                     'form-control border border-1 rounded',
                                     'placeholder': 'Your Message'})
    )
