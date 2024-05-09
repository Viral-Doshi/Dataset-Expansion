import pandas as pd
import streamlit as st
from sklearn.preprocessing import LabelEncoder
from mice import *
import seaborn as sns
import matplotlib.pyplot as plt
import anthropic
import json
import os
import opendatasets as od
from urllib import request

# def display_recommendations2(recommendations):
#     # Split recommendations by numeric index
#     recommendations_list = recommendations.strip().split("\n\n")
    
#     # Initialize lists to store dataset names, links, and join columns
#     datasets = []
#     links = []
#     join_columns = []
    
#     # Parse each recommendation
#     for rec in recommendations_list:
#         lines = rec.strip().split("\n")
#         dataset_info = ""
#         link = ""
#         join_column = ""
#         for line in lines:
#             line = line.strip()
            
#             if line.startswith("Link"):
#                 link = line.split(": ")[1].strip()
#             elif line.startswith("Join Column") or line.startswith("Join Columns"):
#                 join_column = line.split(": ")[1].strip()
#             else:
#                 dataset_info = line.split(": ")[1].strip()
#         datasets.append(dataset_info)
#         links.append(link)
#         join_columns.append(join_column)
    
#     # Create DataFrame from parsed data
#     df = pd.DataFrame({"Dataset": datasets, "Link": links, "Join Column(s)": join_columns})
    
#     # Display DataFrame as table
#     st.write("Dataset Recommendations:")
#     df['Link'] = df['Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
#     st.write(df.to_html(escape=False), unsafe_allow_html=True)

# Define a function to download a file from a URL
def download_file(url, filename):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file in binary write mode and write the content of the response
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    

def handle_download(df):
    try:
        row_number = int(st.session_state.row_number)
        if 1 <= row_number <= len(df):
            link = df.iloc[row_number - 1]['Link']
            print("[handle_download]: " + "Link : ", link)
            od.download(link)  # Download the file
            st.session_state['message'] = "Dataset downloaded successfully!"
            st.session_state['message_type'] = "success"
        else:
            st.session_state['message'] = "Invalid row number. Please enter a valid row number."
            st.session_state['message_type'] = "error"
    except ValueError:
        st.session_state['message'] = "Please enter a valid row number."
        st.session_state['message_type'] = "error"

def display_recommendations(recommendations):
    # Split recommendations by numeric index
    recommendations_list = recommendations.strip().split("\n\n")
    
    # Initialize lists to store dataset names, links, and join columns
    datasets = []
    links = []
    join_columns = []
    
    # Parse each recommendation
    for rec in recommendations_list:
        lines = rec.strip().split("\n")
        dataset_info = ""
        link = ""
        join_column = ""
        for line in lines:
            line = line.strip()
            print("PPP",line)
            if "link" in line.lower():
                link = line.split("Link:")[1].strip()
            elif "join column" in line.lower() or "join columns" in line.lower():
                join_column = line.split(":")[1].strip()
            # else:
            #     dataset_info = line.split(": ")[1].strip()
        # datasets.append(dataset_info)
        links.append(link)
        join_columns.append(join_column)
    
    # Create DataFrame from parsed data
    df = pd.DataFrame({"Link": links, "Join Column(s)": join_columns})
    link_df = pd.DataFrame({"Link": links})
    
    # Display DataFrame as table
    st.write("Dataset Recommendations:")
    
    df['Link'] = df['Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
    st.write(df.to_html(escape=False), unsafe_allow_html=True)
    
    # Add option for user to download dataset
    st.write("Enter the row number of the dataset you want to download:")
    row_number = st.text_input("Enter row number", key='row_number')
    if st.button("Download", key='download_button'):
        # df = pd.DataFrame({
        #     "Link": ["https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"] * 10
        # })
        handle_download(link_df)

    if 'message' in st.session_state and st.session_state['message']:
        if st.session_state['message_type'] == "success":
            st.success(st.session_state['message'])
        elif st.session_state['message_type'] == "error":
            st.error(st.session_state['message'])



def get_dataset_recommendations(file_name, column_names):
    if 'recommendations' not in st.session_state:
        main_name = file_name.split('.')[0]  # Extract main dataset name
        # Define the prompt
        prompt = f"""
        I have a dataset named '{main_name}' containing information about {', '.join(column_names)}. 
        I want to increase the size of this dataset by joining similar datasets. 
        Could you please help me find similar datasets to join? 
        For each dataset recommendation, provide a link to download the dataset 
        and suggest a corresponding column to join with the '{main_name}' dataset.

        Here's some information about the '{main_name}' dataset:
        - Main dataset name: '{main_name}'
        - Description: Contains information about {', '.join(column_names)}.

        Find datasets that contain similar types of information 
        and suggest a column from each dataset that could be used to join with the '{main_name}' dataset. 
        Ensure that the suggested datasets are publicly available for download 
        and are in a compatible format (e.g., CSV).
        Also make sure to find only relevant datasets on which after joining it makes sense.
        Return only links and corresponding join columns from Kaggle. 
        The format should be 
        1. Link: www.example.com 
        Join Column: A

        2. Link: www.example.com
        Join Column: B

        and so on. 
        Don't give any other details.
        Thank you!
        """
        # prompt="Liverpool"
        # Call Anthropics API
        client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key="",
        )
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user",
                "content": prompt}  # Pass the prompt as the content
            ]
        )

        
        response_text = ''.join([block.text for block in message.content])
        # Print the text response
        # print(response_text)
        st.session_state['recommendations'] = response_text   
    else:
        response_text = st.session_state['recommendations']

    return response_text




