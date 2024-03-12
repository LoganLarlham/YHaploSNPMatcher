from dash import Dash, dcc, html, Input, Output, dash_table, State, callback_context
import glob
import os
import sys
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import UserCompareAADR, User_snpfilter

external_stylesheets_style = [{
    'href': '04_Dashapp/assets/bootstrap.css',
    'rel': 'stylesheet',
}]

app = Dash(__name__, external_stylesheets=external_stylesheets_style, suppress_callback_exceptions=True)
app.title = 'Y Haplogroup Matcher'

userfiles = glob.glob('01_Raw_data/TestUsers/Test*/*_DNA.txt') + glob.glob('01_Raw_data/TestUsers/Test*/*.csv')
userfiles_options = [{'label': os.path.basename(file).split('_')[0], 'value': file} for file in userfiles]

app.layout = html.Div([
    html.Div([
        html.H1('Which ancient dna sample are you most similar to?'),
        html.H2('Upload your DNA file to find out! (must be in plink format)'),
        html.H3('Matches against samples in the AADR database'),
    ], className='my-background'),
    dcc.Dropdown(
        id='userfile-dropdown',
        options=userfiles_options,
        placeholder="Select a test file or upload your own",
        className='form-control',
        style={'width': '40%', 'margin': 'auto', 'margin-bottom': '20px'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        className='form-control',
        style={
            'width': '40%', 
            'margin': 'auto', 
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin-bottom': '20px',
        },
        multiple=False
    ),
    html.Div([
        dcc.Textarea(id='haplogroup',
                   placeholder='Enter your haplogroup', 
                   style={'width': '40%',
                            'margin-left': 'auto',
                            'margin-right': 'auto',
                            'margin-bottom': '20px',
                            'textAlign': 'center',}),
        html.Button('Submit', id='submit-data', n_clicks=0, style={'width': '10%', 'margin': 'auto', 'display': 'block'})], 
        style={'textAlign': 'center'}),
    html.Div(id='output-data-upload'),
    html.Div(id='total_comparisons', style={'width': '60%', 'margin': 'auto', 'margin-top': '20px'}),
    html.Div(id='results-container', style={'width': '60%', 'margin': 'auto', 'margin-top': '20px'}),
    html.Div(id='error-message', style={'color': 'red', 'textAlign': 'center'}),
])

@app.callback(
    Output('error-message', 'children'),
    [Input('submit-data', 'n_clicks')],
    [State('userfile-dropdown', 'value'),
    State('upload-data', 'filename'),
    State('haplogroup', 'value')],
)
def update_error_message(dropdown_value, filename, haplogroup, n_clicks):
    if n_clicks is None:
        # Submit button has not been clicked; return without updating the error message
        return ''
    
    if (dropdown_value or filename) and haplogroup:
        return ''  # Return empty message if conditions are met
    else:
        return 'Please select a file and enter your haplogroup to submit.' #return error message if conditions are not met

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return decoded

@app.callback(
    [Output('results-container', 'children'),
    Output('total_comparisons', 'children')],
    [Input('submit-data', 'n_clicks')],
    [State('userfile-dropdown', 'value'),
     State('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State('haplogroup', 'value')],
    prevent_initial_call=True
)
def update_output(n_clicks, dropdown_value, upload_contents, upload_filename, haplogroup):
    if n_clicks > 0:
        file_path = None
        if upload_contents:
            content = parse_contents(upload_contents, upload_filename)
            file_path = f'03_tmpfiles/Filtered_User/{upload_filename}'
            with open(file_path, 'wb') as f:
                f.write(content)
        else:
            file_path = dropdown_value
        
        try:
            # Assuming your processing functions return a DataFrame or similar for displaying in the DataTable
            results_file_path = User_snpfilter.UserCrossref(file_path, haplogroup)
            AADR_ped_rsids, AADR_ped_meta = UserCompareAADR.getAADRData()
            results, total_compared = UserCompareAADR.getMatches(results_file_path, AADR_ped_rsids, AADR_ped_meta)
            
            return html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": results.columns[1], "id": results.columns[1]}, {"name": results.columns[6], "id": results.columns[6]}, {"name": results.columns[7], "id" : results.columns[7]} ],
                    data=results.iloc[:, [1, 6, 7]].to_dict('records'),
                    style_table={'overflowX': 'auto'}, 
                    style_cell_conditional=[{'if': {'column_id': 'non_matching_mutations'},
                                            'textAlign': 'left'}]
                )
            ]), html.Div(f'Total number of alleles compared: {total_compared}')
    
        except Exception as e:

            error_message = f'An error occurred: {e}'
            return (html.Div(error_message), html.Div('Unable to compute total comparisons due to error'))



if __name__ == '__main__':
    app.run_server(debug=True, port=6015)
