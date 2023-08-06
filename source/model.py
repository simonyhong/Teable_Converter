import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

to_generate_embeddings =False

class Table_information:
    def __init__(self, df, sentence_bert):
        self.sentence_bert = sentence_bert
        self.df = df
        self.joined_value_string,  self.mean_length_list, self.std_dev_length_list = self.convert_and_join()
        self.len_of_value = [len(value_string) for value_string in self.joined_value_string]
        self.embed_name_list     = [self.embed_sentences([column_mame]) for column_mame in self.df.columns]
        self.embed_sentences_list= [self.embed_sentences([joined_str]) for joined_str in self.joined_value_string]
        self.data_type_list      = [self.data_type(df[col]) for col in self.df.columns]

    def convert_and_join(self):
        mean_length = {}
        std_dev_length = {}
        
        for column_name in self.df.columns:
            if self.df[column_name].dtype == 'object' and self.is_date(self.df[column_name]):
                self.df[column_name] = pd.to_datetime(self.df[column_name]).dt.strftime('%Y-%m-%d')
            else:
                self.df[column_name] = self.df[column_name].astype(str)
                
            # Compute mean and standard deviation of string lengths for each column
            lengths = self.df[column_name].str.len()
            mean_length[column_name] = lengths.mean()
            std_dev_length[column_name] = lengths.std()
                
        joined_value_string = self.df.apply(lambda col: ', '.join(col.values.astype(str)), axis=0)
        
        return joined_value_string, mean_length, std_dev_length


    def data_type(df, column):
        if pd.to_datetime(column, errors='coerce').notna().all():
            return "datetime"
        elif pd.to_numeric(column, errors='coerce').notna().all(): 
            return "numeric"
        elif np.all(column.map(lambda x: isinstance(x, bool))):
            return "boolean"
        else: 
            if pd.to_numeric(column, errors='coerce').notna().any():
                return "alpha_numeric"
            else: 
                return "string"

    def is_date(self, column):
        try:
            pd.to_datetime(column)
            return True
        except ValueError:
            return False

    def embed_sentences(self, sentence_list): # The sentence needs to be in list or array form
        if len(sentence_list)>0:
          result = self.sentence_bert.encode(sentence_list)
          return (result.T / (result**2).sum(axis=1) ** 0.5).T   # Normalizing embeddings, so that euclidian distance is equivalent to cosine distance
        else: return np.asarray([])


def cosine_similarity(a, b):
    return 1 - cosine(a, b)

def map_columns(table1_info, table2_info):
    candidate_df_dic = {}
    ranked_candidates = []

    for col1, embed1, name1, data_type1 in zip(table1_info.df.columns, table1_info.embed_sentences_list, table1_info.embed_name_list, table1_info.data_type_list):
        candidates = []
        for col2, embed2, name2, data_type2 in zip(table2_info.df.columns, table2_info.embed_sentences_list, table2_info.embed_name_list, table2_info.data_type_list):
            similarity_score = 0.5*cosine_similarity(embed1[0], embed2[0])
            # Compute similarity score for mean length and standard deviation
            mean_length_diff = abs(table1_info.mean_length_list[col1] - table2_info.mean_length_list[col2])
            std_dev_diff = abs(table1_info.std_dev_length_list[col1] - table2_info.std_dev_length_list[col2])
            mean_length_similarity =0.25*( 1 / (1 + mean_length_diff))
            std_dev_similarity    = 0.25*(1 / (1 + std_dev_diff))

            column_name_similarity  = cosine_similarity(name1[0], name2[0])
            type_score = int(data_type1 == data_type2)

            # Storing scores in a dictionary
            scores = {
                'Column Similarity': similarity_score, 
                'Mean Length Similarity': mean_length_similarity,
                'Std Dev Length Similarity': std_dev_similarity,
                'Column Name Similarity': column_name_similarity,
                'Type Similarity': type_score, 
                'Total Score': similarity_score+ mean_length_similarity + std_dev_similarity + column_name_similarity  + type_score
            }
            
            candidates.append((col2, scores))
        
        # Sort the candidates by 'Total Score' in descending order
        candidates.sort(key=lambda x: x[1]['Total Score'], reverse=True)

        # Create a DataFrame for each column in table1_info (template_info)
        candidate_df = pd.DataFrame([scores for _, scores in candidates], index=[col for col, _ in candidates])
        candidate_df_dic[col1] = candidate_df

        # Append the list of sorted candidate column names
        ranked_candidates.append([col for col, _ in candidates])
    
    # Create a DataFrame of template columns and their corresponding candidate columns in ranked order
    ranked_candidates_df = pd.DataFrame(ranked_candidates, index=table1_info.df.columns)

    return candidate_df_dic, ranked_candidates_df


def adjust_format(template_col, data_col):
    # Define the symbols to check
    symbols = ["-", ":"]

    # Check each symbol
    for symbol in symbols:
        # If symbol is in template but not in data, add it to data
        if template_col.str.contains(symbol).any() and not data_col.str.contains(symbol).any():
            # Extracting the position of symbol from the template data
            symbol_position = template_col.apply(lambda x: x.find(symbol))

            # Adding symbol in the data based on the template
            for i in range(len(data_col)):
                position = symbol_position[i]
                data_col[i] = data_col[i][:position] + symbol + data_col[i][position:]

        # If symbol is not in template but in data, remove it from data
        elif not template_col.str.contains(symbol).any() and data_col.str.contains(symbol).any():
            data_col = data_col.str.replace(symbol, '')

    return data_col

def adjust_datetime_format(template_col, data_col):
    # Convert template and data columns to datetime
    template_col = pd.to_datetime(template_col)
    data_col = pd.to_datetime(data_col)

    # Get the datetime format from the first non-NaT value in template_col
    datetime_format = template_col.dropna().iloc[0].strftime('%Y-%m-%d')

    # Format data_col according to the format obtained from template_col
    data_col = data_col.dt.strftime(datetime_format)

    return data_col

def adjust_numeric_format(template_col, data_col):
    template_col = pd.to_numeric(template_col, errors='coerce')
    data_col = pd.to_numeric(data_col, errors='coerce')

    # If template column is of integer type, convert data column to integer
    if np.issubdtype(template_col.dtype, np.integer):
        print("Integer")
        data_col = data_col.astype(int)

    # If template column is of float type, match the number of decimal places in data column with that of template column
    elif np.issubdtype(template_col.dtype, np.floating):
        print("Float")
        # Count the number of decimal places in the first non-null value of the template column
        decimal_places = len(str(template_col.dropna().iloc[0]).split('.')[1])
        data_col = data_col.round(decimal_places)
    else: 
        print("Other numeric")
        
    return data_col