from django import forms


class LoadFileForm(forms.Form):
    file = forms.FileField()