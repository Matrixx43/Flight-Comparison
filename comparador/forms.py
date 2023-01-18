from django import forms

class DateTypeInput(forms.DateInput):
    # Clase auxiliar para cambiar el tipo de DateField de "type=text" a "type=date" en HTML
    input_type = 'date'

class BuscarVuelosForm(forms.Form):
    origen = forms.CharField(label='Origen ', max_length=200, min_length=3, widget=forms.TextInput(attrs={'id': 'aeropuerto1'}))
    destino = forms.CharField(label='Destino ', max_length=200, min_length=3, widget=forms.TextInput(attrs={'id': 'aeropuerto2'}))
    fecha = forms.DateField(label='Fecha ', widget=DateTypeInput())