#from dash import Dash, html, dcc, callback, Input, Output
#import dash_bootstrap_components as dbc
import sequence_processor as seqpr


#import os
#from collections import Counter

#import dash_bio as dashbio
import dash_bootstrap_components as dbc
#import plotly.express as px
#from Bio.PDB import PDBList, PDBParser, parse_pdb_header
from dash import Dash, Input, Output, State, callback, ctx, dcc, html
#from dash_bio.utils import PdbParser as DashPdbParser
#from dash_bio.utils import create_mol3d_style
import base64


# Initialize the Dash app
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = dbc.Container([
    dbc.Row([
        html.Div("Sequence Splicer and Translator", className="text-primary text-center fs-3 mb-4")
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Label("Enter DNA Sequence:", className="fw-bold"),
            dbc.Input(
                id='seq-input',
                type='text',
                placeholder='e.g., ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG',
                className="mb-2"
            ),
            dbc.Label("Enter Exon Coordinates with format: \"exon1StartPos,exon1EndPos;exon2StartPos,exon2EndPos;...\"", className="fw-bold"),
            dbc.Input(
                id='ex-input',
                type='text',
                placeholder='e.g., 1,12;21,39',
                className="mb-2"
            ),
            dbc.Label("Enter Coding Sequence Coordinates with format: \"cdsStartPos,cdsEndPos\"", className="fw-bold"),
            dbc.Input(
                id='cds-input',
                type='text',
                placeholder='e.g., 4,15',
                className="mb-2"
            ),
            dbc.Row([
                dbc.Col(dbc.Button("Process Sequence", id='process-button', color="primary"), width="auto"),
                dbc.Col(dbc.Button("Reset", id='reset-button', color="danger"), width="auto"),
            ], className="g-2"),
            html.Div(id='status-message', className="mt-3")
        ], width=2),

        dbc.Col([
            html.Div(className="mt-4"),
            dcc.Upload(
                id='upload-fasta',
                children=dbc.Button('Or Upload a DNA Sequence Fasta File')
            )
        ], width="auto"),    
    ], className="mt-4"),
 
    dbc.Row([
        dbc.Col([
            dbc.Label("Mature mRNA Sequence", className="fw-bold"),
            html.Pre(
                id='mrna-output',
                className="bg-light p-3 border rounded",
                style={"whiteSpace": "pre-wrap","overflow-wrap":"break-word"}
            ),
            
            dbc.Button("Download mRNA FASTA file", id='btn-download-mrna'),
            dcc.Download(id='download-mrna'),  
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Protein Sequence", className="fw-bold"),
            html.Pre(
                id='protein-output',
                className="bg-light p-3 border rounded",
                style={"whiteSpace": "pre-wrap","overflow-wrap":"break-word"}
            ),
             
            dbc.Button("Download protein FASTA file", id='btn-download-protein'),
            dcc.Download(id='download-protein'),
            
        ])
    ]),

], fluid=True)

# callback function that takes generated mRNA sequence and downloads it as FASTA upon download button being clicked
@callback(
    Output('download-mrna', 'data'),
    Input('btn-download-mrna', 'n_clicks'),
    State('mrna-output', 'children'),
    prevent_initial_call=True
)
def download_mrna(click, mrna_sequence):

    return dict(content=(f">mrna_sequence\n{mrna_sequence}"), filename='output_mrna.fasta')

# callback funciton that takes generated protein sequence and downloads it as FASTA upon download button being clicked
@callback(
    Output('download-protein', 'data'),
    Input('btn-download-protein', 'n_clicks'),
    State('protein-output', 'children'),
    prevent_initial_call=True
)
def download_protein(click, protein_sequence):

    return dict(content=(f">protein_sequence\n{protein_sequence}"), filename='output_protein.fasta')


# callback function that takes sequence and coordinates inputs to process and return output sequences when 
# process button is clicked
@callback(
    [Output('protein-output', 'children'),
    Output('mrna-output', 'children'),
    Output('status-message', 'children')],
    Input('process-button', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    State('upload-fasta', 'contents'),
    State('seq-input', 'value'),
    State('ex-input', 'value'),
    State('cds-input', 'value'),
    prevent_initial_call=True
)
def process_sequence(process_clicks, reset_clicks, fasta_contents, dna_sequence, exon_string, cds_string):
    
    # if reset button is clicked, resets all previously output sequences
    if ctx.triggered_id == 'reset-button':
        return (
            None,
            None,
            None
        )
    
    # check if inputs are present
    if (dna_sequence and exon_string and cds_string):
        dna_sequence = dna_sequence.upper()
        input = "text"
    elif (fasta_contents and exon_string and cds_string):
        try:
            dna_sequence = parse_uploaded_fasta(fasta_contents)
            input = "uploaded file"
        except Exception:
            return (
            "",
            "",
            dbc.Alert("Please upload valid FASTA with single DNA sequence.", color="warning")
        )   
    else:
        return (
            "",
            "",
            dbc.Alert("Please enter/upload valid DNA sequence and coordinates values.", color="warning")
        )

    try:
        # process sequence and coordinates with sequence_processor module
        exon_coordinates = seqpr.coords_string_to_tuple(exon_string)
        mature_mrna = seqpr.mature_mrna_generator(dna_sequence, exon_coordinates)
        cds_positions = seqpr.cds_pos_to_tuple(cds_string)
        protein_sequence = seqpr.mrna_translator(mature_mrna, cds_positions)

        return (f"{protein_sequence}",
                f"{mature_mrna}",
                html.Div([
                    dbc.Alert(f"Successfully processed sequence from {input}", color='success')
                ])
        )

    # uses SystemExit as exception to handle because sequence_processor module handles invalid inputs with sys.exit(1)
    except SystemExit:
        return (
            None,
            None,
            dbc.Alert("Please enter/upload valid DNA sequence and coordinates values.", color="warning")
        )

    # handles all other exceptions not handled in sequence_processor module
    except Exception as e:
        return (
            None,
            None,
            f"Error: {e}"
            )


def parse_uploaded_fasta(contents: str) -> str:
    """
    Given input FASTA file contents from uploaded file, converts to Python string, processes, and returns sequence.

    Args:
        contents: FASTA file contents from uploaded file as a string

    Returns:
        returns the sequence from the FASTA file as a string
    """
    
    #split the content information from the actual content and convert to Python string
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')

    # iterates through decoded contents line by line to check for unique sequences and add sequence lines to a list
    sequence_counter = 0
    sequence_lines = []
    for line in decoded.splitlines():
        if line.startswith(">"):
            sequence_counter += 1
        elif line.strip() and not line.startswith(">"):
            sequence_lines.append(line.strip())

    # if there is more or less than one sequnence in the file, raises exception
    if sequence_counter != 1:
        raise Exception
    
    # join the sequence fragments from the list into one string that is returned
    return "".join(sequence_lines).upper()
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)