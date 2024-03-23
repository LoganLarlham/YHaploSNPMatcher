#This script is a Dash app that allows users to upload their DNA files and compare them to the AADR database.

#import necessary Dash modules and other libraries

from dash import Dash, dcc, html, Input, Output, dash_table, State
import glob
import os
import sys
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets/scripts')))

# import necessary functions from scripts
from assets.scripts import UserCompareAADR, User_snpfilter
from assets.scripts.UserCompareAADR import AADR_data, AADR_metadata_subset

# initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Y Haplogroup Matcher'

#get the test files
userfiles = glob.glob('01_Raw_data/TestUsers/Test*/*_DNA.txt') + glob.glob('01_Raw_data/TestUsers/Test*/*.csv')
userfiles_options = [{'label': os.path.basename(file).split('_')[0], 'value': file} for file in userfiles]

#Define app layout, dropdown for selecting test file, file upload box for using your own file,
# haplogroup input, number of results to display, and submit button
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
        html.Div('Number of results to display:', style={'margin-bottom': '10px'}),
        dcc.Dropdown(id='num_results',
                     options=[{'label': i, 'value': i} for i in range(5, 51, 5)],
                     value=25,
                     style={'width': '40%',
                            'margin-left': 'auto',
                            'margin-right': 'auto',
                            'margin-bottom': '20px',
                            'textAlign': 'center',}),
        html.Button('Submit', id='submit-data', n_clicks=0, style={'width': '10%', 'margin': 'auto', 'display': 'block'})], 
        style={'textAlign': 'center'}),
    html.Div(id='output-data-upload'),
    html.Div(id='total_comparisons', style={'width': '60%', 'margin': 'auto', 'margin-top': '20px'}),
    html.Div([
        html.Div(id='results-container', style={'width': '45%', 'margin-right': '5%'}),
        html.Div(id='additional-data', style={'width': '45%', 'margin-left': '5%'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '90%', 'margin': 'auto'}),
    html.Div(id='error-message', style={'color': 'red', 'textAlign': 'center'}),
])


#define callback to parse the uploaded file and display name of file
@app.callback(
    Output('error-message', 'children'),
    [Input('submit-data', 'n_clicks'),
    Input('results-container', 'children')],
    [State('userfile-dropdown', 'value'),
    State('upload-data', 'filename'),
    State('haplogroup', 'value')],
)
def update_error_message(dropdown_value, filename, haplogroup, n_clicks, results_children):
    if n_clicks is None or results_children:
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


#callback to take info from boxes when submit button is clicked and run comparison functions.
@app.callback(
    [Output('results-container', 'children'),
    Output('total_comparisons', 'children')],
    [Input('submit-data', 'n_clicks')],
    [State('userfile-dropdown', 'value'),
     State('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State('haplogroup', 'value'),
     State('num_results', 'value')],
    prevent_initial_call=True
)
#function which runs the comparison functions, creates a table of results, and returns the table
def update_output(n_clicks, dropdown_value, upload_contents, upload_filename, haplogroup, num_results):
    if n_clicks > 0: #only run if submit button has been clicked
        file_path = None #initialize file_path variable
        if upload_contents: #if a file has been uploaded, parse the contents and write to a temporary file
            content = parse_contents(upload_contents, upload_filename)
            file_path = f'03_tmpfiles/Filtered_User/{upload_filename}'
            with open(file_path, 'wb') as f:
                f.write(content)
        else:
            file_path = dropdown_value
        
        try:
            # Run the comparison functions from UserCompareAADR.py and User_snpfilter.py scripts
            results_file_path = User_snpfilter.UserCrossref(file_path, haplogroup)
            AADR_ped_rsids, AADR_ped_meta = AADR_data
            results, total_compared = UserCompareAADR.getMatches(results_file_path, AADR_ped_rsids, AADR_ped_meta, num_results)

            #return the results in a table, selecting only desired columns
            return html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": results.columns[1], "id": results.columns[1]}, {"name": results.columns[6], "id": results.columns[6]}, {"name": results.columns[7], "id" : results.columns[7]} ],
                    data=results.iloc[:, [1, 6, 7]].to_dict('records'),
                    style_table={'overflowX': 'auto'}, 
                    style_data_conditional=[
                        {'if': {'column_id': 'non_matching_mutations'}, 'textAlign': 'left'}
                        ]     
                        ) #add some text which shows the total number of comparisons and instructs you to click a row for more info
            ]),  html.Div([html.P(f'Total number of alleles compared: {total_compared}'), html.P('Click a match for additional info')])
    
        
        except ValueError as e:

            error_message = f'An error occurred: {e}'
            return (html.Div(error_message), html.Div('Unable to compute total comparisons due to error'))

#callback to display additional data when a row is clicked
@app.callback(
    Output('additional-data', 'children'),
    [Input('table', 'active_cell'),
     Input('table', 'data')],
    prevent_initial_call=True
)
#function to get the additional data for the individual when a row is clicked
def display_additional_data(active_cell, data):
    if active_cell:
        try:
            # get the row that was clicked
            row = data[active_cell['row']]
            # get the individual id from the row
            individual_id = row['GeneticID']
            # get the individual data from the AADR_metadata_subset data frame
            additional_detail = UserCompareAADR.getMetaData(individual_id, AADR_metadata_subset)
            # return the individual data
            return html.Div([
                dash_table.DataTable(
                    id='additional-table',
                    columns=[{"name": i, "id": i} for i in additional_detail.columns],
                    data=additional_detail.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                )
            ])
        except Exception as e:
            # If an error occurs, return a Div containing the error message
            return html.Div([
                'An error occurred: ', str(e),
                dash_table.DataTable(id='additional-table')
            ])
    else:
        return html.Div()

#run the app, run on port 6015 (chosen randomly, becaause default was often in use)
if __name__ == '__main__':
    app.run_server(debug=True, port=6015)
