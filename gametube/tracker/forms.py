from django import forms

class TrackerSearchForm(forms.Form):
    servers = (('EUNE', 'EUNE'),('EUW', 'EUW'), ('BR', 'BR'), ('JP', 'JP'), ('KR', 'KR'), ('LAN', 'LAN'), ('LAS', 'LAS'), ('NA', 'NA'), ('OC', 'OC'), ('TR', 'TR'), ('RU', 'RU'))
    username = forms.CharField(label='Username', max_length=30, min_length=1 ,widget=forms.TextInput(attrs={'class': 'form__search-input'}))
    server = forms.ChoiceField(choices=servers, widget=forms.Select(attrs={'class': 'form__search-input'}))
