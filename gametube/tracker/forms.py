from django import forms

class TrackerSearchForm(forms.Form):
    servers = (('EUNE', 'EUNE'),('EUW', 'EUW'))
    username = forms.CharField(label='Username', max_length=30, min_length=1 ,widget=forms.TextInput(attrs={'class': 'form__search-input'}))
    server = forms.ChoiceField(choices=servers, widget=forms.Select(attrs={'class': 'form__search-input'}))
