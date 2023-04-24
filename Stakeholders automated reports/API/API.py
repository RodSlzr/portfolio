# PROPUBLICA
API_KEY = 1 # check private repo
# OPENSECRETS
API_KEY2 = 1 # check private repo
# email : 1 # check private repo
# password : 1 # check private repo

from redis import StrictRedis
from congress import Congress
import time
import json
from crpapi import CRP

crp = CRP(API_KEY2)
congress = Congress(API_KEY)

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

bill_type = ['introduced','updated','cosponsored','withdrawn']
os_get = ['office','phone','fax','webform','congress_office']
os_sum = ['cycle','first_elected','next_election','total','spent','cash_on_hand','debt','source',"last_updated"]

def populate(filter, id_dic):
    data = congress.members.filter(filter)
    if len(id_dic) < data[0]["num_results"]:
        for i in [j["id"] for j in data[0]["members"] if j["id"] not in id_dic]:
            try:
                id_dic[i] = congress.members.get(i)
                id_dic[i]['bills'] = {k : congress.bills.by_member(i, type = k)['bills'] for k in bill_type}
                for role in id_dic[i]['roles']:
                    for subcommittee in role['subcommittees']:
                        subcommittee['parent_committee_name'] = congress.committees.get(role['chamber'],\
                            subcommittee['parent_committee_id'], role['congress'])["name"]
                        subcommittee['parent_committee_url'] = congress.committees.get(role['chamber'],\
                            subcommittee['parent_committee_id'], role['congress'])["url"]
                for j in os_get:
                    id_dic[i][j] = crp.candidates.get(id_dic[i]['crp_id'])['@attributes'][j]
                for j in os_sum:
                    id_dic[i][j] = crp.candidates.summary(id_dic[i]['crp_id'])[j]
                id_dic[i]['top_organizations'] = [org['@attributes'] for org in\
                    crp.candidates.contrib(id_dic[i]['crp_id'], id_dic[i]['cycle'])]
                for organization in id_dic[i]['top_organizations']:
                    try:
                        organization['profile'] = crp.orgs.summary(crp.orgs.get(organization['org_name'])["@attributes"]["orgid"])
                    except:
                        continue
                id_dic[i]['top_industries'] = [org['@attributes']\
                    for org in crp.candidates.industries(id_dic[i]['crp_id'], id_dic[i]['cycle'])]
                id_dic[i]['top_sector'] = [org['@attributes']\
                    for org in crp.candidates.sector(id_dic[i]['crp_id'], id_dic[i]['cycle'])]
            except:
                time.sleep(75)
                return populate(filter, id_dic)
        return id_dic
    else:
        print('Dictionary already updated: ', filter)
        return id_dic

senate_dic = populate("senate", {})
house_dic = populate("house", {})

json_house_string = json.dumps(house_dic)
with open('json_house_data.json', 'w', encoding = 'utf-8') as f:
    json.dump(json_house_string, f, ensure_ascii = False, indent = 4)
    
json_senate_string = json.dumps(senate_dic)
with open('json_senate_data.json', 'w', encoding = 'utf-8') as f:
    json.dump(json_senate_string, f, ensure_ascii = False, indent = 4)

with open('json_senate_data.json', 'r', encoding = 'utf-8') as f:
    senate_dic = json.loads(json.load(f))

with open('json_house_data.json', 'r', encoding = 'utf-8') as f:
    house_dic = json.loads(json.load(f))
    