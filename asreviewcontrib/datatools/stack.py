import argparse
import warnings
from pathlib import Path

import pandas as pd
from pandas.api.types import is_string_dtype
from asreview import ASReviewData
from asreview.data.base import load_data


def _check_suffix(input_files, output_file):
    # Also raises ValueError on URLs that do not end with a file extension
    suffixes = [Path(item).suffix for item in input_files if item is not None]
    suffixes.append(Path(output_file).suffix)

    set_ris = {".txt", ".ris"}
    set_tabular = {".csv", ".tab", ".tsv", ".xlsx"}
    set_suffixes = set(suffixes)

    if len(set(suffixes)) > 1:
        if not (set_suffixes.issubset(set_ris) or set_suffixes.issubset(set_tabular)):
            raise ValueError(
                "• Several file types were given; All input files, as well as the output file should be of the same "
                "type. "
            )


def vstack(output_file, input_files):
    _check_suffix(input_files, output_file)
    list_dfs = [load_data(item).df for item in input_files]
    for df_i in range(len(list_dfs)):
        df = list_dfs[df_i]
        list_dfs[df_i] = df.assign(name_of_database=["'"+input_files[df_i]+"'"]*len(df.index))

    df_vstacked = pd.concat(list_dfs).reset_index(drop=True)
    as_vstacked = ASReviewData(df=df_vstacked)
    as_vstacked = ASReviewData(df=drop_duplicates(as_vstacked))
    as_vstacked.to_file(output_file)

def duplicated(asrdata, pid='doi'):
        """Return boolean Series denoting duplicate rows.
        Identify duplicates based on titles and abstracts and if available,
        on a persistent identifier (PID) such as the Digital Object Identifier
        (`DOI <https://www.doi.org/>`_).
        Arguments
        ---------
        pid: string
            Which persistent identifier to use for deduplication.
            Default is 'doi'.
        Returns
        -------
        pandas.Series
            Boolean series for each duplicated rows.
        """
        
        if pid in asrdata.df.columns:
            # in case of strings, strip whitespaces and replace empty strings with None
            if is_string_dtype(asrdata.df[pid]):
                s_pid = asrdata.df[pid].str.strip().replace("", None)
            else:
                s_pid = asrdata.df[pid]

            # save boolean series for duplicates based on persistent identifiers
            s_dups_pid = ((s_pid.duplicated()) & (s_pid.notnull()))
        else:
            s_dups_pid = None      

        # get the texts, clean them and replace empty strings with None
        s = pd.Series(asrdata.texts) \
            .str.replace("[^A-Za-z0-9]", "", regex=True) \
            .str.lower().str.strip().replace("", None)

        # save boolean series for duplicates based on titles/abstracts
        s_dups_text = ((s.duplicated()) & (s.notnull()))

        # final boolean series for all duplicates
        if s_dups_pid is not None:
            s_dups = s_dups_pid | s_dups_text
        else:
            s_dups = s_dups_text
        return s_dups

def drop_duplicates(asrdata, pid='doi', inplace=False, reset_index=True):
    """Drop duplicate records.
    Drop duplicates based on titles and abstracts and if available,
    on a persistent identifier (PID) such the Digital Object Identifier
    (`DOI <https://www.doi.org/>`_).
    Arguments
    ---------
    pid: string, default 'doi'
        Which persistent identifier to use for deduplication.
    inplace: boolean, default False
        Whether to modify the DataFrame rather than creating a new one.
    reset_index: boolean, default True
        If True, the existing index column is reset to the default integer index.
    Returns
    -------
    pandas.DataFrame or None
        DataFrame with duplicates removed or None if inplace=True
    """
    df = asrdata.df[~duplicated(asrdata, pid)]
    dupes = asrdata.df[duplicated(asrdata, pid)]

    for row in range(len(df.index)):
        for dupe in range(len(dupes.index)):
            if dupe==0:
                    df.iloc[row, df.columns.get_loc("name_of_database")] = "[" + str(df.iloc[row, df.columns.get_loc("name_of_database")])

            doi = df.iloc[row, df.columns.get_loc("doi")]
            title = df.iloc[row, df.columns.get_loc("title")]

            #check if duplicate matches with doi if it is not empty, else do the same check with title
            if doi and doi == dupes.iloc[dupe, dupes.columns.get_loc("doi")]:
                df.iloc[row, df.columns.get_loc("name_of_database")] = str(df.iloc[row, df.columns.get_loc("name_of_database")]) +","+ dupes.iloc[dupe, dupes.columns.get_loc("name_of_database")]
            elif title and title == dupes.iloc[dupe, dupes.columns.get_loc("title")]:
                df.iloc[row, df.columns.get_loc("name_of_database")] = str(df.iloc[row, df.columns.get_loc("name_of_database")]) +","+ dupes.iloc[dupe, dupes.columns.get_loc("name_of_database")]
            if dupe==len(dupes.index)-1:
                df.iloc[row, df.columns.get_loc("name_of_database")] = str(df.iloc[row, df.columns.get_loc("name_of_database")]) + "]"

    if reset_index:
        df = df.reset_index(drop=True)
    if inplace:
        asrdata.df = df
        return
    return df


def _parse_arguments_vstack():
    parser = argparse.ArgumentParser(prog="asreview data vstack")
    parser.add_argument("output_path", type=str, help="The output file path.")
    parser.add_argument(
        "datasets", type=str, nargs="+", help="Any number of datasets to stack vertically."
    )

    return parser
