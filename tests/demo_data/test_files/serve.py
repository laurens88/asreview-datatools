import argparse
import warnings
from pathlib import Path
import sys

import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype
from asreview import ASReviewData, config
from asreview.data.base import load_data


def serve(file, annotators):
    if not annotators:
        print("No annotators were given.")
        return

    dataframe = pd.read_csv(file)

    label_columns = [col for col in dataframe.columns if 'final_label_' in col]

    if label_columns:

        annotation_df = pd.DataFrame(columns=dataframe.columns)

        for row in range(len(dataframe)):
            #check if none of the columns that contain "final_label_" have a label 0 or 1
            if not row_has_label(dataframe.iloc[row], label_columns):
                unlabeled_row = dataframe.iloc[row]
                annotation_df.loc[len(annotation_df)] = unlabeled_row
    
        print(annotation_df)
        print(f'Found {len(annotation_df)} records without label.')
    
    else:
        annotation_df = dataframe

    #drop all columns except title, abstract, doi, and MID
    important_columns = config.COLUMN_DEFINITIONS['title'] + config.COLUMN_DEFINITIONS['abstract'] \
    + config.COLUMN_DEFINITIONS['doi'] + ['MID'] \
    + [col for col in annotation_df.columns if 'year' in col]
    annotation_df =  annotation_df[annotation_df.columns.intersection(important_columns)]

    output_annotation_df(annotation_df, annotators)

    

def row_has_label(row, label_columns):
    # for col in label_columns:
    #     if row[col] in [0, 1]:
    #         return True
    # return False
    return any(row[col] in [0, 1] for col in label_columns)

def output_annotation_df(annotation_df, annotators):
    #add annotator columns to annotation dataframe
    for annotator in annotators:
        #create copy of dataframe for each annotator
        df = annotation_df.copy()

        #add title abstract annotation columns
        df[f'TI-AB_IC1_{annotator}'] = np.nan
        df[f'TI-AB_IC2_{annotator}'] = np.nan
        df[f'TI-AB_IC3_{annotator}'] = np.nan
        df[f'TI-AB_IC4_{annotator}'] = np.nan
        df[f'TI-AB_other_exlusion_reason_{annotator}'] = np.nan
        df[f'TI-AB_final_label_{annotator}'] = np.nan

        #add full text annotation columns
        df[f'FT_IC1_{annotator}'] = np.nan
        df[f'FT_IC2_{annotator}'] = np.nan
        df[f'FT_IC3_{annotator}'] = np.nan
        df[f'FT_IC4_{annotator}'] = np.nan
        df[f'FT_other_exlusion_reason_{annotator}'] = np.nan
        df[f'FT_final_label_{annotator}'] = np.nan

        #output new annotation dataframe
        df.to_csv(annotator+".csv")

def main():
    file = sys.argv[1]
    annotators = sys.argv[2:]
    serve(file, annotators)

if __name__ == "__main__":
    main()
