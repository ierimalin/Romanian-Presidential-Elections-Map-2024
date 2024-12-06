import os
import csv
import json
import requests
import pandas as pd

datadir = "data/raw"
results_dir = "data/processed"
turnout_dir = "data/turnout"
csvfile = f"{datadir}/election_data.csv"


def read_election_data():
    election_data = {}

    # The exact column names from the CSV
    party_columns = [
        "UNIUNEA DEMOCRATĂ MAGHIARĂ DIN ROMÂNIA-voturi",
        "PARTIDUL NAȚIONAL LIBERAL-voturi",
        "FORȚA DREPTEI-voturi",
        "ALIANȚA PENTRU UNIREA ROMÂNILOR-voturi",
        "UNIUNEA SALVAȚI ROMÂNIA-voturi",
        "PARTIDUL SOCIAL DEMOCRAT-voturi",
        "PARTIDUL OAMENILOR TINERI-voturi",
        "REÎNNOIM PROIECTUL EUROPEAN AL ROMÂNIEI-voturi",
        "PARTIDUL NOUA ROMÂNIE-voturi",
        "PARTIDUL S.O.S. ROMÂNIA-voturi",
        "PATRIOȚII POPORULUI ROMÂN-voturi",
        "PARTIDUL PHRALIPE AL ROMILOR-voturi",
        "PARTIDUL NAȚIONAL CONSERVATOR ROMÂN-voturi",
        "PARTIDUL ECOLOGIST ROMÂN-voturi",
        "PARTIDUL ROMÂNIA ÎN ACȚIUNE-voturi",
        "PARTIDUL REPUBLICAN DIN ROMÂNIA-voturi",
        "ALTERNATIVA PENTRU DEMNITATE NAȚIONALĂ-voturi",
        "PARTIDUL SOCIAL DEMOCRAT UNIT-voturi",
        "DREPTATE ȘI RESPECT ÎN EUROPA PENTRU TOȚI-voturi",
        "PARTIDUL SOCIAL DEMOCRAT INDEPENDENT-voturi",
        "SĂNĂTATE EDUCAŢIE NATURĂ SUSTENABILITATE-voturi",
        "LIGA ACȚIUNII NAȚIONALE-voturi",
        "ALIANȚA NAȚIONAL CREȘTINĂ-voturi",
        "ROMÂNIA SOCIALISTĂ-voturi",
        "PARTIDUL UNIUNEA GETO-DACILOR-voturi",
        "PARTIDUL DREPTĂȚII-voturi",
        "PARTIDUL PATRIA-voturi",
        "DANIEL CIOBBANU-CANDIDAT INDEPENDENT-voturi",
        "PARTIDUL VERDE-voturi",
        "PARTIDUL OAMENILOR CREDINCIOȘI-voturi",
        "PARTIDUL NAȚIONAL ȚĂRĂNESC CREȘTIN DEMOCRAT-voturi",
        "IOAN-MIHAI BĂCANU-CANDIDAT INDEPENDENT-voturi",
        "CIPRIAN-GHEORGHE STĂTESCU-CANDIDAT INDEPENDENT-voturi",
        "IULIAN LUNGU-CANDIDAT INDEPENDENT-voturi",
        "IOAN-AUREL STANCU-CANDIDAT INDEPENDENT-voturi",
        "CONSTANTIN-MIRCEA STOICA-CANDIDAT INDEPENDENT-voturi"
    ]

    #Removing annoying -voturi suffix
    party_names = [party.replace('-voturi', '') for party in party_columns]

    with open(csvfile, newline='', encoding='utf-8') as csv_file:
        csvreader = csv.DictReader(csv_file)
        
        print(f"CSV Headers: {csvreader.fieldnames}")
        
        for row in csvreader:
            county = row['precinct_county_name']  
            locality = row['uat_name']           
            
            if county not in election_data:
                election_data[county] = {}
            if locality not in election_data[county]:
                #Structure of the locality in the json
                election_data[county][locality] = {
                    'total_registered': 0,
                    'total_turnout': 0,
                    'permanent_list': 0,
                    'supplementary_list': 0,
                    'mobile_urn': 0,
                    'party_votes': {party: 0 for party in party_names}
                }
            
            #data sources
            election_data[county][locality]['total_registered'] += int(row['a'])
            election_data[county][locality]['total_turnout'] += int(row['b'])
            election_data[county][locality]['permanent_list'] += int(row['a1'])
            election_data[county][locality]['supplementary_list'] += int(row['a2'])
            election_data[county][locality]['mobile_urn'] += int(row['a3'])
            
            #aggregate for each party
            for i in range(len(party_columns)):
                party_name = party_names[i]
                election_data[county][locality]['party_votes'][party_name] += int(row[party_columns[i]])
    
    return election_data


