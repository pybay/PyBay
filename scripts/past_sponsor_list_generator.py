import csv
company_dict = {}
with open("PyBayPastSponsorsWithWeightedAmount.csv", "r") as f:
    company_share = csv.reader(f)
    for company_data in company_share:
        if company_data[0] not in company_dict:
            company_dict[company_data[0]] = 0
        company_dict[company_data[0]] = company_dict[company_data[0]]+ round(int(company_data[1])/10)

with open("finalpastsponsorlist.txt", "w") as pslf:
    for name, weight in company_dict.items():
        company_name_times = f"{name},"*weight
        pslf.write(company_name_times)
