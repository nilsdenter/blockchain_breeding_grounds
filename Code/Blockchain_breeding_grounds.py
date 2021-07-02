import pandas as pd
import statistics
from collections import defaultdict
import os
os.chdir("N:\\Publikationen\\2021 Blockchain Breeding grounds\\02_Analysis")
metadata = pd.read_csv("./Raw_Data/raw_data_2020_autumn.csv", index_col=0)
print("\nIn total {0} worldwide patent applications in Blockchain technology.".format(len(metadata)))
priority_filings_authorities = pd.read_csv("./Raw_Data/priority_filings_per_authority_and_year.csv")
priority_filings_worldwide = pd.read_csv("./Raw_Data/priority_filings_per_authority_and_year.csv")

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
metadata.to_excel("./Raw_Data/raw_data_2020_autumn.xlsx")

 
p1 = [i for i in range (2009,2015)]
p2 = [i for i in range(2015,2021)]
print("\nIn total {0} worldwide patent PRIORITY applications in Blockchain technology.".format(len(bc_priority_filing_ids)))

bc_priority_filings = defaultdict(lambda: defaultdict(int))
set_offices = set()

mean_values = defaultdict(lambda: defaultdict(float))

for index in bc_priority_filing_ids:
    data = metadata.loc[index,:]
    year = data["appln_filing_year"]
    office = data["appln_auth"]
    set_offices.add(office)
    if year in p1:
        period = "2009-2014"
    elif year in p2:
        period = "2015-2020"
    else:
        print("\nERROR: Year not in p1 nor p2!")
        break
    if office not in bc_priority_filings:
        bc_priority_filings[office][period] = 1
    elif period not in bc_priority_filings[office]:
        bc_priority_filings[office][period] = 1
    else:
        bc_priority_filings[office][period] += 1
    
    #sum up worldwide blockchain patents
    office = "Worldwide"
    if office not in bc_priority_filings:
        bc_priority_filings[office][period] = 1
    elif period not in bc_priority_filings[office]:
        bc_priority_filings[office][period] = 1
    else:
        bc_priority_filings[office][period] += 1

set_offices_without_epo_wipo_eapo = list(set_offices)[:]
set_offices_without_epo_wipo_eapo.remove("EP")
set_offices_without_epo_wipo_eapo.remove("WO")
set_offices_without_epo_wipo_eapo.remove("EA")
set_offices_without_epo_wipo_eapo.sort()
    
#all priority filings per authority
total_priority_filings = defaultdict(lambda: defaultdict(int))   
for index, row in priority_filings_authorities.iterrows():
    year = row["appln_filing_year"]
    office = row["appln_auth"]
    filings = row["number_priority_filings"]
    if year in p1:
        period = "2009-2014"
    elif year in p2:
        period = "2015-2020"
    else:
        print("\nERROR: Year not in p1 nor p2!")
        break
    if office not in total_priority_filings:
        total_priority_filings[office][period] = filings
    elif period not in total_priority_filings[office]:
        total_priority_filings[office][period] = filings
    else:
        total_priority_filings[office][period] += filings

#all worldwide priority filings
for index, row in priority_filings_worldwide.iterrows():
    year = row["appln_filing_year"]
    office = "Worldwide"
    filings = row["number_priority_filings"]
    if year in p1:
        period = "2009-2014"
    elif year in p2:
        period = "2015-2020"
    else:
        print("\nERROR: Year not in p1 nor p2!")
        break
    if office not in total_priority_filings:
        total_priority_filings[office][period] = filings
    elif period not in total_priority_filings[office]:
        total_priority_filings[office][period] = filings
    else:
        total_priority_filings[office][period] += filings
        
