import peewee

proxy = peewee.Proxy()


class Metadatos(peewee.Model):
    class Meta:
        database = proxy
        indexes = (
            (('catalogo_id', 'dataset_id', 'distribucion_id', 'serie_id'), True),
        )

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    distribucion_id = peewee.CharField(max_length=128)
    serie_id = peewee.CharField(max_length=128, primary_key=True)

    indice_tiempo_frecuencia = peewee.CharField(max_length=8)
    serie_titulo = peewee.TextField()
    serie_unidades = peewee.TextField()
    serie_descripcion = peewee.TextField()

    distribucion_titulo = peewee.TextField()
    distribucion_descripcion = peewee.TextField()
    distribucion_url_descarga = peewee.TextField()

    dataset_responsable = peewee.TextField()
    dataset_fuente = peewee.TextField()
    dataset_titulo = peewee.TextField()
    dataset_descripcion = peewee.TextField()
    dataset_tema = peewee.TextField()

    serie_indice_inicio = peewee.DateField()
    serie_indice_final = peewee.DateField()
    serie_valores_cant = peewee.IntegerField(null=True)
    serie_dias_no_cubiertos = peewee.IntegerField(null=True)
    serie_actualizada = peewee.BooleanField()
    serie_valor_ultimo = peewee.FloatField(null=True)
    serie_valor_anterior = peewee.FloatField(null=True)
    serie_var_pct_anterior = peewee.FloatField(null=True)
    serie_discontinuada = peewee.BooleanField(null=True)

    consultas_total = peewee.IntegerField()
    consultas_30_dias = peewee.IntegerField()
    consultas_90_dias = peewee.IntegerField()
    consultas_180_dias = peewee.IntegerField()


class Valores(peewee.Model):
    class Meta:
        database = proxy
        primary_key = peewee.CompositeKey('serie_id', 'indice_tiempo')

    serie_id = peewee.ForeignKeyField(Metadatos)
    indice_tiempo = peewee.DateField()
    valor = peewee.DoubleField(null=True)


class Fuentes(peewee.Model):
    class Meta:
        database = proxy

    fuente = peewee.TextField(primary_key=True)
    series_cant = peewee.IntegerField()
    valores_cant = peewee.IntegerField()
    fecha_primer_valor = peewee.DateField()
    fecha_ultimo_valor = peewee.DateField()