def load_home():
    load_file()


def preprocess(data_file, file_name):

    def highlight_index(index):
        if index.name in ["Datatype", "Nulls"]:
            return ['background-color: #202638'] * len(data_file.columns)
        else:
            return [''] * len(data_file.columns)

    styled_df = data_file.style.apply(highlight_index, axis=1)
    styled_df = styled_df.highlight_null(color='#5e3030') 

    st.write("")  # Add spacing after the section
    st.write("Uploaded Data:")
    st.write(styled_df)

    column_names= data_file.columns.tolist()

    if 'row_number' not in st.session_state:
        st.session_state['row_number'] = "0"
    if 'message' not in st.session_state:
        st.session_state['message'] = ""
    if 'message_type' not in st.session_state:
        st.session_state['message_type'] = "info"

    if 'recommendations' not in st.session_state:
        recommendations = get_dataset_recommendations(file_name, column_names)
    else:
        recommendations = st.session_state['recommendations']

    # recommendations = get_dataset_recommendations(file_name, column_names)

    display_recommendations(recommendations)
    # display_recommendations_with_checkboxes(recommendations)


def restructure_dataframe(data):
    local_df = pd.DataFrame(data)
    cols = []
    datatype = []
    nulls = []
    for i in range(len(local_df.columns)):
        cols.append(local_df.columns[i])
        datatype.append(str(local_df.dtypes.loc[local_df.columns[i]]))
        nulls.append(str(int(local_df.isnull().sum()[local_df.columns[i]])))

    # Create DataFrame
    info_df = pd.DataFrame([datatype, nulls], columns=cols, index=['Datatype', 'Nulls'])

    # print(info_df)
    combined_df = pd.concat([info_df, local_df], axis=0)

    return combined_df


def load_file():
    if "file" not in st.session_state:
        file = st.file_uploader("Upload File Here", type={"csv", "tsv", "xlsx"})
        st.write("")
        if file is not None:
            
            file_name = file.name

            if str(file.name).endswith(".csv"):
                st.session_state.file = pd.read_csv(file)
                data_file = restructure_dataframe(st.session_state.file)

            elif str(file.name).endswith(".tsv"):
                st.session_state.file =pd.read_csv(file, sep = "\t")
                data_file = restructure_dataframe(st.session_state.file)

            elif str(file.name).endswith(".xlsx"):
                st.session_state.file = pd.read_excel(file)
                data_file = restructure_dataframe(st.session_state.file)

            if not st.session_state.file.empty:
                preprocess(data_file,file_name)
            else:
                st.write("File format not accepted or File is empty")
    else:
        data_file = restructure_dataframe(st.session_state.file)
        preprocess(data_file,"as")
