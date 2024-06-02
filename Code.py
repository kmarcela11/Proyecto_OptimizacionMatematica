import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import ALL, MATCH
from pulp import *
import plotly.graph_objects as go

# Crear la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Estilo CSS para las tablas
tabla_style = {
    'borderCollapse': 'collapse',
    'width': '100%',
    'border': '1px solid #ddd',
    'textAlign': 'left',
}

cabecera_style = {
    'border': '1px solid #ddd',
    'padding': '8px',
    'backgroundColor': '#f2f2f2',
}

celda_style = {
    'border': '1px solid #ddd',
    'padding': '8px',
}

# Funciones para generar las tablas
def generar_tabla_gasolina(cantidad_gasolina):
    header = [
        html.Tr([html.Th("Tipo de gasolina", style=cabecera_style), html.Th("Precio de venta por barril.", style=cabecera_style)])
    ]
    rows = [
        html.Tr([html.Td(f"Tipo {i+1}", style=celda_style), html.Td(dcc.Input(id={'type': 'precio-gasolina', 'index': i+1}, type='number', placeholder='Ingrese el precio', min = 0), style=celda_style)])
        for i in range(cantidad_gasolina)
    ]
    return html.Table(header + rows, style=tabla_style)

def generar_tabla_crudo(cantidad_crudo):
    header = [
        html.Tr([html.Th("Crudo", style=cabecera_style), html.Th("Precio de compra por barril.", style=cabecera_style)])
    ]
    rows = [
        html.Tr([html.Td(f"Tipo {i+1}", style=celda_style), html.Td(dcc.Input(id={'type': 'precio-crudo', 'index': i+1}, type='number', placeholder='Ingrese el precio', min = 0 ), style=celda_style)])
        for i in range(cantidad_crudo)
    ]
    return html.Table(header + rows, style=tabla_style)

def generar_tablag(cantidad_gasolina):
    header = [
        html.Tr([html.Th("Tipo de gasolina", style=cabecera_style), html.Th("Cantidad de barriles diarios", style=cabecera_style)])
    ]
    rows = [
        html.Tr([html.Td(f"Tipo {i+1}", style=celda_style), html.Td(dcc.Input(id={'type': 'cantidad-barriles', 'index': i+1}, type='number', placeholder='Ingrese la cantidad de barriles', min = 0), style=celda_style)])
        for i in range(cantidad_gasolina)]
    return html.Table(header + rows, style=tabla_style)

def generar_tabla_gasolina_octano_azufre(cantidad_gasolina):
    header = [
        html.Tr([html.Th("Tipo de gasolina", style=cabecera_style), html.Th("Índice mínimo de octano", style=cabecera_style), html.Th("Porcentaje máximo de azufre", style=cabecera_style)])
    ]
    rows = [
        html.Tr([html.Td(f"Tipo {i+1}", style=celda_style), html.Td(dcc.Input(id={'type': 'min-octano', 'index': i+1}, type='number', placeholder='Ingrese el índice mínimo' , min = 0), style=celda_style), 
                 html.Td(dcc.Input(id={'type': 'max-azufre', 'index': i+1}, type='number', placeholder='Ingrese el porcentaje máximo', min = 0), style=celda_style)])
        for i in range(cantidad_gasolina)
    ]
    return html.Table(header + rows, style=tabla_style)

def generar_tabla_crudo_caracteristicas(cantidad_crudo):
    header = [
        html.Tr([html.Th("Crudo", style=cabecera_style), html.Th("Índice de octano", style=cabecera_style), html.Th("Azufre (%)", style=cabecera_style)])
    ]
    rows = [
        html.Tr([html.Td(f"Tipo {i+1}", style=celda_style), html.Td(dcc.Input(id={'type': 'indice-octano', 'index': i+1}, type='number', placeholder='Ingrese el índice de octano', min = 0), style=celda_style),
                  html.Td(dcc.Input(id={'type': 'porcentaje-azufre', 'index': i+1}, type='number', placeholder='Ingrese el porcentaje de azufre', min  = 0), style=celda_style)])
        for i in range(cantidad_crudo)
    ]
    return html.Table(header + rows, style=tabla_style)

