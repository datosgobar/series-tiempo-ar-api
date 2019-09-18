import decimal

import numpy as np


def significant_figures(serie):
    """Devuelve la cantidad de cifras significativas de una serie (iterable)
    El valor es el *máximo* de todos los valores del iterable. Es decir,
    si una serie tiene un indicador con 2 cifras significativas, y otro con 3,
    se interpreta que la serie tendrá 3 cifras significativas (y el primer indicador
    con 2 debería representarse con zero-padding a 3 cifras al usuario).
    """

    figures = 0
    serie = [x for x in serie if not np.isnan(x)]
    for value in serie:
        figure = decimal.Decimal(str(value)).normalize().as_tuple().exponent
        figures = max(figures, -figure)

    return figures
