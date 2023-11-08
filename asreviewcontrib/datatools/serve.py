import argparse
import warnings
from pathlib import Path
import sys

import pandas as pd
from pandas.api.types import is_string_dtype
from asreview import ASReviewData, config
from asreview.data.base import load_data


def serve(file, *annotators):
    dataframe = pd.read_csv(file)
    important_columns = config.COLUMN_DEFINITIONS['title'] + config.COLUMN_DEFINITIONS['abstract'] + config.COLUMN_DEFINITIONS['doi']
    dataframe =  dataframe[dataframe.columns.intersection(important_columns)]
    #check all columns that contain "include" per row
    #if all of the columns for that row are empty:
        #store row in new dataframe
    #add annotator columns to new dataframe
    #return new dataframe


def main():
    serve(sys.argv[1:])

if __name__ == "__main__":
    main()
