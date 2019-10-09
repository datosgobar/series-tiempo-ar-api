import decimal
import math

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
        figure = infer_decimals(value)
        figures = max(figures, -figure)

    return figures


# Adiviná si lo robé de SO
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def infer_decimals(value):
    """
    Devuelve la cantidad de cifras decimales del valor, aplicando una heurística de corrección
    previa.

    Para valores del estilo 1.0000000000000001, (común al serializar números en punto flotante),
    se los trunca a 17 - N dígitos, siendo N la cantidad de dígitos enteros del mismo indicador.
    El objetivo es recortar el margen de error dado por la precisión en floats. De esta manera,
    el valor del ejemplo anterior, 1.0000000000000001, pasa a 1.000000000000000 -> 1.0
    """
    integer_digits = len(str(int(math.modf(value)[1])))
    truncated = truncate(value, 17 - integer_digits)
    return decimal.Decimal(str(truncated)).normalize().as_tuple().exponent
