
## Directory Sturcture
    # Note: The BERT folder (paraphrase-distilroberta-base-v2) is not included in GitHub reposititory.
    # This is because of its big size. 
    # Please get the BERT zip file from here: 
        https://drive.google.com/file/d/1jok2pXgogmQFP1QWus74awjM41EPwCvg/view?usp=drive_link
    # And extract and put it in the directory as below.

    Table_Converter/
    ├── paraphrase-distilroberta-base-v2   # Put the extracted BERT model here, with the name as here.
    ├── myenv/                             # Make your own virtual environment
    ├── source/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── app.py                         # Flask application entry point
    │   ├── model.py                       # Script used by the application
    │   ├── templates/                     # Directory for Jinja2 templates
    │   │   ├── home.html
    │   │   ├── table.html
    │   │   └── new_table_df.html
    │   └── uploads/                       # Directory for uploaded csv files
    ├── test_files/                        # Contains the test files (template.csv, table_A.csv, table_B.csv) 
    ├── .gitignore
    ├── README.md
    ├── requirements.txt
    └── setup.py



## Installation & Usage
(0) Get BERT model as described above
(1) activate the the virtual environment
(2) Install it:
        pip install -e .
(3) Run the program: 
        python -m source
* For your convenience, the test files (template.csv, table_A.csv, table_B.csv) are in test_files folder.


## Summary of operations

1. The user interface initially provides two drop-boxes for users to upload two CSV files - a template and a target table to be reformatted according to the template. Upon clicking the "Upload" button, the 'upload_files()' function within 'app.py' is called to download and process the CSV files, generating a pandas DataFrame named 'column_mapping_df'.

2. 'column_mapping_df' is converted to HTML format and rendered via the "table.html" file. This table on the webpage shows a mapping between the template and the target table. The user selects the corresponding columns from the table, with default selection set to the first column. Once selections are made, the user clicks the "Accept" button.

3. The "Accept" button triggers the 'submit()' function in 'app.py', sending the user's selection as a list to the Flask server. This function generates the final DataFrame, "new_table_df", which contains the reformatted table matching the template format.

4. The final DataFrame "new_table_df" is rendered on the webpage via "new_table_df.html". A "Download" button is provided for the user to download the reformatted table. On clicking "Download", the "new_table_df" file is saved in the user's Download folder as a CSV file.