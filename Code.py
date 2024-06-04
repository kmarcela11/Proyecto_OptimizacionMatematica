import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from pulp import *
import plotly.graph_objects as go


# Crear la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])

def generar_tabla_gasolina(cantidad_gasolina):
    header = [html.Tr([html.Th("Tipo de gasolina"), html.Th("Precio de venta por barril")])]
    rows = [html.Tr([html.Td(f"Tipo {i+1}"), html.Td(dcc.Input(id={'type': 'precio-gasolina', 'index': i+1}, type='number', placeholder='Ingrese el precio', min=0))]) for i in range(cantidad_gasolina)]
    return dbc.Table(header + rows, bordered=True, hover=True, responsive=True, className="mb-4", style={"border": "2px solid black","text-align": "center"})  # Aquí se establece la altura fija

def generar_tabla_crudo(cantidad_crudo):
    header = [html.Tr([html.Th("Tipo  de   Crudo"), html.Th("Precio   de   compra   por barril")])]
    rows = [html.Tr([html.Td(f"Tipo {i+1}"), html.Td(dcc.Input(id={'type': 'precio-crudo', 'index': i+1}, type='number', placeholder='Ingrese el precio', min=0))]) for i in range(cantidad_crudo)]
    return dbc.Table(header + rows, bordered=True, hover=True, responsive=True, className="mb-4", style={"border": "2px solid black", "text-align": "center"})  # Aquí se establece la altura fija

def generar_tablag(cantidad_gasolina):
    header = [html.Tr([html.Th("Tipo de gasolina"), html.Th("Cantidad de barriles diarios")])]
    rows = [html.Tr([html.Td(f"Tipo {i+1}"), html.Td(dcc.Input(id={'type': 'cantidad-barriles', 'index': i+1}, type='number', placeholder='Número de barriles ', min=0))]) for i in range(cantidad_gasolina)]
    return dbc.Table(header + rows, bordered=True, hover=True, responsive=True, className="mb-4", style={"border": "2px solid black", "text-align": "center"})

def generar_tabla_gasolina_octano_azufre(cantidad_gasolina):
    header = [html.Tr([html.Th("Tipo de gasolina"), html.Th("Índice mínimo de octano"), html.Th("Porcentaje máximo de azufre")])]
    rows = [html.Tr([html.Td(f"Tipo {i+1}"), html.Td(dcc.Input(id={'type': 'min-octano', 'index': i+1}, type='number', placeholder='Índice mínimo', min=0)), html.Td(dcc.Input(id={'type': 'max-azufre', 'index': i+1}, type='number', placeholder='Porcentaje máximo', min=0))]) for i in range(cantidad_gasolina)]
    return dbc.Table(header + rows, bordered=True, hover=True, responsive=True, className="mb-4", style={"border": "2px solid black", "text-align": "center"})

