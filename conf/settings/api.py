# Único índice asignado a las series de tiempo
TS_INDEX = 'indicators'

# Modos de representación de las series, calculados y guardados
# en el proceso de indexación
REP_MODES = [
    'value',
    'change',
    'change_a_year_ago',
    'percent_change',
    'percent_change_a_year_ago'
]

API_DEFAULT_VALUES = {
    'rep_mode': 'value',
    'start': 0,
    'limit': 100
}
