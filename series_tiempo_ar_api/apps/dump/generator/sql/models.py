import peewee

proxy = peewee.Proxy()


class Dataset(peewee.Model):
    class Meta:
        database = proxy
        primary_key = peewee.CompositeKey('catalogo_id', 'identifier')

    catalogo_id = peewee.CharField(max_length=64)
    identifier = peewee.CharField(max_length=128)
    titulo = peewee.TextField()
    descripcion = peewee.TextField()
    fuente = peewee.TextField(null=True)
    responsable = peewee.TextField()


class Distribucion(peewee.Model):
    class Meta:
        database = proxy
        primary_key = peewee.CompositeKey('catalogo_id', 'identifier')

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    identifier = peewee.CharField(max_length=128)
    titulo = peewee.TextField()
    descripcion = peewee.TextField()


class Serie(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    distribucion_id = peewee.CharField(max_length=128)
    serie_id = peewee.CharField(max_length=128, primary_key=True)
    indice_tiempo_frecuencia = peewee.CharField(max_length=8)
    titulo = peewee.TextField()
    unidades = peewee.TextField()
    descripcion = peewee.TextField()
    indice_inicio = peewee.DateField()
    indice_final = peewee.DateField()
    valores_cant = peewee.IntegerField(null=True)
    dias_no_cubiertos = peewee.IntegerField(null=True)


class Valores(peewee.Model):
    class Meta:
        database = proxy
        primary_key = peewee.CompositeKey('serie_id', 'indice_tiempo')

    serie_id = peewee.CharField(max_length=128)
    indice_tiempo = peewee.DateField()
    valor = peewee.DoubleField(null=True)


class Fuente(peewee.Model):
    class Meta:
        database = proxy

    fuente = peewee.TextField(primary_key=True)
    series_cant = peewee.IntegerField()
    valores_cant = peewee.IntegerField()
    fecha_primer_valor = peewee.DateField()
    fecha_ultimo_valor = peewee.DateField()
