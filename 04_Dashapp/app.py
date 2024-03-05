from dash import Dash, dcc, html, Input, Output, dash_table
import glob
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from scripts import UserCompareAADR, User_snpfilter


app = Dash(__name__)

# Get a list of user files from the 03_tmpfiles directory
userfiles = glob.glob('01_Raw_data/TestUsers/Test*/*_DNA.txt') + glob.glob('01_Raw_data/TestUsers/Test*/*.csv')
userfiles_options = [{'label': os.path.basename(file).split('_')[0], 'value': file} for file in userfiles]

app.layout = html.Div([
    dcc.Dropdown(id='userfile-dropdown', options=userfiles_options, value=userfiles[0]),
    html.Div(id='results-container')
])

@app.callback(
    Output('results-container', 'children'),
    [Input('userfile-dropdown', 'value')]
)
def update_results(selected_file):
    try:
        #generate filtered file and return path
        results_file_path = User_snpfilter.UserCrossref(selected_file)
        
        # Call a function from data_processing to process the file and get results
        results = UserCompareAADR.getMatches(results_file_path)
        
        # Generate HTML table or other components to display results
        # This is just a placeholder, replace with your actual result presentation logic
        return html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in results.columns],
                data=results.to_dict('records'),
                style_table={'overflowX': 'auto'},  # Optional: adds horizontal scrollbar if table exceeds container width
        )
    ])
    except Exception as e:
        # If an error occurs, return a Div containing the error message
        return html.Div([
            'An error occurred: ', str(e)
        ])
if __name__ == '__main__':
    app.run_server(debug=True)