#calculate the revealed technology advantage index
rta = defaultdict(lambda: defaultdict(float))
output_rta = defaultdict(lambda: defaultdict(float))
rta_values_p1 = []
rta_values_p2 = []
for office in set_offices_without_epo_wipo_eapo:
    total_priority_bc = 0
    total_priority = 0
    total_priority_bc_worldwide = 0
    total_priority_worldwide = 0
    for period in ["2009-2014", "2015-2020"]:
        priority_bc = bc_priority_filings[office][period]
        total_priority_bc += priority_bc
        priority = total_priority_filings[office][period]
        total_priority += priority
        priority_bc_worldwide = bc_priority_filings["Worldwide"][period]
        total_priority_bc_worldwide += priority_bc_worldwide
        priority_worldwide = total_priority_filings["Worldwide"][period]
        total_priority_worldwide += priority_worldwide
        rta[office][period] = (priority_bc/priority)/(priority_bc_worldwide/priority_worldwide)
        output_rta[office_abbreviations[office]][period] = (priority_bc/priority)/(priority_bc_worldwide/priority_worldwide)
        if period == "2009-2014":
            rta_values_p1.extend([(priority_bc/priority)/(priority_bc_worldwide/priority_worldwide)])
        elif period == "2015-2020":
            rta_values_p2.extend([(priority_bc/priority)/(priority_bc_worldwide/priority_worldwide)])
            
    output_rta[office_abbreviations[office]]["Total_filings"] = bc_priority_filings[office]["2009-2014"] +  bc_priority_filings[office]["2015-2020"]
df_rta = pd.DataFrame.from_dict(data=output_rta, orient="index")
df_rta.sort_values(by=["2015-2020"], inplace=True)
mean_values["RTA"]["2009-2014"] = statistics.mean(rta_values_p1)
mean_values["RTA"]["2015-2020"] = statistics.mean(rta_values_p2)

#calculate national breeding grounds index
nbg = defaultdict(lambda: defaultdict(float))
output_nbg = defaultdict(lambda: defaultdict(float))
nbg_values_p1 = []
nbg_values_p2 = []
for office in set_offices_without_epo_wipo_eapo:
    for period in ["2009-2014", "2015-2020"]:
        rta_office = rta[office][period]
        priority_bc = bc_priority_filings[office][period]
        nbg[office][period] = rta_office * priority_bc
        output_nbg[office_abbreviations[office]][period] = rta_office * priority_bc
        if period == "2009-2014":
            nbg_values_p1.extend([rta_office * priority_bc])
        if period == "2015-2020":
            nbg_values_p2.extend([rta_office * priority_bc])
    output_nbg[office_abbreviations[office]]["Total_filings"] = bc_priority_filings[office]["2009-2014"] +  bc_priority_filings[office]["2015-2020"]
df_nbg = pd.DataFrame.from_dict(data=output_nbg, orient="index")
df_nbg.sort_values(by=["2015-2020"], inplace=True)
mean_values["NBG"]["2009-2014"] = statistics.mean(nbg_values_p1)
mean_values["NBG"]["2015-2020"] = statistics.mean(nbg_values_p2)

#sum up pct_priority_filings with appln_kind=='W' or non_pct if else
#mandantory to calculate the weighted national breeding grounds index, that is the RTA multiplicated with 5 times the pct priority applications and 0.2 times the non-pct priority applications
pct_priority_filings = defaultdict(lambda: defaultdict(int))
non_pct_priority_filings = defaultdict(lambda: defaultdict(int))
for index in bc_priority_filing_ids:
    data = metadata.loc[index,:]
    year = data["appln_filing_year"]
    if year in p1:
        period = "2009-2014"
    elif year in p2:
        period = "2015-2020"
    else:
        print("\nERROR: Year not in p1 nor p2!")
        break
    
    if "W" in data["appln_kind"]:
        office = data["receiving_office"]
        pct = 1
        non_pct = 0
    else:
        office = data["appln_auth"]
        pct = 0
        non_pct = 1
    
    if office not in pct_priority_filings or period not in pct_priority_filings[office]:
        pct_priority_filings[office][period] = pct
    else:
        pct_priority_filings[office][period] += pct
    if office not in non_pct_priority_filings or period not in non_pct_priority_filings[office]:
        non_pct_priority_filings[office][period] = non_pct
    else:
        non_pct_priority_filings[office][period] += non_pct
        



