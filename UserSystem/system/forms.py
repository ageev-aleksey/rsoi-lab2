from django import forms

class SingUp(forms.Form):
    nick = forms.CharField(max_length=30, null = False)
    password = forms.PasswordInput()
    fname = forms.CharField(max_length= 30)
    lname = forms.CharField(max_length = 30)
    patronymic = forms.CharField(max_length=30)
    birthday = forms.DateField()
