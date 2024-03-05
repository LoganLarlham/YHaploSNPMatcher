#this script will take the filtered files 01_Raw_data/AADR_plink/AncMalesRelv_flat.map and 01_Raw_data/AADR_plink/AncMalesRelv_flat.ped
#and create a dataframe, then compare the snps at each poisition to the snps in the filtered user file. b37_filtered_Test4_DNA.txt
#it will the output a list of IDs from the map file in descending order of the number of snps that match the user file.

import os
import sys
import pandas as pd

#load in .xlsx file with AADR metadata
#read in the AADR metadata file
AADR_metadata = pd.read_excel('01_Raw_data/AADR_plink/AADR Annotation.xlsx')

print(AADR_metadata.head())

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


#Read in the user file
userfile = pd.read_csv('b37_filtered_Test4_DNA.txt', sep='\t', skiprows=2, names=['rsid', 'chromosome', 'position', 'allele1', 'allele2'])


#this section of code merges the userfile with the AADR_ped_rsids data frame on rsid, then creates a comparison data frame and counts the number of snps that match for each individual
#merge the userfile with the AADR_ped_rsids data frame on rsid
merged_df = pd.merge(userfile, AADR_ped_rsids, on='rsid', how='inner')
#create comparison data frame
comparison_df = merged_df.drop(columns=['rsid', 'chromosome', 'position', 'allele1'])
comparison_df = comparison_df.astype(str)
#count the number of snps that match for each individual
allele2_values = comparison_df['allele2']
matches = (comparison_df.iloc[:, 1:] == allele2_values.values[:, None]).sum()



#sort the matches in descending order
matches = matches.sort_values(ascending=False)

print('matches\n', matches.head())






