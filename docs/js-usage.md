# Usar en componentes web

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
 

- [Con `TSComponents`](#con-tscomponents)
    - [`card`](#card)
    - [`graphic`](#graphic)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<link type="text/css" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.8.2/css/all.min.css" media="all" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_2.0.0/dist/css/components.css" type="text/css">
<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_2.0.0/dist/js/components.js'></script>

<style>
.row {
    width: 90%;
    margin: auto;
    display: flex;
    justify-content: space-around;
}
</style>

## Con `TSComponents`

El objeto TSComponents fue desarrollado por el equipo de Datos Argentina para simplificar el uso de la API de Series de Tiempo en experiencias web.

Consiste de una librería JS y una hoja de estilos CSS versionadas en un CDN con distintos componentes diseñados para funcionar fácilmente con la API.

Ver más en la [documentación de TSComponents](https://datosgobar.github.io/series-tiempo-ar-explorer/reference/ts-components/).

### `card`

El componente `card` permite embeber el último valor de un indicador en experiencias web para armar tableros o indicadores testigo. El objeto es altamente personalizable y tiene muchas variantes.

<div class="row">
    <div id="ipc"></div>
    <div id="exportaciones"></div>
</div>

Estas tarjetas se generan a partir del siguiente código:
<br>

```html
<!-- importa librería JS -->
<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_2.0.0/dist/js/components.js'></script>

<!-- importa hoja de estilos CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_2.0.0/dist/css/components.css" type="text/css">
<link type="text/css" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.8.2/css/all.min.css" media="all" />

<!-- estilo para ordenar las tarjetas en filas -->
<style>
.row {
    width: 90%;
    margin: auto;
    display: flex;
    justify-content: space-around;
}
</style>

<!-- código HTML donde ubicar divs con cards, en rows -->
<div class="row">
    <div id="ipc"></div>
    <div id="exportaciones"></div>
</div>

<!-- JS que genera el gráfico en el div -->
<script>
    window.onload = function() {
        TSComponents.Card.render('ipc', {
            serieId: '148.3_INIVELNAL_DICI_M_26:percent_change',
            color: '#F9A822',
            title: "Indice de Precios al Consumidor Nacional",
            links: "none"
        })

        TSComponents.Card.render('exportaciones', {
            serieId: '74.3_IET_0_M_16:percent_change_a_year_ago',
            explicitSign: true,
            title: "Exportaciones",
            links: "none"
        })
    }
</script>
```

Ver [referencia completa del componente `card`](https://datosgobar.github.io/series-tiempo-ar-explorer/reference/ts-components/card/).

### `graphic`

El componente `graphic` permite embeber gráficos de líneas, áreas o barras en experiencias web. Permite elegir distintos elementos de filtro de fechas, personalizar los textos, etc.

<div id="tmi"></div>

<br>
<br>
Este gráfico se genera a partir del siguiente código:
<br>

```html
<!-- importa librería JS -->
<script type='text/javascript' src='https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_2.0.0/dist/js/components.js'></script>

<!-- importa hoja de estilos CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/datosgobar/series-tiempo-ar-explorer@ts_components_2.0.0/dist/css/components.css" type="text/css">

<!-- código HTML donde ubicar un div con un gráfico -->
<div id="tmi"></div>

<!-- JS que genera las tarjetas en sus divs -->
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

<script>
    window.onload = function() {
        TSComponents.Graphic.render('tmi', {
            graphicUrl: 'https://apis.datos.gob.ar/series/api/series/?ids=tmi_arg',
            title: 'Tasa de Mortalidad Infantil de Argentina',
            source: 'Dirección de Estadística e Información en Salud (DEIS). Secretaría de Gobierno de Salud'
        })

        TSComponents.Card.render('ipc', {
            serieId: '148.3_INIVELNAL_DICI_M_26:percent_change',
            color: '#F9A822',
            hasChart: 'small',
            title: "Indice de Precios al Consumidor Nacional",
            links: "none"
        })

        TSComponents.Card.render('exportaciones', {
            serieId: '74.3_IET_0_M_16:percent_change_a_year_ago',
            explicitSign: true,
            hasChart: 'small',
            title: "Exportaciones",
            links: "none"
        })
    }
</script>
