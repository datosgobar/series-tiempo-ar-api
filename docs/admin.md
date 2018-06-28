# Features del panel de administrador


## Indexación manual de metadatos

Creando nuevos modelos `IndexMetadataTask` se lanzarán procesos asincrónicos para indexar metadatos de los nodos registrados al cluster de Elasticsearch. Un nuevo proceso de indexación no puede ser lanzado mientras haya algún otro ejecutándose. Se puede seguir el estado de la tarea corriendo a través de los campos del modelo.

