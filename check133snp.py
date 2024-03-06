#a script to check if any of /home/inf-35-2023/b29_popgen_proj/01_Raw_data/TestUsers/Test2/1335f138c24a7a0183238a9862b8713b.csv rsids are in /home/inf-35-2023/b29_popgen_proj/01_Raw_data/AncientYDNA/snpFile_b37_isogg2019.txt

import os
import sys

file133 = pd.read_csv('/home/inf-35-2023/b29_popgen_proj/01_Raw_data/TestUsers/Test2/1335f138c24a7a0183238a9862b8713b.csv', sep=',')

isogg2019 = pd.read_csv('/home/inf-35-2023/b29_popgen_proj/01_Raw_data/AncientYDNA/snpFile_b37_isogg2019.txt', sep='\t')

#check if any of file133 first columns values are in isogg2019 first column values and print them, not based on rsid

#check if any of file133 first columns values are in isogg2019 first column values and print them, not based on rsid

matches = file133[file133.columns[0]].isin(isogg2019[isogg2019.columns[0]].values)
print(matches.sum())


