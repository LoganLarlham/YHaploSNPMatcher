#this script will have a function which takes test4.txt snp file and compares to the AncientYDNA/snpFile_b37_isogg2019.txt file 
#to cross-reference and filter out the snps that are not in the isogg2019 file. output subset file will include two header lines, first with user and haplogroup,
# second with column names. 
#should use pandas to read in the files and compare the snps.

#may want to add form for naming user.


import os
import sys
import pandas as pd

#need to add functionality to only get isogg snps which are associated with the userfile haplogroup


def UserCrossref(inputfile):
    #read in the isogg2019 file
    isogg2019 = pd.read_csv('01_Raw_data/AncientYDNA/snpFile_b37_isogg2019.txt', sep='\t')
    #add column names to isogg2019
    isogg2019.columns = ['rsid', 'position', 'ref', 'haplogroup', 'var', 'genotype']
    #inputfiel basename
    basename = os.path.basename(inputfile)
    #make a new file to write to in current directory with  inputfile basename
    outputfile = open('03_tmpfiles/Filtered_User/b37_filtered_' + basename, 'w')
    #write the user and haplogroup to the file
    outputfile.write('#User: ' + basename + '\n')
    #write the column names to the file
    outputfile.write('#rsid\tchromosome\tposition\tallele1\n')

    if inputfile.endswith('.txt'):
        #read in the user snp file
        userfile = pd.read_csv(inputfile, sep='\t')
        #remove all rows from userfile which are not chromosome 24(Y) or Y
        if len(userfile.columns) == 5:
            #rename userfile columns
            userfile.columns = ['rsid', 'chromosome', 'position', 'allele1', 'allele2']
        elif len(userfile.columns) == 4:
            userfile.columns = ['rsid', 'chromosome', 'position', 'allele1',]
        #only keep the first chatacter of the allele1 column (insted of genotype, only 1 allele)
    elif inputfile.endswith('.csv'):
        userfile = pd.read_csv(inputfile, sep=',')
        #rename userfile columns
        if len(userfile.columns) == 5:
            userfile.columns = ['rsid', 'chromosome', 'position', 'allele1', 'allele2']
        elif len(userfile.columns) == 4:
            userfile.columns = ['rsid', 'chromosome', 'position', 'allele1',]
    else:
        raise ValueError(f"Unsupported file format: {inputfile}; must be .txt or .csv in plink format")
        
    #remove all rows from userfile which are not chromosome 24(Y) or Y
    userfile = userfile[(userfile['chromosome'] == 24) | (userfile['chromosome'] == 'Y') | (userfile['chromosome'] == 'XY')]
    userfile['allele1'] = userfile['allele1'].str[0]

    #copy lines from userfile to outputfile if the rsid is in the isogg2019 file
    # Create a mask that is True for rows where 'rsid' is in isogg2019['rsid'].values
    mask = userfile['rsid'].isin(isogg2019['rsid'].values)

    # Select the rows where the mask is True
    selected_rows = userfile[mask]

    # Write the selected rows to the output file
    selected_rows.to_csv(outputfile, sep='\t', columns=['rsid', 'chromosome', 'position', 'allele1'], header=False, index=False)    #close the output file
    outputfile.close()
    return '03_tmpfiles/Filtered_User/b37_filtered_' + basename