def generar_tabla_crudo_caracteristicas(cantidad_crudo):
    header = [html.Tr([html.Th("Tipo de  Crudo"), html.Th("Índice de octano"), html.Th("Azufre (%)")])]
    rows = [html.Tr([html.Td(f"Tipo {i+1}"), html.Td(dcc.Input(id={'type': 'indice-octano', 'index': i+1}, type='number', placeholder='índice de octano', min=0)), html.Td(dcc.Input(id={'type': 'porcentaje-azufre', 'index': i+1}, type='number', placeholder='Porcentaje de azufre', min=0))]) for i in range(cantidad_crudo)]
    return dbc.Table(header + rows, bordered=True, hover=True, responsive=True, className="mb-4", style={"border": "2px solid black", "text-align": "center"})


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
    fig.add_trace(go.Bar(x=nombres, y=valores, name='Datos de ejemplo', marker_color='lightblue',  # Cambiar el color de las barras
        width=0.5))

    fig.update_layout(xaxis_title='Tipos de crudo', 
                      yaxis_title='Cantidades de barriles'  ,  bargap=0.2 
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


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "11rem",
    "padding": "2rem 1rem",
    "background-color": "#212f3d",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Estilo para el pie de página
FOOTER_STYLE = {
    "position": "fixed",
    "bottom": 0,
    "left": 0,
    "width": "100%",
    "padding": "1rem",
    "background-color": "#212f3d",
    "color": "white",
    "text-align": "center",
}

sidebar = html.Div(
    [
        html.H3("BLENDEK", className="display-20", style={"color": "white"}),
        html.Hr(style={"borderTop": "1px solid white"}),
        dbc.Nav(
            [
                dbc.NavLink("Datos", href="/", active="exact"),
                dbc.NavLink("Resultados", href="/page-1", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
         # Contenido del pie de página
        html.Footer("© 2024 Blendek Inc.", style=FOOTER_STYLE)
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Store(id='grafs'),
    dcc.Location(id="url"), sidebar, content])

introducir_datos_layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("OPTIMIZACIÓN DE BLENDING"), className="text-center")
        ]),
        dbc.Row([
            dbc.Col(html.H4("Seleccione la cantidad de:"), className="mb-2")
        ]),
        dbc.Row([
            dbc.Col([
                html.H5('Tipos de gasolina'),
                dcc.Slider(id='cantidad-gasolina', min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)})
            ], width=6),
            dbc.Col([
                html.H5('Tipos de crudo'),
                dcc.Slider(id='cantidad-crudo', min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)})
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='tablas-precio-crudo', children=[])),
            dbc.Col(html.Div(id='tablas-precio-gasolina', children=[])),
            dbc.Col(html.Div(id='tablas-cantidad-gasolina', children=[])),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(html.Div(id='tablas-caracteristicas-gasolina', children=[])),
            dbc.Col(html.Div(id='tablas-caracteristicas-crudo', children=[]))
        ], className="mb-2"),
        dbc.Row([
            html.H6("¿Cuál es la cantidad máxima de compra de barriles de petróleo crudo por día de su empresa?", style={'margin-top': '20px'}),
                dcc.Input(id='input-max-compra-barriles', type='number', placeholder='Ingrese la cantidad', min=0)
        ]), 
        dbc.Row([
            html.H6("¿Cuánto cuesta transformar un barril de petróleo crudo a gasolina? (Dólares)", style={'margin-top': '20px'}),
                 dcc.Input(id='input-costo-transformacion', type='number', placeholder='Ingrese el costo', min=0)
        ]), 
        dbc.Row([
            html.H6("¿Cuál es la cantidad máxima de barriles de gasolina que puede producir diariamente?", style={'margin-top': '20px'}),
                dcc.Input(id='input-max-produccion-gasolina', type='number', placeholder='Ingrese la cantidad', min=0)
        ]), 
        dbc.Row([
            html.H6("Si su empresa invierte un dólar en publicidad, ¿En cuántos barriles aumenta la demanda de gasolina?",style={'margin-top': '20px'}),
                dcc.Input(id='input-publicidad', type='number', placeholder='Ingrese la cantidad', min=0)
        ]), 
        dbc.Row([
            html.H6("")
        ]),
        dbc.Row([
            dbc.Col(dbc.Button("OPTIMIZAR", id='boton-optimizar', color="primary", className="text-center"))
        ], className="text-center"),

    ])
])

resultado_layout = html.Div([
    html.H1("RESULTADOS", className= "text-center"),
    html.Div(id='resultado', children=[])
])

# Callback para generar las tablas 
@app.callback(
    [Output('tablas-precio-crudo', 'children'),
     Output('tablas-precio-gasolina', 'children'),
     Output('tablas-caracteristicas-crudo', 'children'),
     Output('tablas-caracteristicas-gasolina', 'children'),
     Output('tablas-cantidad-gasolina', 'children')],
    [Input('cantidad-crudo', 'value'),
     Input('cantidad-gasolina', 'value')]
)

