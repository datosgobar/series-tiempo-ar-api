import json
import pandas as pd

from series_tiempo_ar.helpers import freq_iso_to_pandas
from django_datajsonar.models import Field, Distribution

from series_tiempo_ar_api.libs.datajsonar_repositories.series_repository import SeriesRepository
from series_tiempo_ar_api.libs.indexing import constants


def init_df(distribution: Distribution, time_index: Field):
    """Inicializa el DataFrame del CSV de la distribución pasada,
    seteando el índice de tiempo correcto y validando las columnas
    dentro de los datos
    """
    distribution.refresh_from_db()  # Recarga la distribución si ya fue leída
    df = read_distribution_csv_as_df(distribution, time_index)
    fields = SeriesRepository.get_present_series(distribution=distribution)
    drop_null_or_missing_fields_from_df(df, [field.title for field in fields])

    data = df.values
    new_index = generate_df_time_index(df, time_index)
    identifiers = get_distribution_series_identifers(distribution, series_titles=df.columns)
    return pd.DataFrame(index=new_index, data=data, columns=identifiers)


def read_distribution_csv_as_df(distribution: Distribution, time_index: Field) -> pd.DataFrame:
    df = pd.read_csv(distribution.data_file,
                     parse_dates=[time_index.title],
                     index_col=time_index.title,
                     float_precision='high')
    return df


def drop_null_or_missing_fields_from_df(df, field_titles):
    for column in df.columns:
        all_null = df[column].isnull().all()
        if all_null or column not in field_titles:
            df.drop(column, axis='columns', inplace=True)


def get_distribution_time_index_periodicity(time_index: Field) -> str:
    periodicity = json.loads(time_index.metadata)[constants.SPECIAL_TYPE_DETAIL]
    return periodicity


def generate_df_time_index(df: pd.DataFrame, time_index: Field):
    periodicity = get_distribution_time_index_periodicity(time_index)
    freq = freq_iso_to_pandas(periodicity)
    new_index = pd.date_range(df.index[0], df.index[-1], freq=freq)

    # Chequeo de series de días hábiles (business days)
    if freq == constants.DAILY_FREQ and new_index.size > df.index.size:
        new_index = pd.date_range(df.index[0],
                                  df.index[-1],
                                  freq=constants.BUSINESS_DAILY_FREQ)
    return new_index


def get_distribution_series_identifers(distribution: Distribution, series_titles: list) -> list:
    identifier_for_each_title = {s.title: s.identifier
                                 for s in SeriesRepository.get_present_series(distribution=distribution)}
    return [identifier_for_each_title[title] for title in series_titles]
