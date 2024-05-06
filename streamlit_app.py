import streamlit as st
import pandas as pd
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

# Set page config and sidebar title
st.set_page_config(layout='wide')
st.sidebar.title('🎈 ESMFold')
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
def update(sequence, index):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    # Disable SSL verification
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
                update(seq, i)
        else:
            st.error("CSV file does not contain a column named 'Sequence'. Please check the file structure.")

# Sidebar file uploader
file = st.sidebar.file_uploader('Upload CSV file', type=['csv'])

# Protein sequence input
DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)

# Predict button
predict = st.sidebar.button('Predict')

# Process CSV file if uploaded
process_csv(file)

# If predict button is clicked
if predict:
    update(txt, 0)

# If no input is provided
if not predict and file is None:
    st.warning('👈 Enter protein sequence data or upload a CSV file!')
