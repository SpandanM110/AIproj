import streamlit as st
import pandas as pd
import py3Dmol
import requests
import biotite.structure.io as bsio
from stmol import showmol
import os
from gradientai import Gradient

# Set page config and sidebar title
st.set_page_config(layout='wide')
st.sidebar.title('Proteoders')
st.sidebar.write('De novo peptide sequencing')

# Function to render protein structure
def render_mol(pdb):
    pdbview = py3Dmol.view()
    pdbview.addModel(pdb,'pdb')
    pdbview.setStyle({'cartoon':{'color':'spectrum'}})
    pdbview.setBackgroundColor('white')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    pdbview.spin(True)
    showmol(pdbview, height=500, width=800)

# Function to predict and display protein structure
def predict_protein_structure(sequence, index):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # Assume the API endpoint for protein structure prediction
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence, verify=False)
    pdb_string = response.content.decode('utf-8')

    with open(f'predicted_{index}.pdb', 'w') as f:
        f.write(pdb_string)

    struct = bsio.load_structure(f'predicted_{index}.pdb', extra_fields=["b_factor"])
    b_value = round(struct.b_factor.mean(), 4)

    # Display protein structure
    st.subheader(f'Visualization of predicted protein structure {index}')
    render_mol(pdb_string)

    # plDDT value is stored in the B-factor field
    st.subheader(f'plDDT {index}')
    st.write('plDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
    st.info(f'plDDT: {b_value}')

    st.download_button(
        label=f"Download PDB {index}",
        data=pdb_string,
        file_name=f'predicted_{index}.pdb',
        mime='text/plain',
        key=f"download_button_{index}"
    )

# Function to process CSV file
def process_csv(file):
    if file is not None:
        df = pd.read_csv(file)
        if 'sequence' in df.columns:
            sequences = df['sequence'].tolist()
            for i, seq in enumerate(sequences):
                st.subheader(f'Protein Sequence: {seq[:10]}...')
                predict_protein_structure(seq, i)
        else:
            st.error("CSV file does not contain a column named 'Sequence'. Please check the file structure.")

# Function to display drug visualization
def visualize_drug(drug_name):
    # Use the Gradient AI model to generate drug visualization
    base_model = gradient.get_base_model(base_model_slug="nous-hermes2")
    new_model_adapter = base_model.create_model_adapter(name=" Prot")
    response = gradient.query_model("nous-hermes2", query=drug_name)
    drug_visualization = response.generated_output
    st.subheader(f'Drug Visualization: {drug_name}')
    st.write(drug_visualization)

# Sidebar file uploader
file = st.sidebar.file_uploader('Upload CSV file', type=['csv'])

# Protein sequence input
DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)

# Dropdown for additional functionalities
selected_option = st.sidebar.selectbox("Select an option", ["Protein Sequencing", "Protein Visualization", "Drug Visualization"])

# Process CSV file if uploaded
process_csv(file)
os.environ['GRADIENT_WORKSPACE_ID'] = 'c0bb3a21-b667-4546-a16b-e45f05973fda_workspace'
os.environ['GRADIENT_ACCESS_TOKEN'] = '5xE38Xgw8BG45z4lv9ebjC5mQ2WrC9jm'
# Initialize Gradient AI
gradient = Gradient()

# If selected option is Protein Sequencing
if selected_option == "Protein Sequencing":
    if st.sidebar.button('Predict'):
        predict_protein_structure(txt, 0)

# If selected option is Protein Visualization
elif selected_option == "Protein Visualization":
    st.sidebar.write("Option for protein visualization selected.")
    # Placeholder for protein visualization function

# If selected option is Drug Visualization
elif selected_option == "Drug Visualization":
    st.sidebar.write("Option for drug visualization selected.")
    drug_name = st.sidebar.text_input('Enter Drug Name')
    if st.sidebar.button('Visualize'):
        visualize_drug(drug_name)

# If no input is provided
if not selected_option and not file:
    st.warning('👈 Enter protein sequence data, upload a CSV file, or select an option for visualization!')

# Close Gradient AI
gradient.close()