def opti(valores_precios_gasolina, precio_b, cantidad_b, min_oc, max_az, indice_oc, azufre_cru, cantidad_gasolina, cantidad_crudo, restricciones):
    print(valores_precios_gasolina, precio_b, cantidad_b, min_oc, max_az, indice_oc, azufre_cru, cantidad_gasolina, cantidad_crudo, restricciones)
    
    #Crea problema de optimizacion
    problema = LpProblem("Maximizar_ganancias", LpMaximize)

    # Crear variables Gij dinámicamente utilizando dict comprehensions y rangos
    variables_G = {f"G{i}{j}": LpVariable(f"G{i}{j}", lowBound=0, cat='Integer') 
                for i in range(1, cantidad_crudo + 1) for j in range(1, cantidad_gasolina + 1)}

    # Crear variables Pi dinámicamente utilizando dict comprehensions y rangos
    variables_P = {f"P{i}": LpVariable(f"P{i}", lowBound=0, cat='Integer') 
                for i in range(1, cantidad_gasolina + 1)}

    #Funcion de costo(onjetivo)
    ganancias = 0
    costos = 0

    for j in range(1, cantidad_gasolina + 1):
        for i in range(1, cantidad_crudo + 1):
            ganancias += valores_precios_gasolina[j-1] * variables_G[f"G{i}{j}"]
        
    for i in range(1, cantidad_crudo + 1):
        for j in range(1, cantidad_gasolina + 1):
            costos += precio_b[i-1] * variables_G[f"G{i}{j}"]

    for j in range(1, cantidad_gasolina + 1):
        costos += variables_P[f"P{j}"]

    for i in range(1, cantidad_crudo + 1):
        for j in range(1, cantidad_gasolina + 1):
            costos += restricciones[1] * variables_G[f"G{i}{j}"]

    problema += ganancias - costos

    #Restricciones
    #Capacidad de compra de crudo restricciones[0]
    for i in range(1, cantidad_crudo + 1):
        suma = 0
        for j in range(1, cantidad_gasolina + 1):
            suma += variables_G[f"G{i}{j}"]

        problema += suma <= restricciones[0]
            
    #Capacidad de producción restricciones[2]
    suma2 = 0
    for i in range(1, cantidad_crudo + 1):
        for j in range(1, cantidad_gasolina + 1):
            suma2 += variables_G[f"G{i}{j}"]
    problema += suma2 <= restricciones[2]

    #Demanda estimada de gasolina  restricciones[3]
    for j in range(1, cantidad_gasolina + 1):
        sum_gas = 0
        for i in range(1, cantidad_crudo + 1):
            sum_gas += variables_G[f"G{i}{j}"]
        
        suma3 = sum_gas - restricciones[3]*variables_P[f"P{j}"]
        problema += suma3 == cantidad_b[j-1]

    #Indice minimo de azufre
    for j in range(1, cantidad_gasolina + 1):
        suma_az = 0
        suma_az2 = 0
        for i in range(1, cantidad_crudo + 1):
            suma_az += azufre_cru[i-1] * variables_G[f"G{i}{j}"]
            suma_az2 += variables_G[f"G{i}{j}"]
        
        suma_az2 = suma_az2 * max_az[j-1]
        problema += suma_az - suma_az2 <= 0

    #Indice octanaje
    for j in range(1, cantidad_gasolina + 1):
        suma_oct = 0
        suma_oct2 = 0
        for i in range(1, cantidad_crudo + 1):
            suma_oct += indice_oc[i-1] * variables_G[f"G{i}{j}"]
            suma_oct2 += variables_G[f"G{i}{j}"]
        
        suma_oct2 = suma_oct2 * min_oc[j-1]
        problema += suma_oct - suma_oct2 >= 0

    # Resolver el problema

    problema.solve(PULP_CBC_CMD(msg=False))

    # Resultados
    valores = []
    nombres = []

    for v in problema.variables():
        nombres.append(v.name)
        valores.append(v.varValue)

    resultados = (f"El valor de la función objetivo en el óptimo es: {problema.objective.value()}")

    return nombres, valores, problema.objective.value()
    
def graficas(nombres, valores):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=nombres, y=valores, name='Datos de ejemplo'))

    fig.update_layout(
    xaxis_title='Tipos de crudo',
    yaxis_title='Cantidades de barriles'   
    )
    return fig

def graficas2(nombres, valores):
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=nombres, y=valores, name='Datos de ejemplo'))

    fig2.update_layout(
    yaxis_title='Doláres invertidos en publicidad',
    xaxis_title='Tipo de gasolina'   
    )
    return fig2


