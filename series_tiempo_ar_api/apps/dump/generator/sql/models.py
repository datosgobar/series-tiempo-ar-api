import peewee

proxy = peewee.Proxy()


class Serie(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    distribucion_id = peewee.CharField(max_length=128)
    serie_id = peewee.CharField(max_length=128)
    indice_tiempo_frecuencia = peewee.CharField(max_length=8)
    titulo = peewee.TextField()
    unidades = peewee.TextField()
    descripcion = peewee.TextField()
    indice_inicio = peewee.DateField()
    indice_final = peewee.DateField()
    valores_cant = peewee.IntegerField(null=True)
    dias_no_cubiertos = peewee.IntegerField(null=True)


class Distribucion(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    dataset_id = peewee.CharField(max_length=128)
    identifier = peewee.CharField(max_length=128)
    titulo = peewee.TextField()
    descripcion = peewee.TextField()


class Dataset(peewee.Model):
    class Meta:
        database = proxy

    catalogo_id = peewee.CharField(max_length=64)
    identifier = peewee.CharField(max_length=128)
    titulo = peewee.TextField()
    descripcion = peewee.TextField()
    fuente = peewee.TextField()
    responsable = peewee.TextField()


class Valores(peewee.Model):
    class Meta:
        database = proxy

    serie_id = peewee.CharField(max_length=128)
    indice_tiempo = peewee.DateField()
    valor = peewee.DoubleField(null=True)
