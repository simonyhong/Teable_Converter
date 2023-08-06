from flask import Flask, render_template, request, Response, send_file
import pandas as pd
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from . import model


app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('home.html')

# bert_path = '../paraphrase-distilroberta-base-v2'
bert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'paraphrase-distilroberta-base-v2')
sentence_bert  = SentenceTransformer(bert_path)


def process(template_path, table_path):
    global column_mapping_df, template_df, table_df, template_info, table_info
    template_df = pd.read_csv(template_path)
    table_df = pd.read_csv(table_path)

    template_info=model.Table_information(template_df, sentence_bert)
    table_info=model.Table_information(table_df, sentence_bert)
    candidate_df_dic, column_mapping_df =model.map_columns(template_info, table_info)
    for col1, candidate_df in candidate_df_dic.items():
        print(f'{col1}: \n')
        print(candidate_df)
        print('\n')    
    html = column_mapping_df.to_html(table_id='mytable')  # convert DataFrame to HTML string
    return html  # return HTML string as a result


@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        # check if the post request has the file parts
        if 'template' not in request.files or 'table' not in request.files:
            return 'No file parts'
        
        template_file = request.files['template']
        table_file = request.files['table']

        # If the user does not select a file, the browser might
        # submit an empty file without a filename.
        if template_file.filename == '' or table_file.filename == '':
            return 'No selected file'
        
        # save the files
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_file.filename)
        table_path = os.path.join(app.config['UPLOAD_FOLDER'], "table_to_convert.csv")
        template_file.save(template_path)
        table_file.save(table_path)
        
        # Call the process function with the paths of the saved files.
        result = process(template_path, table_path)  # result is the HTML string
        return render_template('table.html', table=result)


@app.route('/submit', methods=['POST'])    # new route
def submit():
    global new_table_df
    user_defined_colum_list = request.get_json()
    print("in submit")
    print(user_defined_colum_list)   # This should print the array from your fetch request

    selected_column_names=[]
    for idx, col in zip(column_mapping_df.index, user_defined_colum_list[1:]):
        selected_column_names.append(column_mapping_df.loc[idx, col-1])

    data = {}
    for i, (col_name, temp_type, table_type) in enumerate(zip(selected_column_names, template_info.data_type_list, table_info.data_type_list)):
        print(i, col_name)
        data_col = table_df[col_name].copy()
        template_col = template_df[template_df.columns[i]]

        # Adjust string formatting
        if temp_type == 'string' and table_type == 'string':
            print("string")
            data_col = model.adjust_format(template_col, data_col)
            
            # Adjust "Plan" column
            if "Plan" in template_df[template_df.columns[i]].iloc[0] and "Plan" not in data_col.iloc[0]:
                data_col = data_col + " Plan"
            elif "Plan" not in template_df[template_df.columns[i]].iloc[0] and "Plan" in data_col.iloc[0]:
                data_col = data_col.str.replace(" Plan", "")

        # Adjust datetime formatting
        elif temp_type == 'datetime' and table_type == 'datetime':
            print("datetime")
            data_col = model.adjust_datetime_format(template_col, data_col)
        
        # Adjust numeric formatting
        elif  temp_type == 'numeric' and table_type == 'numeric':
            print("numeric")
            data_col = model.adjust_numeric_format(template_col, data_col)
        
        # Store the adjusted column in the data dictionary
        data[template_df.columns[i]] = data_col

    new_table_df=pd.DataFrame(data)
    print("Here is the new table:\n")
    print(new_table_df)
    return 'Table successfully created.', 200

def get_downloads_folder():
    home = os.path.expanduser("~")
    return os.path.join(home, "Downloads")

@app.route('/show_new_table')
def show_new_table():
    global new_table_df
    html = new_table_df.to_html()
    return render_template('new_table_df.html', table=html)


@app.route('/download')
def download():
    global new_table_df
    csv_filename = 'new_table.csv'  # name of csv file
    csv_path = os.path.join(get_downloads_folder(), csv_filename)
    new_table_df.to_csv(csv_path, index=False)
    return send_file(csv_path, as_attachment=True)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
