from django import forms
from django.contrib.auth import authenticate
from django.core import validators
from django.contrib.auth.forms import BaseUserCreationForm
from users import models
from django.contrib.auth import get_user_model


class UserAuthForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), help_text="Enter email here", template_name = 'field.html')
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), validators=[validators.MinLengthValidator(2), validators.MaxLengthValidator(14)])

    template_name = "form.html"

    def clean_email(self):
        # validation
        # transformation
        email = self.cleaned_data.get('email')
        # raise forms.validationError('Email is not valid')
        return email.lower()
    
    def clean(self):
        clean_data = self.cleaned_data
        email = clean_data.get('email')
        password = clean_data.get('password')

        user = authenticate(email=email, password=password)
        if user:
            self.user = user
        else:
            raise forms.ValidationError('Invalid username or password')
        
    def get_user(self):
        return self.user    
    
class UserSignupForm(BaseUserCreationForm):
    
    class Meta:
        # model = models.User # get_user_model
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "dob" )
        # exclude = ("last_login", "password", "date_joined")

        widgets = {
            'dob': forms.DateInput(attrs={"type": "date"})
        }

class UserUpdateForm(forms.ModelForm):

    class Meta:

        model = models.User
        fields = ("first_name", "last_name")
        