def process_turnout_data(election_data):
    """Process the election data to calculate turnout statistics and party vote percentages."""
    processed_turnout_and_votes = {}

    for county, precincts in election_data.items():
        processed_turnout_and_votes[county] = {}

        for precinct_name, data in precincts.items():
            total_registered = data['total_registered']
            total_turnout = data['total_turnout']
            
            turnout_percentage = (total_turnout / total_registered) * 100 if total_registered > 0 else 0
            
            total_party_votes = sum(data['party_votes'].values())  
            party_percentages = {}
            for party, votes in data['party_votes'].items():
                party_percentages[party] = (votes / total_party_votes) * 100 if total_party_votes > 0 else 0

            processed_turnout_and_votes[county][precinct_name] = {
                "total_registered": total_registered,
                "total_turnout": total_turnout,
                "turnout_percentage": turnout_percentage,
                "permanent_list": data['permanent_list'],
                "supplementary_list": data['supplementary_list'],
                "mobile_urn": data['mobile_urn'],
                "party_votes": data['party_votes'],  
                "party_percentages": party_percentages  
            }

    output_file = os.path.join(results_dir, "turnout_and_party_votes.json")
    with open(output_file, "w", encoding='utf-8') as file:
        json.dump(processed_turnout_and_votes, file, indent=4, ensure_ascii=False)

    print(f"Turnout and party vote data saved to {output_file}.")

# For the nationwide data, I will employ web scraping from the roaep website.
cookies = {
    'route': '72e8872808a0ca7748a1ea7472ad9b9a',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,ro;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

params = {
    '_': '1733228483388',
}

response = requests.get(
    'https://prezenta.roaep.ro/parlamentare01122024/data/json/sicpv/pv/pv_aggregated.json',
    params=params,
    cookies=cookies,
    headers=headers,
)

t = response.json()

# Extracting data
senate_corespondence = t["scopes"]["CNTRY"]["S_C"]["RO"]["candidates"]
cd_corespondence = t["scopes"]["CNTRY"]["CD_C"]["RO"]["candidates"]
senate = t["scopes"]["CNTRY"]["S"]["RO"]["candidates"]
cd = t["scopes"]["CNTRY"]["CD"]["RO"]["candidates"]

df_senate = pd.DataFrame(senate)
df_senate_corespondence = pd.DataFrame(senate_corespondence)

df_cd = pd.DataFrame(cd)
df_cd_corespondence = pd.DataFrame(cd_corespondence)

# Merging data
df_senate_updated = pd.merge(df_senate, df_senate_corespondence[['id', 'votes']], on='id', how='left', suffixes=('_total', '_correspondence'))
df_senate_updated['votes_correspondence'] = df_senate_updated['votes_correspondence'].fillna(0)
df_senate_updated['total_votes'] = df_senate_updated['votes_total'] + df_senate_updated['votes_correspondence']

df_cd_updated = pd.merge(df_cd, df_cd_corespondence[['id', 'votes']], on='id', how='left', suffixes=('_total', '_correspondence'))
df_cd_updated['votes_correspondence'] = df_cd_updated['votes_correspondence'].fillna(0)
df_cd_updated['total_votes'] = df_cd_updated['votes_total'] + df_cd_updated['votes_correspondence']

#Calculate percentages
total_senate_votes = df_senate_updated['total_votes'].sum()
total_cd_votes = df_cd_updated['total_votes'].sum()

df_senate_updated['percentage'] = (df_senate_updated['total_votes'] / total_senate_votes) * 100
df_cd_updated['percentage'] = (df_cd_updated['total_votes'] / total_cd_votes) * 100


senate_updated_candidates = df_senate_updated[['id', 'candidate', 'total_votes', 'percentage']].to_dict(orient='records')
cd_updated_candidates = df_cd_updated[['id', 'candidate', 'total_votes', 'percentage']].to_dict(orient='records')

# Update the original 't' structure with percentage data
for i, candidate in enumerate(t["scopes"]["CNTRY"]["S"]["RO"]["candidates"]):
    senate_info = senate_updated_candidates[i]
    candidate['total_votes'] = senate_info['total_votes']
    candidate['percentage'] = senate_info['percentage']

for i, candidate in enumerate(t["scopes"]["CNTRY"]["CD"]["RO"]["candidates"]):
    cd_info = cd_updated_candidates[i]
    candidate['total_votes'] = cd_info['total_votes']
    candidate['percentage'] = cd_info['percentage']

# Save as new json - but be careful, the data inside [S] and [CD] now include correspondence too.
updated_t_json = json.dumps(t, ensure_ascii=False, indent=4)

output_file = os.path.join(results_dir, "aggregated_results.json")
with open(output_file, "w", encoding="utf-8") as file:
    file.write(updated_t_json)

print(f"Updated JSON file with aggregated county-and country-wide results saved to {output_file}.")

def main():
    election_data = read_election_data()
    process_turnout_data(election_data)

if __name__ == "__main__":
    main()
