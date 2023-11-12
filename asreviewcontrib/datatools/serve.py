import argparse
import warnings
from pathlib import Path
import sys

import pandas as pd
from pandas.api.types import is_string_dtype
from asreview import ASReviewData, config
from asreview.data.base import load_data


def serve(file, *annotators):
    print("test")
    print(f'File: {file}')
    print("hello")
    print(f'Annotators: {annotators}')

    dataframe = pd.read_csv(file)

    label_columns = [col for col in df.columns if df[col].astype(str).str.contains('include').any()]

    print(label_columns)

    annotation_df = pd.Dataframe(columns=dataframe.columns)

    for row in range(len(dataframe)):
        #check if none of the columns that contain "include" have a label 0 or 1
        if not dataframe[label_columns].isin([0, 1]):
            unlabeled_row = dataframe.iloc[row]
            annotation_df = annotation_df.append(unlabeled_row)
    
    print(annotation_df)

    #drop all columns except title, abstract, doi, MID, and any columns containing year
    important_columns = config.COLUMN_DEFINITIONS['title'] 
    + config.COLUMN_DEFINITIONS['abstract'] 
    + config.COLUMN_DEFINITIONS['doi'] 
    + ['MID', 'publication_year']
    + [c for c in annotation_df.columns if "year" in c]
    annotation_df =  annotation_df[annotation_df.columns.intersection(important_columns)]

    print(annotation_df)

    #add annotator columns to annotation dataframe
    for annotator in annotators:
        #create copy of dataframe for each annotator
        df = annotation_df.copy()

        #add title abstract annotation columns
        df[f'TI-AB_IC1_{annotator}'] = pd.np.nan
        df[f'TI-AB_IC2_{annotator}'] = pd.np.nan
        df[f'TI-AB_IC3_{annotator}'] = pd.np.nan
        df[f'TI-AB_IC4_{annotator}'] = pd.np.nan
        df[f'TI-AB_other_exlusion_reason_{annotator}'] = pd.np.nan
        df[f'TI-AB_final_label_{annotator}'] = pd.np.nan

        #add full text annotation columns
        df[f'FT_IC1_{annotator}'] = pd.np.nan
        df[f'FT_IC2_{annotator}'] = pd.np.nan
        df[f'FT_IC3_{annotator}'] = pd.np.nan
        df[f'FT_IC4_{annotator}'] = pd.np.nan
        df[f'FT_other_exlusion_reason_{annotator}'] = pd.np.nan
        df[f'FT_final_label_{annotator}'] = pd.np.nan

        #output new annotation dataframe
        df.to_csv(annotator+".csv")

    

def main():
    serve(sys.argv[1:])

if __name__ == "__main__":
    main()
