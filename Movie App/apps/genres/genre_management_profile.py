from urllib.parse import parse_qs, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB, modifyDB

layout = html.Div(
    [

        dcc.Store(id='genreprofile_genreid', storage_type='memory', data=0),
        
        html.H2('Genre Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='genreprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Title", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='genreprofile_name',
                                placeholder="Title"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                # dbc.Row(
                #     [
                #         dbc.Label("Genre", width=1),
                #         dbc.Col(
                #             html.Div(
                #                 dcc.Dropdown(
                #                     id='movieprofile_genre',
                #                     placeholder='Genre'
                #                 ),
                #                 className='dash-bootstrap'
                #             ),
                #             width=5,
                #         )
                #     ],
                #     className='mb-3'
                # ),
                # dbc.Row(
                #     [
                #         dbc.Label("Release Date", width=1),
                #         dbc.Col(
                #             dcc.DatePickerSingle(
                #                 id='movieprofile_releasedate',
                #                 placeholder='Release Date',
                #                 month_format='MMM Do, YY',
                #             ),
                #             width=5, 
                #             className='dash-bootstrap'
                #         )
                #     ],
                #     className='mb-3'
                # ),
                html.Div(
                    [
                        dbc.Checklist(
                            id='genreprofile_deleteind',
                            options= [dict(value=1, label="Mark as Deleted")],
                            value=[] 
                        )
                    ], 
                    id='genreprofile_deletediv'
                )

            ]
        ),
          dbc.Button(
            'Submit',
            id='genreprofile_submit',
            n_clicks=0 # Initialize number of clicks
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Message here! Edit me please!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/genres/genre_management' # Clicking this would lead to a change of pages
                    )
                )
            ],
            centered=True,
            id='genreprofile_successmodal',
            backdrop='static' # Dialog box does not go away if you click at the background
        )
    ]
)

@app.callback(
    [
        # Output('movieprofile_genre', 'options'),
        Output('genreprofile_genreid', 'data'),
        Output('genreprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search'),
    ]
)
def movieprofile_populategenres(pathname, urlsearch):
    if pathname == '/genres/genre_management_profile':
        # sql = """
        # SELECT genre_name as label, genre_id as value
        # FROM genres 
        # WHERE genre_delete_ind = False
        # """
        # values = []
        # cols = ['label', 'value']

        # df = getDataFromDB(sql, values, cols)
        # # The output must be a dictionary with the following structure
        # # options=[
        # #     {'label': "Factorial", 'value': 1},
        # #     {'label': "Palindrome Checker", 'value': 2},
        # #     {'label': "Greeter", 'value': 3},
        # # ]

        # genre_options = df.to_dict('records')

        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]
        
        if create_mode == 'add':
            genreid = 0
            deletediv = 'd-none'
        else:
            genreid = int(parse_qs(parsed.query)['id'][0])
            deletediv = ''
        
        return [genreid, deletediv]
    else:
        raise PreventUpdate

        
@app.callback(
    [
        # dbc.Alert Properties
        Output('genreprofile_alert', 'color'),
        Output('genreprofile_alert', 'children'),
        Output('genreprofile_alert', 'is_open'),
        # dbc.Modal Properties
        Output('genreprofile_successmodal', 'is_open')
    ],
    [
        # For buttons, the property n_clicks 
        Input('genreprofile_submit', 'n_clicks')
    ],
    [
        # The values of the fields are States 
        # They are required in this process but they 
        # do not trigger this callback
        State('genreprofile_name', 'value'),
        # State('movieprofile_genre', 'value'),
        # State('movieprofile_releasedate', 'date'),

        State('url', 'search'),
        State('genreprofile_genreid', 'data'),
        State('genreprofile_deleteind', 'value'),
    ]
)
def movieprofile_saveprofile(submitbtn, title, urlsearch, 
                             genreid, deleteind):
    ctx = dash.callback_context
    # The ctx filter -- ensures that only a change in url will activate this callback
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]

        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]

    else:
        raise PreventUpdate

    if eventid == 'genreprofile_submit' and submitbtn:
        # the submitbtn condition checks if the callback was indeed activated by a click
        # and not by having the submit button appear in the layout

        # Set default outputs
        alert_open = False
        modal_open = False
        alert_color = ''
        alert_text = ''

        # We need to check inputs
        if not title: # If title is blank, not title = True
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply the movie title.'
        # elif not genre:
        #     alert_open = True
        #     alert_color = 'danger'
        #     alert_text = 'Check your inputs. Please supply the movie genre.'
        # elif not releasedate:
        #     alert_open = True
        #     alert_color = 'danger'
        #     alert_text = 'Check your inputs. Please supply the movie release date.'
        else: # all inputs are valid
            # Add the data into the db

            if create_mode == 'add':
                sql = '''
                    INSERT INTO genres (genre_name)
                    VALUES (%s)
                '''
                values = [title]

            elif create_mode == 'edit':
                sql = '''
                    UPDATE genres 
                    SET 
                        genre_name = %s,
                        genre_delete_ind = %s
                    WHERE
                        genre_id = %s
                '''
                values = [title, 
                          bool(deleteind),
                          genreid]

            else:
                raise PreventUpdate

            modifyDB(sql, values)

            # If this is successful, we want the successmodal to show
            modal_open = True

        return [alert_color, alert_text, alert_open, modal_open]

    else: 
        raise PreventUpdate


@app.callback(
    [
        Output('genreprofile_name', 'value'),
        # Output('movieprofile_genre', 'value'),
        # Output('movieprofile_releasedate', 'date'),
    ],
    [
        Input('genreprofile_genreid', 'modified_timestamp')
    ],
    [
        State('genreprofile_genreid', 'data'),
    ]
)
def movieprofile_loadprofile(timestamp, genreid):
    if genreid: # check if genreid > 0

        # Query from db
        sql = """
            SELECT genre_name
            FROM genres
            WHERE genre_id = %s
        """
        values = [genreid]
        # col = ['genre_name', 'genreid', 'releasedate']
        col = ['genre_name']

        df = getDataFromDB(sql, values, col)

        if not df.empty:
            genrename=df['genre_name'][0]
            return[genrename]
        # genrename = df['genrename'][0]
        # # Our dropdown list has the genreids as values then it will 
        # # display the correspoinding labels
        
        # genreid = int(df['genreid'][0])
        # # releasedate = df['releasedate'][0]

        # return [genrename, genreid]

    else:
        raise PreventUpdate