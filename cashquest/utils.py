import datetime

def hoje_inicio_mes():
    hoje = datetime.date.today()
    return hoje.replace(day=1), hoje