#calculate weighted national breeding grounds index
wnbg = defaultdict(lambda: defaultdict(float))
output_wnbg = defaultdict(lambda: defaultdict(float))
wnbg_values_p1 = []
wnbg_values_p2 = []
for office in set_offices_without_epo_wipo_eapo:
    for period in ["2009-2014", "2015-2020"]:
        rta_office = rta[office][period]
        priority_bc = (pct_priority_filings[office][period]*5) + (non_pct_priority_filings[office][period]/5)
        wnbg[office][period] = rta_office * priority_bc
        output_wnbg[office_abbreviations[office]][period] = rta_office * priority_bc
        if period == "2009-2014":
            wnbg_values_p1.extend([rta_office * priority_bc])
        if period == "2015-2020":
            wnbg_values_p2.extend([rta_office * priority_bc])
    output_wnbg[office_abbreviations[office]]["PCT filings 2009-2014"] = pct_priority_filings[office]["2009-2014"]
    output_wnbg[office_abbreviations[office]]["PCT filings 2015-2020"] = pct_priority_filings[office]["2015-2020"]
    output_wnbg[office_abbreviations[office]]["non_PCT filings 2009-2014"] = non_pct_priority_filings[office]["2009-2014"]
    output_wnbg[office_abbreviations[office]]["non_PCT filings 2015-2020"] = non_pct_priority_filings[office]["2015-2020"]
    output_wnbg[office_abbreviations[office]]["RTA 2009-2014"] = rta[office]["2009-2014"]
    output_wnbg[office_abbreviations[office]]["RTA 2015-2020"] = rta[office]["2015-2020"]        
df_wnbg = pd.DataFrame.from_dict(data=output_wnbg, orient="index")
df_wnbg.sort_values(by=["2015-2020"], inplace=True)
mean_values["WNBG"]["2009-2014"] = statistics.mean(wnbg_values_p1)
mean_values["WNBG"]["2015-2020"] = statistics.mean(wnbg_values_p2)


#figure for normal nbg and weighted nbg
os.chdir("N:\\Publikationen\\2021 Blockchain Breeding grounds\\Submission\\WPI\\Revision_1\\Figures\\new")
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import numpy as np
#fig, (ax1,ax2) = plt.subplots(ncols=1,nrows=2,figsize=[6.4,4*2], sharex=True)
fig, (ax1,ax2) = plt.subplots(ncols=2,nrows=1,figsize=[6.4*1.5,4])
#fig, (ax1,ax2) = plt.subplots(ncols=2,nrows=1,figsize=[6.4*1.5,4*1.5])
#fig, (ax1,ax2) = plt.subplots(ncols=1,nrows=2,figsize=[6.4,4*1.5])
mpl.rcParams['font.size'] = 10
mpl.rcParams["font.family"] = "calibri"
df_nbg.sort_values(by=["2015-2020"], inplace=True, ascending=False)

ax1.set(xscale="log")
ax2.set(xscale="log")
ax1.grid(color='lightgray', linewidth=0.5)
ax2.grid(color='lightgray', linewidth=0.5)
nbg_values_p1 = list(df_nbg["2009-2014"])[:15]
nbg_values_p2 = list(df_nbg["2015-2020"])[:15]
nbg_countries = list(df_nbg.index)[:15]

df = pd.DataFrame(data=[nbg_countries, nbg_values_p1,nbg_values_p2]).T
df.rename(columns={0: "Patent Authority", 1: "2009-2014", 2: "2015-2020"}, inplace=True)
df.sort_values(by=["2015-2020"], inplace=True, ascending=True)

ax1.scatter(x = df["2009-2014"], y=df["Patent Authority"], marker = "^", color="grey", label="2009-2014")
ax1.scatter(x = df["2015-2020"], y=df["Patent Authority"], marker = "o", color="black", label="2015-2020")

ax1.vlines(x=mean_values["NBG"]["2009-2014"], ymin=-5, ymax=20, colors="grey", linestyles="dashed", label = "Mean 2009-2014", linewidth=1)
ax1.vlines(x=mean_values["NBG"]["2015-2020"], ymin=-5, ymax=20, colors="black", linestyles="dashed", label = "Mean 2015-2020", linewidth=1)

ax1.set_ylim([-0.5, 14.5])
ax2.set_ylim([-0.5, 14.5])
ax1.set_xlabel("NBG index", style="italic")
ax2.set_xlabel("NBG_weighted index", style="italic")

