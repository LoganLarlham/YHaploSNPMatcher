#!/bin/bash

grep -v "#" b37_filtered_Test4_DNA.txt | cut -f 1 >> relevant_rsids.txt