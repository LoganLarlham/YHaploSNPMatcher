# Y Haplogroup Matcher

## Description

This application allows users to upload their DNA files in a specific format (plink format) to compare their Y-chromosomal DNA (Y-DNA) haplogroups against ancient DNA samples stored in the Ancient Ancestry DNA Repository (AADR). Users can discover which ancient DNA samples they are most similar to, based on the matching single-nucleotide polymorphisms (SNPs).

## Installation

Ensure you have Python and the following packages installed before running this application:

- Dash
- Pandas
- NumPy

You can install these packages using pip:

```shell
pip install dash pandas numpy
```

Or, if you prefer using Conda, use:

```shell
conda install dash pandas numpy
```
## Usage
To use the Y Haplogroup Matcher, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Run the app.py script located within the 04_Dashapp directory to start the Dash application:
```shell
python 04_Dashapp/app.py
```
4. Specify in the command line the port you'd like the webapp to run on.

5. Open a web browser and go to http://127.0.0.1:XXXX/ (XXXX being your specified port).

6. Follow the instructions on the web application to upload your DNA file and enter your Y haplogroup, or try using the test files included (Try using Haplogroup R1b1a1b)

7. lick Submit to view your results.

## Scripts Overview

The application consists of three main Python scripts:

app.py: Runs the Dash web application, allowing users to upload their DNA files and compare them against the AADR database.

User_snpfilter.py: Filters the user's SNP file to ensure compatibility with the AADR database and the specified haplogroup.

UserCompareAADR.py: Compares the filtered SNP file against the AADR database and calculates similarity based on matching SNPs.