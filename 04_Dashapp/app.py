
# √ need to add functionality to upload a user file
# √ need to change formatting of page
# √ need to change data displayed into the table
#need to add hover/click functionality to the table
#need to add a button to download the results



from dash import Dash, dcc, html, Input, Output, dash_table
import glob
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from scripts import UserCompareAADR, User_snpfilter




#External CSS Stylesheets
external_stylesheets_style = [{
    'href': '04_Dashapp/assets/bootstrap.css',
    'rel': 'stylesheet',
}]

# Add the external_stylesheets to the app
app = Dash(__name__, external_stylesheets=external_stylesheets_style)
app.title = 'Y Haplogroup Matcher'

# Get a list of user files from the 03_tmpfiles directory
userfiles = glob.glob('01_Raw_data/TestUsers/Test*/*_DNA.txt') + glob.glob('01_Raw_data/TestUsers/Test*/*.csv')
userfiles_options = [{'label': os.path.basename(file).split('_')[0], 'value': file} for file in userfiles]

# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.H1('Which ancient dna sample are you most similar to?'),
        html.H2('Upload your DNA file to find out! (must be in plink format)'),
        html.H3('Matches against samples in the AADR database'),
    ], className='my-background'),
    dcc.Dropdown(
        id='userfile-dropdown',
        options=userfiles_options, 
        value=userfiles[0],
        className='form-control',
        style={'width': '40%', 'margin': 'auto'}),
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
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Button('Clear', id='clear-upload', n_clicks=0, style={'display': 'none'}),  
    html.Div(id='output-data-upload'),
    html.Div(id='results-container',
             style={'width': '40%', 'margin': 'auto'})
])

#callback to update upload box to show the name of uploaded file and clear button
@app.callback(
    Output('upload-data', 'style'),
    Output('upload-data', 'children'),
    Input('upload-data', 'filename'),
    Input('upload-data', 'contents'),
    Input('clear-upload', 'n_clicks')
)

#function to update the upload box
def update_upload_box(filename, contents, n_clicks):
    if n_clicks:
        return {
            'width': '40%', 
            'margin': 'auto', 
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
        }, html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ])
    elif contents is not None:
        return {
            'width': '40%', 
            'margin': 'auto', 
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'backgroundColor': '#00cc85' 
        }, html.Div([
            f'File uploaded: {filename}',
            html.Button('Clear', id='clear-upload', n_clicks=0)
        ])
    else:
        return {
            'width': '40%', 
            'margin': 'auto', 
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
        }, html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ])

#callback to update the results container when a file is selected/uploaded
@app.callback(
    Output('results-container', 'children'),
    [Input('userfile-dropdown', 'value'),
    Input('upload-data', 'contents')],
    prevent_initial_call=True
    )

#function to update the results container
def update_results(selected_file, uploaded_file):
    try:
        # If a file was uploaded, use the uploaded file
        if uploaded_file is not None:
            # Get the file content
            content = uploaded_file.read()
            # Get the file name
            filename = uploaded_file.filename
            # Save the file
            with open(f'03_tmpfiles/Filtered_User/{filename}', 'wb') as f:
                f.write(content)
            # Set the selected file to the uploaded file
            selected_file = f'03_tmpfiles/Filtered_User/{filename}'
        else:
            # If no file was uploaded, use the selected file
            selected_file = selected_file
        #generate filtered file and return path
        results_file_path = User_snpfilter.UserCrossref(selected_file)
        
        # Call function from UserCompareAADR to process the file and get results
        results = UserCompareAADR.getMatches(results_file_path)
        
        # Generate HTML table or other components to display results
        # This is just a placeholder, replace with your actual result presentation logic
        return html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": results.columns[1], "id": results.columns[1]}, {"name": results.columns[6], "id": results.columns[6]}],
                data=results.iloc[:, [1, 6]].to_dict('records'),
                style_table={'overflowX': 'auto'},  # Optional: adds horizontal scrollbar if table exceeds container width
            )
        ])
    except Exception as e:
        # If an error occurs, return a Div containing the error message
        return html.Div([
            'An error occurred: ', str(e)
        ])

#callback to allow user to hover over a result and see additional detail, and click to change results container to additional detail
@app.callback(
    Output('results-container', 'children'),
    [Input('table', 'active_cell')],
    [Input('table', 'data')],
    prevent_initial_call=True
    )

#function to update the results container for additional detail
def update_results(active_cell, data):
    try:
        if active_cell:
            #get the row that was clicked
            row = data[active_cell['row']]
            #get the individual id from the row
            individual_id = row['GeneticID']
            #get the individual data from the AADR_metadata_subset data frame
            additional_detail = UserCompareAADR.getMetaData(individual_id)
            #return the individual data
    except Exception as e:
        # If an error occurs, return a Div containing the error message
        return html.Div([
            'An error occurred: ', str(e)
        ])
#run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=6015)