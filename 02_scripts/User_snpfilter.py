#this script will have a function which takes test4.txt snp file and compares to the AncientYDNA/snpFile_b37_isogg2019.txt file 
#to cross-reference and filter out the snps that are not in the isogg2019 file. output subset file will include two header lines, first with user and haplogroup,
# second with column names. 
#should use pandas to read in the files and compare the snps.

#may want to add form for naming user.


import os
import sys
import pandas as pd

def UserCrossref(inputfile, haplogroup):
    #read in the isogg2019 file
    isogg2019 = pd.read_csv('01_Raw_data/AncientYDNA/snpFile_b37_isogg2019.txt', sep='\t')
    #add column names to isogg2019
    isogg2019.columns = ['rsid', 'position', 'ref', 'haplogroup', 'var', 'genotype']
    #read in the user snp file
    userfile = pd.read_csv(inputfile, sep='\t')
    #inputfiel basename
    basename = os.path.basename(inputfile)
    #make a new file to write to in current directory with  inputfile basename
    outputfile = open('TestUsers/b37_filtered_' + basename, 'w')
    #write the user and haplogroup to the file
    outputfile.write('#User: Test4 Haplogroup: ' + haplogroup + '\n')
    #write the column names to the file
    outputfile.write('#rsid\tchromosome\tposition\tallele1\tallele2\n')
    #remove all rows from userfile which do not have 24 in the chromosome column
    userfile = userfile[userfile['chromosome'] == 24]
    print(userfile.head())
    #copy lines from userfile to outputfile if the rsid is in the isogg2019 file
    for index, row in userfile.iterrows():
        if row['rsid'] in isogg2019['rsid'].values:
            outputfile.write(row['rsid'] + '\t' + str(row['chromosome']) + '\t' + str(row['position']) + '\t' + row['allele1'] + '\t' + row['allele2'] + '\n')
    #close the output file
    outputfile.close()
    #print a message to the user
    print('Filtered file has been created for ' + haplogroup + ' in TestUsers/Test4 folder.')



UserCrossref('01_Raw_data/TestUsers/Test4/Test4_DNA.txt', 'FGC11293')

sys.exit()
