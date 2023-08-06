
## Directory Sturcture
    # Note: The BERT folder (paraphrase-distilroberta-base-v2) is not included in GitHub reposititory, because of its big size. 
    # Please get the BERT zip file from here: https://drive.google.com/file/d/1jok2pXgogmQFP1QWus74awjM41EPwCvg/view?usp=drive_link
    # And extract and put it in the directory as below.

    Zero_assignment/
    ├── paraphrase-distilroberta-base-v2   # Put the extracted BERT model here, with the name as here.
    ├── myenv/              # Make your own virtual environment
    ├── source/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── app.py          # Flask application entry point
    │   ├── model.py        # Script used by the application
    │   ├── templates/      # Directory for Jinja2 templates
    │   │   ├── home.html
    │   │   ├── table.html
    │   │   └── new_table_df.html
    │   ├── uploads/        # Directory for uploaded csv files
    │
    ├── .gitignore
    ├── LICENSE
    ├── README.md
    ├── requirements.txt
    └── setup.py



## Installation & Usage
In the case of VS-Code:
(1) activate the the virtual environment
(2) Install it:
        pip install -e .
(3) Run the program: 
        python -m source
* For your convenience, the test files (template.csv, table_A.csv, table_B.csv) are in test_files folder.


## Summary of the operations
(1) Initially there are two boxes that the user uses to drop one csv table file each. 
home.html has this forms.
When the user drops two csv files (one template, the other a table to be converted in the format of the template) and clicks "Upload" button, the home.html script calls the Flask server(app.py)'s following function:
@app.route('/upload', methods=['POST'])
def upload_files()
to download the csv files locally and process them.
This process generates a pandas Dataframe called column_mapping_df.

(2) The column_mapping_df gets converted to html format, and gets renderd via "table.html" file, which displays a table in the web page.
This has a mapping between the template and the table to be converted. 
Then the user selects by clicking table's columns that should match to the ones in template, which will highlight the selected ones. The default selction is the first column (containing the most likely columns from the table) for each index (which contains the template's colimns).
When the selection is done by the user, the user clicks "Accept" button.

(3) When the Accept button is pressed, table.html transmitts the selection as a list to the Flask server by calling 
@app.route('/submit', methods=['POST'])
def submit():
described in app.py.
The submit() function generates the final DataFrame called "new_table_df" as a global variable, which has a new table in the format of template.

The last step above triggers the following stage (4).
(4) The "new_table_df" is transmitted and randered via a file "new_table_df.html" in the web page.
And there is a "Download" button to download the new_table_df table.
The user clicks the "Download"  button and the new_table_df file downloads to the user's Download folder as a csv file