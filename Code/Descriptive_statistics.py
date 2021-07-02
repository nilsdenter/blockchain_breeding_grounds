output = False

import pandas as pd
import statistics
from collections import defaultdict
metadata = pd.read_csv("./Raw_Data/raw_data_2020_autumn.csv", index_col=0)
office_list = pd.read_csv("./Raw_Data/office_abbreviations_shortened.csv")
office_abbreviations = {}
for index, row in office_list.iterrows():
    short = row["Short"]
    long = row["Long"]
    office_abbreviations[short]=long
    

bc_priority_filing_ids = []
binary_priority = []

for index, row in metadata.iterrows():
    if index == row["earliest_filing_id"] and row["ipr_type"]=="PI":
        bc_priority_filing_ids.append(index)
        binary_priority.append(1)
    else:
        binary_priority.append(0)

metadata["priority"] = binary_priority
#metadata.to_excel("./Raw_Data/raw_data_2020_autumn.xlsx")

p1 = [i for i in range (2009,2015)]
p2 = [i for i in range(2015,2021)]

bc_filings = defaultdict(lambda: defaultdict(int))
set_offices = set()
exclude_offices = ["WO", "EP", "EA", "IB"]
exclude_offices = []

for patent, data in metadata.iterrows():
    
    year = data["appln_filing_year"]
    office = data["appln_auth"]
    pct_patent = data["appln_kind"]
    if "W" in pct_patent:
        office = data["receiving_office"]
    
    if office in office_abbreviations:
        office = office_abbreviations[office]
    
    if office in exclude_offices: continue
    priority_binary = data["priority"]
    #set up initial dictionariy
    if office not in bc_filings:
        for period in ["Priority filings 2009-2014", "Priority filings 2015-2020", "Priority filings", "PCT priority filings 2009-2014", "PCT priority filings 2015-2020", "PCT priority filings", "Non-priority filings 2009-2014",  "Non-priority filings 2015-2020", "Non-priority filings",  "Non-PCT priority filings 2009-2014", "Non-PCT priority filings 2015-2020", "Non-PCT priority filings"]:
            bc_filings[office][period] = 0
    
    if priority_binary == 1:
        
        bc_filings[office]["Priority filings"] += 1
        if "W" in pct_patent:
            bc_filings[office]["PCT priority filings"] += 1
        else:
            bc_filings[office]["Non-PCT priority filings"] += 1
        if year in p1:
            bc_filings[office]["Priority filings 2009-2014"] += 1
            if "W" in pct_patent:
                bc_filings[office]["PCT priority filings 2009-2014"] += 1
            else:
                bc_filings[office]["Non-PCT priority filings 2009-2014"] += 1
        elif year in p2:
            bc_filings[office]["Priority filings 2015-2020"] += 1
            if "W" in pct_patent:
                bc_filings[office]["PCT priority filings 2015-2020"] += 1
            else:
                bc_filings[office]["Non-PCT priority filings 2015-2020"] += 1
        
    elif priority_binary == 0:
        bc_filings[office]["Non-priority filings"] += 1
        if year in p1:
            typ = "Non-priority filings 2009-2014"
        elif year in p2:
            typ = "Non-priority filings 2015-2020"
        bc_filings[office][typ] += 1

outcome = pd.DataFrame.from_dict(data=bc_filings, orient="index")
outcome.sort_values(by=["Priority filings", "Non-priority filings"], inplace=True, ascending=False)
outcome.to_excel("descriptives.xlsx")