# Definir el diseño de la página 1
pagina_1_layout = html.Div([
    # Pregunta 1
    html.Div([
        html.H2("Digite la cantidad de tipos de gasolina que su empresa produce:", style={'margin-top': '20px'}),
        dcc.Input(id='input-cantidad-gasolina', type='number', placeholder='Ingrese la cantidad', min=1, max=5),
    ], style={'margin-top': '20px'}),
    
    # Pregunta 2
    html.Div([
        html.H2("Digite la cantidad de crudo que usa su empresa para producir cada tipo de gasolina:", style={'margin-top': '20px'}),
        dcc.Input(id='input-cantidad-crudo', type='number', placeholder='Ingrese la cantidad', min=1, max=5),
    ], style={'margin-top': '20px'}),
    
    # Pregunta 3
    html.Div([
        html.H2("¿Cuál es la cantidad máxima de compra de barriles de petróleo crudo por día de su empresa?", style={'margin-top': '20px'}),
        dcc.Input(id='input-max-compra-barriles', type='number', placeholder='Ingrese la cantidad', min=0),
    ], style={'margin-top': '20px'}),
    
    # Pregunta 4
    html.Div([
        html.H2("¿Cuánto cuesta transformar un barril de petróleo crudo a gasolina? (Dólares)", style={'margin-top': '20px'}),
        dcc.Input(id='input-costo-transformacion', type='number', placeholder='Ingrese el costo', min=0),
    ], style={'margin-top': '20px'}),
    
    # Pregunta 5
    html.Div([
        html.H2("¿Cuál es la cantidad máxima de barriles de gasolina que puede producir diariamente?", style={'margin-top': '20px'}),
        dcc.Input(id='input-max-produccion-gasolina', type='number', placeholder='Ingrese la cantidad', min=0),
    ], style={'margin-top': '20px'}),
    
    # Pregunta 6
    html.Div([
        html.H2("Si su empresa invierte un dólar en publicidad, ¿En cuántos barriles aumenta la demanda de gasolina?",style={'margin-top': '20px'}),
        dcc.Input(id='input-publicidad', type='number', placeholder='Ingrese la cantidad', min=0),
    ], style={'margin-top': '20px'}),
    
    # Botón "Siguiente
    html.Div([
        html.Button('Siguiente', id='btn-siguiente', n_clicks=0, style={'margin-top': '20px', 'padding': '10px 20px'}),
    ]),
])

# Definir el diseño de la página 2
pagina_2_layout = html.Div([
    
    # Contenido de la página 2
    html.Div([
        html.P("A continuación, ingrese los detalles necesarios para cada tipo de gasolina y crudo."),
        html.Table(id='tabla-precios-gasolina'),
        html.Table(id='tabla-cantidad-gasolina'),
        html.Table(id='tabla-indice-octano-azufre'),
        html.Table(id='tabla-gasolina-octano-azufre'),
        html.Table(id='tabla-cantidad-crudo'),
    ], style={'margin-top': '20px'}),

    # Botón "Enviar"
    html.Div([
        html.Button('Enviar', id='btn-enviar-datos', n_clicks=0, style={'margin-top': '20px', 'padding': '10px 20px'}),
    ]),

    # Contenedor para las gráficas
    html.Div(id='graficas-container')
])


# Definir el diseño de la aplicación (contiene las páginas 1 y 2)
app.layout = html.Div([
    dcc.Store(id='store-cantidad-gasolina'),
    dcc.Store(id='store-cantidad-crudo'),
    dcc.Store(id='store-restricciones', data=[]),
    dcc.Store(id='store-precios-gasolina', data=[]),
    dcc.Store(id='store-precio-crudo', data=[]),
    dcc.Store(id='store-cantidad-barriles', data=[]),
    dcc.Store(id='store-min-octano', data=[]),
    dcc.Store(id='store-max-azufre', data=[]),
    dcc.Store(id='store-indice-octano', data=[]),
    dcc.Store(id='store-porcentaje-azufre', data=[]),
    dcc.Store(id='store-funct'),

    # Selector de páginas
    dcc.Tabs(id='tabs', value='pagina-1', children=[
        dcc.Tab(label='Datos iniciales', value='pagina-1'),
        dcc.Tab(label='Tablas/Resultados', value='pagina-2'),
    ]),
    
    # Contenedor para mostrar el contenido de la página seleccionada
    html.Div(id='page-content', children=pagina_1_layout)
])

# Callback para actualizar el contenido de la página según la pestaña seleccionada
@app.callback(
    Output('page-content', 'children'),
    [Input('tabs', 'value')]
)
# Se encarga de mostrar la página correcta. 
def display_page(tab):
    if tab == 'pagina-1':
        return pagina_1_layout
    elif tab == 'pagina-2':
        return pagina_2_layout
    else:
        return html.Div()

# Callback para almacenar las cantidades de gasolina y crudo
@app.callback(
    Output('store-cantidad-gasolina', 'data'),
    Output('store-cantidad-crudo', 'data'),
    [Input('btn-siguiente', 'n_clicks')],
    [State('input-cantidad-gasolina', 'value'),
     State('input-cantidad-crudo', 'value')]
)
def store_cantidad_gasolina_y_crudo(n_clicks, cantidad_gasolina, cantidad_crudo):
    if n_clicks > 0 and cantidad_gasolina and cantidad_crudo:
        return cantidad_gasolina, cantidad_crudo
    return dash.no_update, dash.no_update

