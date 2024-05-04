from supporting.colores import Colores
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILD = 'Aim Paint'
INFO =  f'{Colores.NEGRITA}{Colores.AZUL}INFO     {Colores.RESET}'
NAME = f'{Colores.AZUL}Gatito Bot{Colores.RESET}'