df_wnbg.sort_values(by=["2015-2020"], inplace=True, ascending=False)

wnbg_values_p1 = list(df_wnbg["2009-2014"])[:15]
wnbg_values_p2 = list(df_wnbg["2015-2020"])[:15]
wnbg_countries = list(df_wnbg.index)[:15]

df = pd.DataFrame(data=[wnbg_countries, wnbg_values_p1,wnbg_values_p2]).T
df.rename(columns={0: "Patent Authority", 1: "2009-2014", 2: "2015-2020"}, inplace=True)
df.sort_values(by=["2015-2020"], inplace=True, ascending=True)

ax2.scatter(x = df["2009-2014"], y=df["Patent Authority"], marker = "^", color="grey", label="2009-2014")
ax2.scatter(x = df["2015-2020"], y=df["Patent Authority"], marker = "o", color="black", label="2015-2020")

ax2.vlines(x=mean_values["WNBG"]["2009-2014"], ymin=-5, ymax=20, colors="grey", linestyles="dashed", label = "Mean 2009-2014", linewidth=1)
ax2.vlines(x=mean_values["WNBG"]["2015-2020"], ymin=-5, ymax=20, colors="black", linestyles="dashed", label = "Mean 2015-2020", linewidth=1)
#ax1.legend(title="Period")



#ax2.legend(title="Period", loc='lower right')

ax2.legend(loc='center right', bbox_to_anchor=(1.4, 0.2))


mpl.rcParams['font.size'] = 12

#ax1.set(title="NBG")
fig.suptitle("National Breeding Grounds")

fig.tight_layout()
fig.savefig("National_Breeding_Grounds.png", dpi=1600)
plt.show()


#calculate blockchain patents coming from abroad, that are patents assigned at the respective office, yet being a priority application at an other office
#calculate blockchain patents going to abroad, that are patents assigned at other offices, yet being a priority application at the respective office
coming_from_abroad = defaultdict(lambda: defaultdict(int))
going_to_abroad = defaultdict(lambda: defaultdict(int))
for office in set_offices:
    for period in ["2009-2014", "2015-2020"]:
        coming_from_abroad[office][period] = 0
        going_to_abroad[office][period] = 0

for index, row in metadata.iterrows():
    office = row["appln_auth"]
    year = row["appln_filing_year"]
    if year in p1:
        period = "2009-2014"
    elif year in p2:
        period = "2015-2020"
    else:
        print("\nERROR: Year not in p1 nor p2!")
        break   
    earliest_filing_id = row["earliest_filing_id"]
    
    #going to abroad
    if index == earliest_filing_id and row["ipr_type"]=="PI":
        ids = metadata[metadata["earliest_filing_id"] == index].index.tolist()
        for i in ids:
            going_to_office = metadata.loc[i,"appln_auth"]
            if office != going_to_office:
                going_to_abroad[office][period] += 1
    
    #coming from abroad
    elif index != earliest_filing_id and row["ipr_type"]=="PI":
        ids = metadata[metadata["earliest_filing_id"] == earliest_filing_id].index.tolist()
        #search through all filings corresponding to the earliest filing id if the priority blockchain patent belongs to the dataset
        for i in ids:
            if i == earliest_filing_id and metadata.loc[i,"appln_auth"] != office:
                coming_from_abroad[office][period] += 1
                continue #because there is only one priority filing
    else:
        print("\nERROR: both if conditions did fail")
        break
                
#calculate international breeding grounds index
ibg = defaultdict(lambda: defaultdict(float))
output_ibg = defaultdict(lambda: defaultdict(float))
ibg_values_p1 = []
ibg_values_p2 = []

