import pandas as pd
from collections import defaultdict
metadata = pd.read_csv("raw_data_2020_autumn.csv", index_col=0)
office_list = pd.read_csv("office_abbreviations_shortened.csv", sep=";")
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
    #set up initial dictionary
    if office not in bc_filings:
        for period in ["Priority filings", "PCT priority filings", "Non-priority filings", "Non-PCT priority filings", "Total"]:
            bc_filings[office][period] = 0
    
    if priority_binary == 1:
        bc_filings[office]["Total"] += 1
        bc_filings[office]["Priority filings"] += 1
        if "W" in pct_patent:
            bc_filings[office]["PCT priority filings"] += 1
        else:
            bc_filings[office]["Non-PCT priority filings"] += 1
        
    elif priority_binary == 0:
        bc_filings[office]["Non-priority filings"] += 1
        bc_filings[office]["Total"] += 1

outcome = pd.DataFrame.from_dict(data=bc_filings, orient="index")
outcome.sort_values(by=["Total"], inplace=True, ascending=False)
outcome.to_excel("Blockchain Patent Statistics.xlsx")

top3_offices = ["US", "CN", "KR"]
top3_offices_s = ["USA", "China", "Republic of Korea"]
filings = []
years = []
patent_office = []
filing_type = []

for counter, office in enumerate(top3_offices):
    df1 = metadata[metadata["appln_auth"]==office]
    for year in range(2009,2021):
        years.append(year)
        patent_office.append(top3_offices_s[counter])
        df2 = df1[df1["appln_filing_year"]==year]
        filings.append(len(df2))
        filing_type.append("Total")
        
        df3 = df2[df2["priority"]==1]
        years.append(year)
        patent_office.append(top3_offices_s[counter])
        filings.append(len(df3))
        filing_type.append("Priority")
        
        df3 = df2[df2["priority"]==0]
        years.append(year)
        patent_office.append(top3_offices_s[counter])
        filings.append(len(df3))
        filing_type.append("Non-Priority")      

data = pd.DataFrame(data=zip(filings, years, patent_office, filing_type), columns = ["Patent application count", "Filing year", "Authority", "Type"])
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
mpl.rcParams['font.size'] = 10
mpl.rcParams["font.family"] = "arial"
cm = 1/2.54
size_of_plots = [16*cm,6*cm]
plt.rc('axes', axisbelow=True)
plt.rcParams['axes.axisbelow'] = True

fig, ax1 = plt.subplots(ncols=1,nrows=1,figsize=size_of_plots, sharex=True)
sns.lineplot(ax = ax1, data=data, x="Filing year", y="Patent application count", hue="Authority", style="Type", palette = (sns.color_palette("Greys_r")[0], sns.color_palette("Greys_r")[2], sns.color_palette("Greys_r")[3]))
ax1.grid()
import numpy as np
ax1.set_xticks(np.arange(2009, 2021, 1))
ax1.set_xlabel("Filing year", style="italic")
ax1.set_ylabel("Patent application count", style="italic")
mpl.rcParams['font.size'] = 8
ax1.legend(fontsize="small")
plt.tight_layout()
plt.savefig("Patent Count per Filing Year, Authority and Type.png", dpi=1600)