# Callback para generar las tablas de la página 2
@app.callback(
    Output('tabla-precios-gasolina', 'children'),
    Output('tabla-cantidad-gasolina', 'children'),
    Output('tabla-indice-octano-azufre', 'children'),
    Output('tabla-gasolina-octano-azufre', 'children'),
    Output('tabla-cantidad-crudo', 'children'),
    Input('store-cantidad-gasolina', 'data'),
    Input('store-cantidad-crudo', 'data')
)
# Función para generar las tablas de la página 2
def generar_tablas_pagina_2(data_gasolina, data_crudo):
    if data_gasolina and data_crudo:
        cantidad_gasolina = data_gasolina
        cantidad_crudo = data_crudo
        return (generar_tabla_gasolina(cantidad_gasolina),
                generar_tabla_crudo(cantidad_crudo),
                generar_tablag(cantidad_gasolina),
                generar_tabla_gasolina_octano_azufre(cantidad_gasolina),
                generar_tabla_crudo_caracteristicas(cantidad_crudo))
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


#Callback para hacer el proceso de optimzacion y crear las gráficas
@app.callback(
    Output('graficas-container', 'children'),
    [Input('btn-enviar-datos', 'n_clicks')],
    [State({'type': 'precio-gasolina', 'index': ALL}, 'value'),
    State({'type': 'precio-crudo', 'index': ALL}, 'value'),
    State({'type': 'cantidad-barriles', 'index': ALL}, 'value'),
    State({'type': 'min-octano', 'index': ALL}, 'value'),
    State({'type': 'max-azufre', 'index': ALL}, 'value'),
    State({'type': 'indice-octano', 'index': ALL}, 'value'),
    State({'type': 'porcentaje-azufre', 'index': ALL}, 'value'),
    State('store-cantidad-gasolina', 'data'),
    State('store-cantidad-crudo', 'data'),
    State('store-restricciones', 'data'),]
)

# Función que realiza los procesos principales de optimización y gráficas

def store_valores(n_clicks, valores_precios_gasolina, precio_b, cantidad_b, min_oc, max_az, indice_oc, azufre_cru, cantidad_gasolina, cantidad_crudo, restricciones):
    if n_clicks > 0:
        nombres, valores, optimo = opti(valores_precios_gasolina, precio_b, cantidad_b, min_oc, max_az, indice_oc, azufre_cru, cantidad_gasolina, cantidad_crudo, restricciones)
        graficos =[]
        for j in range(1, cantidad_gasolina+1):
            nombres_grafica = []
            valores_grafica = []
            for i in range(1, cantidad_crudo+1):
                indice = nombres.index(f"G{i}{j}")
                nombres_grafica.append(nombres[indice])
                valores_grafica.append(valores[indice])
            # Utilizar un identificador único para cada gráfica
            graph_id = f'grafica-{i}'
            graph = dcc.Graph(id=graph_id, figure=graficas(nombres_grafica, valores_grafica))
            graficos.append(html.Div([html.H3(f'Gráfica gasolina tipo {j}'), graph]))
        
        nombres_grafica2 = []
        valores_grafica2 = []
        for j in range(1, cantidad_gasolina+1):
                indice = nombres.index(f"P{j}")
                nombres_grafica2.append(nombres[indice])
                valores_grafica2.append(valores[indice])

        graph_id = f'grafica-{cantidad_gasolina+1}'
        graph = dcc.Graph(id=graph_id, figure=graficas2(nombres_grafica2, valores_grafica2))
        graficos.append(html.Div([html.H3(f'Gráfica Publicidad'), graph]))

        graficos.append(html.Div([html.H3(f'El valor de la función objetivo en el óptimo es: {optimo}')]))

        return graficos
    return dash.no_update

# Callback para cambiar a la página 2 cuando se haga clic en el botón "Siguiente"
@app.callback(
    Output('tabs', 'value'),
    Output('store-restricciones', 'data'),
    [Input('btn-siguiente', 'n_clicks')],
    [State('input-cantidad-gasolina', 'value'),
     State('input-cantidad-crudo', 'value'),
     State('input-max-compra-barriles', 'value'),
     State('input-costo-transformacion', 'value'),
     State('input-max-produccion-gasolina', 'value'),
     State('input-publicidad', 'value')]
)

# Validación de que ya se hayan digitados todos los valores para poder pasar a la página 2.

def cambiar_pagina(n_clicks, cantidad_gasolina, cantidad_crudo, max_compra_barriles, costo_transformacion, max_produccion_gasolina, publicidad):
    if n_clicks > 0 and cantidad_gasolina is not None and cantidad_crudo is not None and max_compra_barriles is not None and costo_transformacion is not None and max_produccion_gasolina is not None and publicidad is not None:
        rests = [max_compra_barriles, costo_transformacion, max_produccion_gasolina, publicidad]
        return 'pagina-2', rests
    return dash.no_update, dash.no_update

# Ejecutar la aplicación

if __name__ == '__main__':
    app.run_server(debug = True) # Debug = True: la aplicación se recargará automáticamente cuando se hagan cambios en el código fuente.