for office in set_offices_without_epo_wipo_eapo:
    for period in ["2009-2014", "2015-2020"]:
        priority_bc = bc_priority_filings[office][period]
        coming_abroad = coming_from_abroad[office][period]
        going_abroad = going_to_abroad[office][period]
        if priority_bc > 0:
            ibg[office][period] = (coming_abroad * going_abroad)/priority_bc
            output_ibg[office_abbreviations[office]][period] = (coming_abroad * going_abroad)/priority_bc
            if period == "2009-2014":
                ibg_values_p1.extend([(coming_abroad * going_abroad)/priority_bc])
            if period == "2015-2020":
                ibg_values_p2.extend([(coming_abroad * going_abroad)/priority_bc])
        else:
            ibg[office][period] = 0
            output_ibg[office_abbreviations[office]][period] = 0
            if period == "2009-2014":
                ibg_values_p1.extend([0])
            if period == "2015-2020":
                ibg_values_p2.extend([0])
                
    output_ibg[office_abbreviations[office]]["Going to abroad 2009-2014"] = going_to_abroad[office]["2009-2014"]
    output_ibg[office_abbreviations[office]]["Going to abroad 2015-2020"] = going_to_abroad[office]["2015-2020"]
    output_ibg[office_abbreviations[office]]["Coming from abroad 2009-2014"] = coming_from_abroad[office]["2009-2014"]
    output_ibg[office_abbreviations[office]]["Coming from abroad 2015-2020"] = coming_from_abroad[office]["2015-2020"]
    output_ibg[office_abbreviations[office]]["Priority filings 2009-2014"] = bc_priority_filings[office]["2009-2014"]
    output_ibg[office_abbreviations[office]]["Priority filings 2015-2020"] = bc_priority_filings[office]["2015-2020"]       
df_ibg = pd.DataFrame.from_dict(data=output_ibg, orient="index")
df_ibg.sort_values(by=["2015-2020"], inplace=True)
mean_values["IBG"]["2009-2014"] = statistics.mean(ibg_values_p1)
mean_values["IBG"]["2015-2020"] = statistics.mean(ibg_values_p2)


#calculate weighted international breeding grounds index
wibg = defaultdict(lambda: defaultdict(float))
output_wibg = defaultdict(lambda: defaultdict(float))
wibg_values_p1 = []
wibg_values_p2 = []
for office in set_offices_without_epo_wipo_eapo:
    for period in ["2009-2014", "2015-2020"]:
        wnbg_office = wnbg[office][period]
        coming_abroad = coming_from_abroad[office][period]
        going_abroad = going_to_abroad[office][period]
        if wnbg_office > 0:
            wibg[office][period] = (coming_abroad * going_abroad)/wnbg_office
            output_wibg[office_abbreviations[office]][period] = (coming_abroad * going_abroad)/wnbg_office
            if period == "2009-2014":
                wibg_values_p1.extend([(coming_abroad * going_abroad)/wnbg_office])
            if period == "2015-2020":
                wibg_values_p2.extend([(coming_abroad * going_abroad)/wnbg_office])
        else:
            wibg[office][period] = 0
            output_wibg[office_abbreviations[office]][period] = 0
            if period == "2009-2014":
                wibg_values_p1.extend([0])
            if period == "2015-2020":
                wibg_values_p2.extend([0])
    
    output_wibg[office_abbreviations[office]]["Going to abroad 2009-2014"] = going_to_abroad[office]["2009-2014"]
    output_wibg[office_abbreviations[office]]["Going to abroad 2015-2020"] = going_to_abroad[office]["2015-2020"]
    output_wibg[office_abbreviations[office]]["Coming from abroad 2009-2014"] = coming_from_abroad[office]["2009-2014"]
    output_wibg[office_abbreviations[office]]["Coming from abroad 2015-2020"] = coming_from_abroad[office]["2015-2020"]
    output_wibg[office_abbreviations[office]]["weighed_NBG 2009-2014"] = wnbg[office]["2009-2014"]
    output_wibg[office_abbreviations[office]]["weighted_NBG 2015-2020"] = wnbg[office]["2015-2020"]       
df_wibg = pd.DataFrame.from_dict(data=output_wibg, orient="index")
df_wibg.sort_values(by=["2015-2020"], inplace=True)
mean_values["WIBG"]["2009-2014"] = statistics.mean(wibg_values_p1)
mean_values["WIBG"]["2015-2020"] = statistics.mean(wibg_values_p2)
df_mean_values =  pd.DataFrame.from_dict(data=mean_values, orient="index")

