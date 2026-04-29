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
            dbc.Label("Enter Exon Coordinates with format: \"exon1_StartPos,exon1_EndPos;exon2_StartPos,exon2_EndPos\"", className="fw-bold"),
            dbc.Input(
                id='ex-input',
                type='text',
                placeholder='e.g., 1,12;21,39',
                className="mb-2"
            ),
            dbc.Label("Enter Coding Sequence Coordinates with format: \"CDS_StartPos,CDS_EndPos\"", className="fw-bold"),
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
            html.Div(className="my-4"),
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
                style={
                    "whiteSpace": "pre-wrap",
                    "wordBreak": "break-word"
                }
            ),
            #AI Usage: 
            dbc.Button("Download mRNA FASTA file", id='btn-download-mrna'),
            dcc.Download(id='download-mrna'),
            dcc.Store(id='mrna-store')
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Protein Sequence", className="fw-bold"),
            html.Pre(
                id='protein-output',
                className="bg-light p-3 border rounded",
                style={
                    "whiteSpace": "pre-wrap",
                    "wordBreak": "break-word"
                }
            ),
            #AI Usage: 
            dbc.Button("Download protein FASTA file", id='btn-download-protein'),
            dcc.Download(id='download-protein'),
            dcc.Store(id='protein-store')
        ])
    ]),

], fluid=True)

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
    
    if ctx.triggered_id == 'reset-button':
        return (
            None,
            None,
            None
        )
    
    if (dna_sequence and exon_string and cds_string):
        dna_sequence = dna_sequence.upper()
        input = "text"
    elif (fasta_contents and exon_string and cds_string):
        dna_sequence = parse_uploaded_fasta(fasta_contents)
        input = "uploaded file"
    else:
        return (
            "",
            "",
            dbc.Alert("Please enter/upload valid DNA sequence and coordinates values.", color="warning")
        )
    

    try:
        
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

    except SystemExit:
        return (
            None,
            None,
            "Invalid input. Please check your sequence and coordinate positions."

        )

    except Exception as e:
        return (
            None,
            None,
            f"Error: {e}"
            )
    
def parse_uploaded_fasta(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')

    sequence_lines = []
    for line in decoded.splitlines():
        if line.strip() and not line.startswith(">"):
            sequence_lines.append(line.strip())


    return "".join(sequence_lines).upper()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)