import streamlit as st
import pandas as pd
import numpy as np
import random

# Load the CSV file into a pandas DataFrame
@st.cache
def load_data(file):
    df = pd.read_csv(file)
    return df

# Function to generate peptide features
def generate_peptide(sequence):
    # Mock implementation: Generate random peptide features
    residue_count = len(sequence)
    peptide_length = random.randint(5, residue_count)  # Random peptide length
    molecular_weight = round(random.uniform(500, 2000), 2)  # Random molecular weight
    isoelectric_point = round(random.uniform(5, 10), 2)  # Random isoelectric point
    return peptide_length, molecular_weight, isoelectric_point

file = st.sidebar.file_uploader('Upload CSV file', type=['csv'])
if file is not None:
    df = load_data(file)

    # Select two random sequences
    random_indices = random.sample(range(len(df)), 2)
    random_sequences = df.loc[random_indices]

    # Display the selected sequences
    st.write(" Selected Sequences:")
    st.write(random_sequences)

    # Perform de novo peptide generation
    st.write("Generated Peptide Features:")
    for i, row in random_sequences.iterrows():
        sequence = row['sequence']
        peptide_length, molecular_weight, isoelectric_point = generate_peptide(sequence)
        st.write(f"Sequence {i+1}:")
        st.write(f"- Peptide Length: {peptide_length}")
        st.write(f"- Molecular Weight: {molecular_weight}")
        st.write(f"- Isoelectric Point: {isoelectric_point}")
