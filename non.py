
from datetime import datetime as dt
import datetime
def converterparaformato24h(hour_24h):
 
    hour = int(hour_24h.replace('h', ''))
    
    # Determina AM ou PM
    period = "AM" if hour < 12 else "PM"
    
    # Ajusta a hora para o formato de 12h (12 PM é meio-dia e 12 AM é meia-noite)
    hour_12h = hour if hour <= 12 else hour - 12
    if hour == 0:
        hour_12h = 12  # Ajuste para meia-noite
    
    # Retorna o horário formatado
    return f"{hour_12h:02}:00 {period}"

x_axisbr= ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
x_axis = [datetime.time(i).strftime("%I %p") for i in range(8,19)]


print(converterparaformato24h(x_axisbr[0]))