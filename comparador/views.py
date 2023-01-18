from django.shortcuts import render
from .forms import BuscarVuelosForm
from .models import Aeropuerto
import requests
import json
import pandas as pd

# Create your views here.
def index(request):
    aeropuertos = Aeropuerto.objects.all()
    if request.method == 'POST':
        form = BuscarVuelosForm(request.POST)
        if form.is_valid():
            origen = form.cleaned_data['origen']
            destino = form.cleaned_data['destino']
            fecha = str(form.cleaned_data['fecha'])
            # Obtener codigo de origen
            if Aeropuerto.objects.filter(nombre=origen).exists():
                objeto_aeropuerto = Aeropuerto.objects.get(nombre=origen)
                codigo_origen = objeto_aeropuerto.codigo
            else:
                # El aeropuerto no esta en la base de datos. Aun asi intentamos llamar a la API
                if len(origen) == 3:
                    codigo_origen = origen
                else:
                    return render(request, 'index.html', {"aeropuertos":aeropuertos, "form":form})
            # Obtener codigo de destino
            if Aeropuerto.objects.filter(nombre=destino).exists():
                objeto_aeropuerto = Aeropuerto.objects.get(nombre=destino)
                codigo_destino = objeto_aeropuerto.codigo
            else:
                # El aeropuerto no esta en la base de datos. Aun asi intentamos llamar a la API
                if len(destino) == 3:
                    codigo_destino = destino
                else:
                    return render(request, 'index.html', {"aeropuertos":aeropuertos, "form":form})


            # Llamar a la api para conseguir dataframe con resultados
            try:
                resultados = infoVuelos(codigo_origen, codigo_destino, fecha)
            except:
                resultados = None
            # Pasar dataframe a json
            data = None
            if resultados is not None:
                json_records = resultados.reset_index().to_json(orient ='records')
                data = []
                data = json.loads(json_records)

            return render(request, 'resultados.html', {'origen':origen, 'destino':destino, 'fecha':fecha, 'd':data})
    else:
        form = BuscarVuelosForm()
    return render(request, 'index.html', {"aeropuertos":aeropuertos, "form":form})



def escalas(v):
    if type(v) == dict:
        return False
    elif type(v) == list:
        return True

def infoVuelos(aeropuertoSalida, aeropuertoLlegada, fecha, directo=0):
    df = pd.DataFrame({'opcion':[], 'escalas':[], 'duracion':[], 'salida':[], 'llegada':[], 'aerolineas':[]})
    
    Token = 'Bearer uvzw5k2tagu68tz9g3h6enac'
    url = f'https://api.lufthansa.com/v1/operations/schedules/{aeropuertoSalida}/{aeropuertoLlegada}/{fecha}?directFlights={directo}'
    cabecera = {'Authorization': Token, 'Accept': 'application/json'}
    resp = requests.get(url, headers=cabecera)
    j = resp.json()

    recurso = j['ScheduleResource']
    horario = recurso['Schedule']
    
    contador = 0
    for i in horario:
        contador += 1
        
        # Variables a guardar para mostrar
        DFopcion = 0
        DFn_escalas = 0
        DFinfoescalas = set()
        DFduracion = ''
        DFsalida = ''
        DFllegada = ''
        DFaerolineas = set()

        
        numero = -1
    
        viaje = i['TotalJourney']
        duracion = viaje['Duration']
        vuelo = i['Flight']
        if escalas(vuelo) == False:
            
            # No hay escalas
            DFn_escalas = 0
            
            origen = vuelo['Departure']
            aeropuertoOrigenID = origen['AirportCode']
            salidaPrev = origen['ScheduledTimeLocal']
            horaSalida = salidaPrev['DateTime']
            destino = vuelo['Arrival']
            aeropuertoDestinoID = destino['AirportCode']
            llegadaPrev = destino['ScheduledTimeLocal']
            horaLlegada = llegadaPrev['DateTime']
            
            if 'MarketingCarrier' in vuelo.keys():
                marketing = vuelo['MarketingCarrier']
                aerolineaM = marketing['AirlineID']
                # Aerolineas
                DFaerolineas.add(aerolineaM)
            if 'OperatingCarrier' in vuelo.keys():
                operadora = vuelo['OperatingCarrier']
                aerolineaO = operadora['AirlineID']
                # Aerolineas
                DFaerolineas.add(aerolineaO)
            
            # Duracion
            DFduracion = duracion
            # Salida y Llegada
            DFsalida = horaSalida
            DFllegada = horaLlegada
            
        else:
            for k in vuelo:
                origen = k['Departure']
                aeropuertoOrigenID = origen['AirportCode']
                salidaPrev = origen['ScheduledTimeLocal']
                horaSalida = salidaPrev['DateTime']
                destino = k['Arrival']
                aeropuertoDestinoID = destino['AirportCode']
                llegadaPrev = destino['ScheduledTimeLocal']
                horaLlegada = llegadaPrev['DateTime']
                numero += 1
                # Hora Salida
                if numero + 1 == 1:
                    DFsalida = horaSalida
                for l in range(len(vuelo)-1):
                    if vuelo.index(k) == l:
                        if 'MarketingCarrier' in k.keys():
                            marketing = k['MarketingCarrier']
                            aerolineaM = marketing['AirlineID']
                            # Aerolineas
                            DFaerolineas.add(aerolineaM)
                        if 'OperatingCarrier' in k.keys():
                            operadora = k['OperatingCarrier']
                            aerolineaO = operadora['AirlineID']
                            # Aerolineas
                            DFaerolineas.add(aerolineaO)
                    if k != vuelo[-1]:
                        # Anadir info escala
                        DFinfoescalas.add(aeropuertoDestinoID)
                    else:
                        if 'MarketingCarrier' in k.keys():
                            marketing = k['MarketingCarrier']
                            aerolineaM = marketing['AirlineID']
                            # Aerolineas
                            DFaerolineas.add(aerolineaM)
                        if 'OperatingCarrier' in k.keys():
                            operadora = k['OperatingCarrier']
                            aerolineaO = operadora['AirlineID']
                            # Aerolineas
                            DFaerolineas.add(aerolineaO)
    
            
            # Contar n. escalas
            DFn_escalas = numero
            # Duracion
            DFduracion = duracion
            # Llegada
            DFllegada = horaLlegada
            
        
        # Actualizar DFopcion
        DFopcion = str(contador)
        # Actualizar DFinfoescalas y juntarlo con DFn_escalas
        s = str(int(DFn_escalas))
        if DFn_escalas > 0:
            s += ' ('
            for escala in DFinfoescalas:
                s += f'{escala}, '
            s = s[:-2]
            s += ')'
        DFn_escalas = s
        # Transformar DFaerolineas a string
        cod_aerolineas = {'LH':'Lufthansa', 'LX':'Swiss Int.', 'OS':'Austrian', 'SW':'Brussels', 'EW':'EuroWings'}
        s = ''
        for aerolinea in DFaerolineas:
            if aerolinea in cod_aerolineas:
                s += f'{cod_aerolineas[aerolinea]}, '
        s = s[:-2]
        if s == '':
            s = 'Lufthansa'
        DFaerolineas = s
        # Guardar datos en el dataframe en nueva linea y luego pasar a la siguiente opcion de vuelo
        df.loc[len(df.index)] = [DFopcion, DFn_escalas, DFduracion, DFsalida, DFllegada, DFaerolineas]
    
    return df