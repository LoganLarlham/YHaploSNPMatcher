#this script will take the filtered files 01_Raw_data/AADR_plink/AncMalesRelv_flat.map and 01_Raw_data/AADR_plink/AncMalesRelv_flat.ped
#and create a dataframe, then compare the snps at each poisition to the snps in the filtered user file.
#it will the output a list of IDs from the map file in descending order of the number of snps that match the user file.
#it will also output the total number of snps that were compared.


import pandas as pd
import numpy as np



def getAADRAnnotations():
    #load in .xlsx file with AADR metadata
    #read in the AADR metadata file
    AADR_metadata = pd.read_excel('01_Raw_data/AADR_plink/AADR Annotation.xlsx')

    #write AADR_metadata to a tsv file
    AADR_metadata.to_csv('01_Raw_data/AADR_plink/AADR_metadata.tsv', sep='\t', index=False)

    #remove useless columns from the AADR_metadata
    columns_to_keep = AADR_metadata.columns[[1, 10, 13]]
    columns_to_drop = AADR_metadata.columns.difference(columns_to_keep)
    AADR_metadata_subset = AADR_metadata.drop(columns=columns_to_drop)
    #rename the columns of the AADR_metadata_subset data frame
    AADR_metadata_subset.columns = ['GeneticID', 'FullDate', 'Locality']
    return AADR_metadata_subset


def getAADRData():
    #This section reads in the AADR map into a df with proper column names
    #read in the AADR map file
    AADR_map = pd.read_csv('01_Raw_data/AADR_plink/AncMalesRelvLtr.map', sep='\t', header=None)
    #remove column 3 from the AADR_map
    AADR_map = AADR_map.drop(columns=3)
    #add column names to the AADR_map
    AADR_map.columns = ['chromosome', 'rsid', 'position']


    #this section of code reads in the AADR ped file, splits it into two data frames, one with meta data and one with rsids, then transposes the rsid data frame
    #read in the AADR ped file
    AADR_ped = pd.read_csv('01_Raw_data/AADR_plink/AncMalesRelvLtr.ped', sep='\t', header=None)
    #add column names to the AADR_ped columns
    AADR_ped = AADR_ped.rename(columns={0: '#', 1: 'GeneticID', 2: 'FatherID', 3: 'MotherID', 4: 'Sex', 5: 'Phenotype'})
    # Create a dictionary mapping the current column names to the new names
    new_column_names = {i: name for i, name in enumerate(AADR_map['rsid'].values, start=6)}
    # Use the rename function to change the column names
    AADR_ped = AADR_ped.rename(columns=new_column_names)
    #delete duplicated data from the AADR_ped
    AADR_ped = AADR_ped.map(lambda x: x.split()[0] if isinstance(x, str) else x)


    #split AADR_ped into two data frames, one with rsIDs and one with meta data (columns 1-6)
    AADR_ped_meta = AADR_ped.iloc[:, :6]
    AADR_ped_rsids = AADR_ped.iloc[:, 6:]
    #transpose the AADR_ped_rsids data frame for easier comparison
    AADR_ped_rsids = AADR_ped_rsids.T.reset_index()
    #rename the columns of the AADR_ped_rsids data frame
    AADR_ped_rsids.columns = ['rsid'] + [f'individual_{i}' for i in range(len(AADR_ped_rsids.columns) - 1)]
    return AADR_ped_rsids, AADR_ped_meta

#run the functions so they are available to the user without having to be called each time the submit button is pressed
AADR_metadata_subset = getAADRAnnotations()
AADR_data = getAADRData()

def getNonMatches(userfile_selection, merged_df):
     #Create non_matches DataFrame
    non_matches = merged_df.copy()
    individual_cols = non_matches.columns[4:]

    # Create a boolean DataFrame where True indicates a mismatch
    mismatches = non_matches[individual_cols].ne(non_matches['allele2'], axis=0)

    # Use np.where to vectorize the conditional operation
    for col in individual_cols:
        non_matches[col] = np.where(mismatches[col], non_matches[col] + non_matches['position'].astype(str) + non_matches['allele2'], np.nan)
        non_matches[col] = np.where(non_matches[col].astype(str).str.startswith('0'), np.nan, non_matches[col])
        #non_matches[col] = np.where(non_matches[col].astype(str).str.startswith('0'), non_matches[col].astype(str).str.replace('^0', '-', regex=True), non_matches[col])
    #get list of non-matching snps for each individual and add it as a column to AADR_ped_meta
    return non_matches

    #get the number of matches for each individual and add it as a column to AADR_ped_meta
    #the digits following the underscore in the first columnb of matches is the index of the individual in AADR_ped_meta 


def getMatches(userfile_selection, AADR_ped_rsids, AADR_ped_meta, results_num):

    #Read in the user file
    userfile = pd.read_csv(userfile_selection, sep='\t', skiprows=2, names=['rsid', 'chromosome', 'position', 'allele2'])

    #this section of code merges the userfile with the AADR_ped_rsids data frame on rsid, then creates a comparison data frame and counts the number of snps that match for each individual
    #merge the userfile with the AADR_ped_rsids data frame on rsid
    merged_df = pd.merge(userfile, AADR_ped_rsids, on='rsid', how='inner')
    #create comparison data frame
    comparison_df = merged_df.drop(columns=['rsid', 'chromosome','position'])
    comparison_df = comparison_df.astype(str)
    #count the number of snps that match for each individual
    allele2_values = comparison_df['allele2']
    matches = (comparison_df.iloc[:, 1:] == allele2_values.values[:, None]).sum()
    AADR_ped_meta['matches'] = [matches.iloc[i] for i in range(len(matches))]

    #add non matches to AADR_ped_meta by calling getNonMatches
    non_matches = getNonMatches(userfile_selection, merged_df)
    #for each individual get the values in non_matches as a list and add it to AADR_ped_meta as a new column
    #make a new column in AADR_ped_meta for the non matching values

    non_matches = non_matches.drop(columns=['rsid', 'chromosome', 'position', 'allele2'])

    if 'non_matching_mutations' not in AADR_ped_meta.columns:
        AADR_ped_meta['non_matching_mutations'] = np.nan
    AADR_ped_meta['non_matching_mutations'] = AADR_ped_meta['non_matching_mutations'].astype(object)


    for col in non_matches.columns:
        # Obtain the list of non-NaN values
        non_nan_values = non_matches[col].dropna().tolist()
        
        # The index in AADR_ped_meta that corresponds to the current individual's column in non_matches
        # Assuming the column name format is 'individual_x' and x is the index in AADR_ped_meta
        individual_index = int(col.split('_')[1])  # Extracts the numeric part from the column name
        
        # Update the corresponding row in AADR_ped_meta with the list of non-NaN values
        AADR_ped_meta.at[individual_index, 'non_matching_mutations'] = non_nan_values


    #remove rows from AADR_ped_meta where there are no matches
    AADR_ped_meta = AADR_ped_meta[AADR_ped_meta['matches'] > 0]

    # Assuming AADR_ped_meta['NonMatchValues'] contains lists
    AADR_ped_meta['non_matching_mutations'] = AADR_ped_meta['non_matching_mutations'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)


    #get the total number of allele comparisons
    total_allele_comparisons = len(merged_df)

    print(AADR_ped_meta)
    return AADR_ped_meta.sort_values(by='matches', ascending=False).head(results_num), total_allele_comparisons


  
def getMetaData(GeneticID, AADR_metadata_subset):
    #get the individual data from the AADR_metadata_subset data frame
    individual_data = AADR_metadata_subset[AADR_metadata_subset['GeneticID'] == GeneticID]
    return individual_data