# Función para generar las tablas
def actualizar_tablas(cantidad_crudo, cantidad_gasolina):
    tablas_precio_crudo = generar_tabla_crudo(cantidad_crudo)
    tablas_precio_gasolina = generar_tabla_gasolina(cantidad_gasolina)
    tablas_caracteristicas_crudo = generar_tabla_crudo_caracteristicas(cantidad_crudo)
    tablas_caracteristicas_gasolina = generar_tabla_gasolina_octano_azufre(cantidad_gasolina)
    tablas_cantidad_gasolina = generar_tablag(cantidad_gasolina)

    return tablas_precio_crudo, tablas_precio_gasolina, tablas_caracteristicas_crudo, tablas_caracteristicas_gasolina, tablas_cantidad_gasolina

# Callback para proceso de optimización 
@app.callback(
    Output('grafs', 'data'),
    [Input('boton-optimizar', 'n_clicks')],
    [State({'type': 'precio-crudo', 'index': ALL}, 'value'),
     State({'type': 'precio-gasolina', 'index': ALL}, 'value'),
     State({'type': 'cantidad-barriles', 'index': ALL}, 'value'),
     State({'type': 'min-octano', 'index': ALL}, 'value'),
     State({'type': 'max-azufre', 'index': ALL}, 'value'),
     State({'type': 'indice-octano', 'index': ALL}, 'value'),
     State({'type': 'porcentaje-azufre', 'index': ALL}, 'value'),
     State('cantidad-crudo', 'value'),
     State('cantidad-gasolina', 'value'),
     State('input-max-compra-barriles', 'value'),
     State('input-costo-transformacion', 'value'),
     State('input-max-produccion-gasolina', 'value'),
     State('input-publicidad', 'value'),]
)

# Función que realiza los procesos principales de optimización y gráficas

def store_valores(n_clicks, valores_precios_gasolina, precio_b, cantidad_b, min_oc, max_az, indice_oc, azufre_cru, cantidad_gasolina, cantidad_crudo, max_compra_barriles, costo_trans, max_prod_gasolina, publi):
    if n_clicks is not None and n_clicks>0 and cantidad_gasolina is not None and cantidad_crudo is not None and max_compra_barriles is not None and costo_trans is not None and max_prod_gasolina is not None and publi is not None:
        restricciones = []
        restricciones.append(max_compra_barriles)
        restricciones.append(costo_trans)
        restricciones.append(max_prod_gasolina)
        restricciones.append(publi)
        nombres, valores, optimo = opti(valores_precios_gasolina, precio_b, cantidad_b, min_oc, max_az, indice_oc, azufre_cru, cantidad_gasolina, cantidad_crudo, restricciones)
        graficos =[]
        graficos.append(
            dbc.Card(
                dbc.CardBody([
                    html.H3(f'Las ganancias máximas de la empresa son de:  {optimo} dólares'), html.H6("")
                ]),
                className="mb-11"  # Puedes ajustar las clases de estilo según sea necesario
            )
        )
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
            graficos.append(html.Div([html.H3(f'Gasolina tipo {j}'), 
                                      html.H6(f'La cantidad de barriles por cada tipo de crudo que debería invertir la empresa para producir gasolina tipo {j} es: '),
                                      graph]))
        
        nombres_grafica2 = []
        valores_grafica2 = []
        for j in range(1, cantidad_gasolina+1):
                indice = nombres.index(f"P{j}")
                nombres_grafica2.append(nombres[indice])
                valores_grafica2.append(valores[indice])

        graph_id = f'grafica-{cantidad_gasolina+1}'
        graph = dcc.Graph(id=graph_id, figure=graficas2(nombres_grafica2, valores_grafica2))
        graficos.append(
            html.Div([html.H3(f'Inversión publicidad'),
                      html.H6(f'La cantidad de dólares que la empresa debería invertir por cada tipo de gasolina es:'),
                       graph]))  
        return graficos
    
    return dash.no_update

@app.callback(
    Output('resultado', 'children'),
    Input('url', 'pathname'),
    State('grafs', 'data')
)
def pasar_grafos(path, grafs):
    if grafs is not None and path == "/page-1":
        return grafs
    

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/":
        return introducir_datos_layout
    elif pathname == "/page-1":
        return resultado_layout
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )

if __name__ == "__main__":
    app.run_server(debug=True)
