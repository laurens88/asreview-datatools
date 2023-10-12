import sys
import pandas as pd
from asreview.data.base import load_data, ASReviewData

def insert(*files):
    files = files[0]
    output = files[0]
    
    file_dfs = [ASReviewData.from_file(file).df for file in files[1:]]
    
    
    target = file_dfs[1]
    # asd = ASReviewData.from_file(target)

    #check if column "name_of_database" is present in target, if not create empty "name_of_database" column
    if not "name_of_database" in target.columns:
        target["name_of_database"] = ""

    #check if target file is writable
    target.to_csv(output)
    matched_rows = []

    #loop through label source files
    for i in range(2, len(file_dfs)):
        #loop through source file rows
        for row in range(len(file_dfs[i])):

            #get label, doi and authors
            source_info = file_dfs[i].iloc[row, file_dfs[i].columns.get_loc("name_of_database")]
            doi = file_dfs[i].iloc[row, file_dfs[i].columns.get_loc("doi")]
            authors = file_dfs[i].iloc[row, file_dfs[i].columns.get_loc("authors")]
            title = file_dfs[i].iloc[row, file_dfs[i].columns.get_loc("title")]

            #loop through target file rows
            for target_row in range(len(target)):
                #if doi matches in target row, set label value
                if doi and target.loc[target_row, 'doi'] == doi:
                    if not target_row in matched_rows:
                        target.loc[target_row, 'name_of_database'] = str(source_info)
                        matched_rows.append(target_row)
                        # print("Matches found: ", len(matched_rows))
                #else if authors match in target row, set label value        
                elif authors and target.loc[target_row, 'authors'] == authors:
                    if not target_row in matched_rows:
                        target.loc[target_row, 'name_of_database'] = str(source_info)
                        matched_rows.append(target_row)
                        # print("Matches found: ", len(matched_rows))
                elif title and target.loc[target_row, 'title'] == title:
                    if not target_row in matched_rows:
                        target.loc[target_row, 'name_of_database'] = str(source_info)
                        matched_rows.append(target_row)
                        # print("Matches found: ", len(matched_rows))

    target.to_csv(output)

def main():
    insert(sys.argv[1:])

if __name__ == "__main__":
    main()