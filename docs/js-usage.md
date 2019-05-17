# Usar en componentes web

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Con `TSComponents`](#con-tscomponents)
    - [`graphic`](#graphic)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Con `TSComponents`

El objeto TSComponents fue desarrollado por el equipo de Datos Argentina para simplificar el uso de la API de Series de Tiempo en experiencias web.

Consiste de una librería JS y una hoja de estilos CSS versionadas en un CDN con distintos componentes diseñados para funcionar fácilmente con la API.

Ver más en la [documentación de TSComponents](https://datosgobar.github.io/series-tiempo-ar-explorer/reference/ts-components/).

### `graphic`

El componente `graphic` permite embeber gráficos de líneas, áreas o barras en experiencias web. Permite elegir distintos elementos de filtro de fechas, personalizar los textos, etc.

<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_1.18.2/dist/js/components.js'></script>
<link rel='stylesheet' type='text/css' href='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_1.18.2/dist/css/components.css'/>

<div id="tmi"></div>

<script>
    window.onload = function() {
        TSComponents.Graphic.render('tmi', {
            graphicUrl: 'https://apis.datos.gob.ar/series/api/series/?ids=tmi_arg',
            title: 'Tasa de Mortalidad Infantil de Argentina',
            source: 'Dirección de Estadística e Información en Salud (DEIS). Secretaría de Gobierno de Salud'
        })
    }
</script>

<br>
<br>
Este gráfico se genera a partir del siguiente código:
<br>

```html
<!-- importa librería JS -->
<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_1.18.2/dist/js/components.js'></script>

<!-- importa hoja de estilos CSS -->
<link rel='stylesheet' type='text/css' href='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_1.18.2/dist/css/components.css'/>

<!-- código HTML donde ubicar un div con un gráfico -->
<div id="tmi"></div>

<!-- JS que genera el gráfico en el div -->
<script>
    window.onload = function() {
        TSComponents.Graphic.render('tmi', {
            // Llamada a la API de Series de Tiempo
            graphicUrl: 'https://apis.datos.gob.ar/series/api/series/?ids=tmi_arg',
            title: 'Tasa de Mortalidad Infantil de Argentina',
            source: 'Dirección de Estadística e Información en Salud (DEIS). Secretaría de Gobierno de Salud'
        })
    }
</script>
```

Ver [referencia completa del componente `graphic`](https://datosgobar.github.io/series-tiempo-ar-explorer/reference/ts-components/graphic/).