#figure for normal ibg and weighted ibg


os.chdir("N:\\Publikationen\\2021 Blockchain Breeding grounds\\Submission\\WPI\\Revision_1\\Figures\\new")
#fig, (ax1,ax2) = plt.subplots(ncols=1,nrows=2,figsize=[6.4,4*2], sharex=True)
fig, (ax1,ax2) = plt.subplots(ncols=2,nrows=1,figsize=[6.4*1.5,4])
#fig, (ax1,ax2) = plt.subplots(ncols=2,nrows=1,figsize=[6.4*1.5,4*1.5])
#fig, (ax1,ax2) = plt.subplots(ncols=1,nrows=2,figsize=[6.4,4*1.5])
mpl.rcParams['font.size'] = 10
mpl.rcParams["font.family"] = "calibri"
df_ibg.sort_values(by=["2015-2020"], inplace=True, ascending=False)

ax1.set(xscale="log")
ax2.set(xscale="log")
ax1.grid(color='lightgray', linewidth=0.5)
ax2.grid(color='lightgray', linewidth=0.5)
ibg_values_p1 = list(df_ibg["2009-2014"])[:15]
ibg_values_p2 = list(df_ibg["2015-2020"])[:15]
ibg_countries = list(df_ibg.index)[:15]

df = pd.DataFrame(data=[ibg_countries, ibg_values_p1,ibg_values_p2]).T
df.rename(columns={0: "Patent Authority", 1: "2009-2014", 2: "2015-2020"}, inplace=True)
df.sort_values(by=["2015-2020"], inplace=True, ascending=True)

ax1.scatter(x = df["2009-2014"], y=df["Patent Authority"], marker = "^", color="grey", label="2009-2014")
ax1.scatter(x = df["2015-2020"], y=df["Patent Authority"], marker = "o", color="black", label="2015-2020")

ax1.vlines(x=mean_values["IBG"]["2009-2014"], ymin=-5, ymax=20, colors="grey", linestyles="dashed", label = "Mean 2009-2014", linewidth=1)
ax1.vlines(x=mean_values["IBG"]["2015-2020"], ymin=-5, ymax=20, colors="black", linestyles="dashed", label = "Mean 2015-2020", linewidth=1)


#ax1.set(title="A")
#ax2.set(title="B")

ax1.set_ylim([-0.5, 14.5])
ax2.set_ylim([-0.5, 14.5])
ax1.set_xlabel("IBG index", style="italic")
ax2.set_xlabel("IBG_weighted index", style="italic")
df_wibg.sort_values(by=["2015-2020"], inplace=True, ascending=False)

wibg_values_p1 = list(df_wibg["2009-2014"])[:15]
wibg_values_p2 = list(df_wibg["2015-2020"])[:15]
wibg_countries = list(df_wibg.index)[:15]

df = pd.DataFrame(data=[wibg_countries, wibg_values_p1,wibg_values_p2]).T
df.rename(columns={0: "Patent Authority", 1: "2009-2014", 2: "2015-2020"}, inplace=True)
df.sort_values(by=["2015-2020"], inplace=True, ascending=True)

ax2.scatter(x = df["2009-2014"], y=df["Patent Authority"], marker = "^", color="grey", label="2009-2014")
ax2.scatter(x = df["2015-2020"], y=df["Patent Authority"], marker = "o", color="black", label="2015-2020")

ax2.vlines(x=mean_values["WIBG"]["2009-2014"], ymin=-5, ymax=20, colors="grey", linestyles="dashed", label = "Mean 2009-2014", linewidth=1)
ax2.vlines(x=mean_values["WIBG"]["2015-2020"], ymin=-5, ymax=20, colors="black", linestyles="dashed", label = "Mean 2015-2020", linewidth=1)

#ax2.legend(title="Period", loc='lower right')
ax2.legend(loc='center right', bbox_to_anchor=(1.4, 0.2))

#ax1.set(title="NBG")
mpl.rcParams['font.size'] = 12
fig.suptitle("International Breeding Grounds")

fig.tight_layout()
fig.savefig("International_Breeding_Grounds.png", dpi=1600)
plt.show()