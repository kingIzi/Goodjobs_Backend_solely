from django import forms
from django.core.validators import RegexValidator


class SignUpForm(forms.Form):
    phone_number = forms.CharField(required=True,
                                   validators=[
                                    RegexValidator(
                                        regex=r'^[67]\d{8}$',
                                        message="Invalid phone number, please enter the mobile number without the leading '0' or country code.",
                                        code='invalid_phone_number'
                                   )],
                                   error_messages={'required': 'Phone number is missing.'})
    first_name = forms.CharField(required=True,max_length=255,error_messages={'required': 'You must provide a first name.'})
    last_name = forms.CharField(required=True,max_length=255,error_messages={'required': 'You must also provide a last name.'})
    email = forms.EmailField(required=True,error_messages={'required': 'Please provide a valid email address.'})



class VerifySignUpOtpForm(forms.Form):
    phone_number = forms.CharField(required=True,
                                   validators=[
                                    RegexValidator(
                                        regex=r'^[67]\d{8}$',
                                        message="Invalid phone number, please enter the mobile number without the leading 0 or country code.",
                                        code='invalid_phone_number'
                                   )],
                                   error_messages={'required': 'Phone number is missing.'})
    otp_value = forms.CharField(required=True,error_messages={'required': 'Missing OTP code.'})


class LoginValidator(forms.Form):
    phone_number = forms.CharField(required=True,
                                   validators=[
                                    RegexValidator(
                                        regex=r'^[67]\d{8}$',
                                        message="Invalid phone number, please enter the mobile number without the leading 0 or country code.",
                                        code='invalid_phone_number'
                                   )],
                                   error_messages={'required': 'Phone number is missing.'})
    status = forms.CharField(required=True,error_messages={'required': 'Please specify user role.'})


class VerifyLoginOtpForm(VerifySignUpOtpForm):
    pass


class FetchUsersValidator(forms.Form):
    user_id = forms.IntegerField(required=True, error_messages={'required': 'Please provide a user_id'})


class AddJobCategoryForm(forms.Form):
    name = forms.CharField(required=True,error_messages={'required': 'You must provide a category name'})


class AddJobPostForm(forms.Form):
    company_id = forms.CharField(required=True,error_messages={'required': 'Please select a company'})
    location = forms.CharField(required=True,error_messages={'required': 'Please provide a location'})
    job_title = forms.CharField(required=True,error_messages={'required': 'Please provide a job title'})
    job_type = forms.CharField(required=True,error_messages={'required': 'Please provide a job type'})
    salary_min = forms.CharField(required=True,error_messages={'required': 'Please enter the minimum salary'})
    salary_max = forms.CharField(required=True,error_messages={'required': 'Please provide a maximum salary'})
    job_post_url = forms.CharField(required=True,error_messages={'required': 'Please enter the job post url'}),
    job_description = forms.CharField(required=True,error_messages={'required': 'Please provide a job description'})
    deadline = forms.CharField(required=True,error_messages={'required': 'Please provide an application deadline'})
    category_id = forms.CharField(required=True,error_messages={'required': 'Please select a category'})

class ResendOtpForm(forms.Form):
    phone_number = forms.CharField(required=True,
                                   validators=[
                                    RegexValidator(
                                        regex=r'^[67]\d{8}$',
                                        message="Invalid phone number, please enter the mobile number without the leading 0 or country code.",
                                        code='invalid_phone_number'
                                   )])
    
class CheckExistsCompanyForm(forms.Form):
    name = forms.CharField(required=True,error_messages={'required': 'You must provide a company name'})  

class AddCompanyForm(CheckExistsCompanyForm):
    about_company = forms.CharField(required=True,error_messages={'required': 'You must provide a company description'})
