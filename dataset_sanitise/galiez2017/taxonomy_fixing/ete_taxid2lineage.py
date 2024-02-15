# from ete3 import NCBITaxa
import subprocess
import os
import pathlib as pl
# from pyfastx import Fasta
from typing import List
import json


# get accession from fastas
# /mnt/storage_3/home/hyperscroll/pl0240-01/project_data/phastdna/datasets/Galiez2017/host/fasta
# /home/mmichalczyk/Galiez2017/host
# i ran this on ibm
def get_acc_list(host_path: str):
    fasta_dir = pl.Path(host_path)
    for file in fasta_dir.glob('*.fna'):
        reader = Fasta(file.as_posix())
        print(f'{file.stem}:{reader[0].description.split("[")[1].split("]")[0] if "[" in reader[0].description else reader[0].description.split()[0]}')

# eutils 
#cat accessions_list.txt | epost -db nuccore | esummary -db nuccore | xtract -pattern DocumentSummary -element Caption,TaxId
# command = [
#     "cat", "../../accessions_list.txt",
#     "|", "epost", "-db", "nuccore",
#     "|", "esummary", "-db", "nuccore",
#     "|", "xtract", "-pattern", "DocumentSummary", "-element", "Caption,TaxId"
# ]


def get_taxid_list(acc_list_path: str, output_file_path: str):
# read file - each line is an accessionS
    with open(acc_list_path, "r") as f:
        accessions = f.readlines()
        accessions = [(acc.split(":")[0].strip(), acc.split(":")[1].strip()) for acc in accessions]
    for acc in accessions:
        awk_part = "'{print " + f'"{acc[0]}:"' + '$1' + '"\\t"' + "$2}'"
        # print(awk_part)
        command = f'esummary -db nuccore -id {acc[1]} |  xtract -pattern DocumentSummary -element Caption,TaxId | awk {awk_part} >> {output_file_path}'
        # print(command)
        result = os.system(command)


def compare_accessions_list(lineage_dict1: str, lineage_dict2: str):
    # read json file
    with open(lineage_dict1, "r") as f:
        lineage1 = json.load(f)
    with open(lineage_dict2, "r") as f:
        lineage2 = json.load(f)
    lineage1_len = len(lineage1)
    lineage2_len = len(lineage2)
    omitted = []
    diff_count = 0
    for key in lineage1:
        lineage_names1 = lineage1[key]["lineage_names"]
        try:
            lineage_names2 = lineage2[key]
            # lineage_names2[-1] = f"{lineage_names2[-1].split(". ")[0]}." if lineage_names2[-1] is not None else None
        except KeyError:
            print(f"Key {key} not found in lineage2. Omitted in the taxid fetch")
            omitted.append(key)
            continue
        if lineage_names1 != lineage_names2:
            diff_count += 1
            print(f"Lineage names are different for {key}")
            print(f"ete_way:   {lineage_names1}\nacc_taxid: {lineage_names2}")
            print(f"-------------------")
    print(f"lineage1 (ete) count: {lineage1_len}")
    print(f"lineage2 (acc_taxid) count: {lineage2_len}")
    print(f"difference in: {diff_count}/{lineage1_len}")
    print(f"Omitted {len(omitted)} records")
    print(omitted)
    # print(f"from taxid as list: {len(acc_list1)}")
    # print(f"from acc as list: {len(acc_list2)}")
    # acc_list1: set = set(acc_list1)
    # acc_list2: set = set(acc_list2)
    # print(f"from taxid as set: {len(acc_list1)}")
    # print(f"from acc as set: {len(acc_list2)}")
    # return acc_list1.difference(acc_list2)

def omitted_acc2new_acc_list(omitted_path: str, acc_list_base: str, new_acc_list_path: str):
    with open(omitted_path, "r") as f:
        accessions = f.readlines()
    accessions = [acc.split(" ")[-4] for acc in accessions]
    with open(acc_list_base, "r") as f:
        taxids = f.readlines()
    reversed_taxids = {taxid.strip().split(":")[1]: taxid.strip().split(":")[0] for taxid in taxids}
    new_acc_list = [f"{reversed_taxids[acc]}:{acc}" for acc in accessions]
    with open(new_acc_list_path, 'w') as f:
        print(*new_acc_list, sep="\n", file=f)


def merge_lineages(json1_path: str, json2_path: str, output_lineage_path: str):
    # open dict1
    with open(json1_path, "r") as f:
        lineage1 = json.load(f)
    with open(json2_path, "r") as f:
        lineage2 = json.load(f)
    lineage1.update(lineage2)
    with open(output_lineage_path, "w") as f:
        json.dump(lineage1, f, indent=2)


def remove_strain(json_path: str, output_lineage_path: str):
    with open(json_path, "r") as f:
        lineage = json.load(f)
    for key in lineage:
        name = lineage[key][-1]
        if "sp." in name:
            name = name.split("sp.")[0].strip()
            lineage[key][-1] = f"{name} sp."
    with open(output_lineage_path, "w") as f:
        json.dump(lineage, f, indent=2)


def create_host_metadata(prev_host_wfix: str, new_lineage_json: str, output_metadata_path: str):
    # read json file
    with open(prev_host_wfix, "r") as f:
        prev_host_json = json.load(f)
    with open(new_lineage_json, "r") as f:
        new_lineage = json.load(f)
    # lineage1_len = len(lineage1)
    # lineage2_len = len(lineage2)
    omitted = []
    rank_none_count = {
        "superkingdom": 0,
        "phylum": 0,
        "class": 0,
        "order": 0,
        "family": 0,
        "genus": 0,
        "species": 0
    }
    # diff_count = 0
    for key in prev_host_json:
        lineage_names1 = prev_host_json[key]["lineage_names"]
        try:
            lineage_names2 = new_lineage[key]
            # lineage_names2[-1] = f"{lineage_names2[-1].split(". ")[0]}." if lineage_names2[-1] is not None else None
        except KeyError:
            print(f"Key {key} not found in lineage2. Removing from the metadata")
            omitted.append(key)
            continue
        if lineage_names1 != lineage_names2:
            prev_host_json[key]["lineage_names"] = lineage_names2
            # check for none at ranks
        for i, rank in enumerate(prev_host_json[key]["lineage_names"]):
            if rank is None:
                rank_none_count[list(rank_none_count.keys())[i]] += 1
            # diff_count += 1
            # print(f"Lineage names are different for {key}")
            # print(f"ete_way:   {lineage_names1}\nacc_taxid: {lineage_names2}")
            # print(f"-------------------")
    for obj in omitted:
        prev_host_json.pop(obj)
    
    print(f"rank_none_count: {rank_none_count}")
    print(f"metadata count: {len(prev_host_json)}")
    with open(output_metadata_path, "w") as f:
        json.dump(prev_host_json, f, indent=2)
    
    # print(f"lineage1 (ete) count: {lineage1_len}")
    # print(f"lineage2 (acc_taxid) count: {lineage2_len}")
    # print(f"difference in: {diff_count}/{lineage1_len}")
    # print(f"Omitted {len(omitted)} records")
    # print(omitted)


# read taxid_list.txt
def get_lineage(taxid_list_path: str, output_lineage_path: str):
    with open(taxid_list_path, "r") as f:
        taxids = f.readlines()
        taxids = [taxid.strip() for taxid in taxids]
        # accession_from_taxid = [taxid.split("\t")[0] for taxid in taxids]
    # print(taxids[0].split("\t")[1])
    # open accession list
    # with open(acc_list_path, "r") as f:
    #     accessions = f.readlines()
    #     accessions = [acc.strip() for acc in accessions]
    #diff = comapare_accessions_list(accession_from_taxid, accessions)
    #print(diff)
    #print(len(diff))
    #exit()
    ncbi = NCBITaxa()
    lineage_dict = {}
    lineage_ranks = [
        "superkingdom",
        "phylum",
        "class",
        "order",
        "family",
        "genus",
        "species"]
    for record in taxids:
        # print(record)
        record = record.split("\t")
        print(record)
        taxid = record[1]
        filename = record[0].split(":")[0]
        lineage = ncbi.get_lineage(taxid)
        names = ncbi.get_taxid_translator(lineage)
        # print(names)
    # {1: 'root', 2: 'Bacteria', 1224: 'Pseudomonadota', 1236: 'Gammaproteobacteria', 28256: 'Halomonadaceae', 114185: 'Candidatus Carsonella', 114186: 'Candidatus Carsonella ruddii', 114403: 'Zymobacter group', 131567: 'cellular organisms', 135619: 'Oceanospirillales', 387662: 'Candidatus Carsonella ruddii PV'}
        rank = ncbi.get_rank(lineage)
        # print(rank)
    # {1: 'no rank', 2: 'superkingdom', 1224: 'phylum', 1236: 'class', 28256: 'family', 114185: 'genus', 114186: 'species', 114403: 'no rank', 131567: 'no rank', 135619: 'order', 387662: 'strain'}
    # lineage_and_rank = {v: lineage[k] for k, v in rank.items()}
        lineage_and_rank = {v: names[k] for k, v in rank.items()}
        # print(lineage_and_rank)
    # {'no rank': 'cellular organisms', 'superkingdom': 'Bacteria', 'phylum': 'Pseudomonadota', 'class': 'Gammaproteobacteria', 'family': 'Halomonadaceae', 'genus': 'Candidatus Carsonella', 'species': 'Candidatus Carsonella ruddii', 'order': 'Oceanospirillales', 'strain': 'Candidatus Carsonella ruddii PV'}
        final_lineage = [lineage_and_rank.get(rank, None) for rank in lineage_ranks]
        lineage_dict[filename] = final_lineage
        # print(f"final_lineage")
# ['Bacteria', 'Pseudomonadota', 'Gammaproteobacteria', 'Oceanospirillales', 'Halomonadaceae', 'Candidatus Carsonella', 'Candidatus Carsonella ruddii']
    # save to json
    with open(output_lineage_path, "w") as f:
        json.dump(lineage_dict, f, indent=2)
# 1273687
        

def fix_virus_metadata(host_json: str, prev_virus: str, output_virus_path: str):
    with open(host_json, "r") as f:
        host_json = json.load(f)
    with open(prev_virus, "r") as f:
        virus_json = json.load(f)
    
    changed = 0
    no_change = 0

    for virus_key in virus_json:
        no_change_flag = False
        virus_host = virus_json[virus_key]["host"]['name']
        for host_key in host_json:
            new_name = host_json[host_key]["lineage_names"][-1]
            prev_name = host_json[host_key]["prev_name"]
            new_lineage = host_json[host_key]["lineage_names"]
            old_lineage = virus_json[virus_key]['host']['lineage_names']
            if prev_name == virus_host:
                if new_name != virus_host or new_lineage != old_lineage:
                    # for i, rank in enumerate(new_lineage):
                    #     if rank is None:
                    #         new_lineage[i] = 'unknown'
                    print(new_lineage)
                    virus_json[virus_key]['host']['name'] = new_name
                    virus_json[virus_key]['host']['lineage_names'] = new_lineage
                    print(f">CHANGE {virus_key}\nPrev lineage: {old_lineage}\n New lineage:  {new_lineage}")
                    changed += 1
                    break
                else:
                    no_change_flag = True
                    print(f">NO CHANGE {virus_key}\nPrev lineage: {old_lineage}\n New lineage:  {new_lineage}")
        if no_change_flag:
            no_change += 1
    print(f"Changed: {changed} | No change: {no_change}")

    with open(output_virus_path, "w") as f:
        json.dump(virus_json, f, indent=2)


def check_unlinked_interactions(host_json: str, virus_json: str, output_unlinked_path: str):
    with open(host_json, "r") as f:
        host_json = json.load(f)
    with open(virus_json, "r") as f:
        virus_json = json.load(f)
    
    unlinked_interactions = []
    for virus_key in virus_json:
        link_flag = False
        virus_host_lineage = virus_json[virus_key]["host"]['lineage_names']
        for host_key in host_json:
            host_host_lineage = host_json[host_key]["lineage_names"]
            if virus_host_lineage == host_host_lineage:
                link_flag = True
                break
        if not link_flag:
            unlinked_interactions.append(virus_key)
            print(f'Unlinked interaction: {virus_key}\n Host from virus: {virus_json[virus_key]["host"]["lineage_names"]}')
    with open(output_unlinked_path, "w") as f:
        json.dump(unlinked_interactions, f, indent=2)



def fix_unlinked_interactions(host_json: str, virus_json: str, unlinked_json: str, output_virus_path: str):
    with open(host_json, "r") as f:
        host_json = json.load(f)
    with open(virus_json, "r") as f:
        virus_json = json.load(f)
    with open(unlinked_json, "r") as f:
        unlinked_interactions = json.load(f)
    
    # unlinked_interactions = []
    for virus_key in unlinked_interactions:
        virus_host_lineage = virus_json[virus_key]["host"]['lineage_names']
        virus_host_name = virus_json[virus_key]["host"]["name"]
        for host_key in host_json:
            host_host_lineage = host_json[host_key]["lineage_names"]
            host_host_name = host_json[host_key]["name"]
            if virus_host_name in host_host_name:
                virus_json[virus_key]["host"]['lineage_names'] = host_host_lineage
                print(f'Fixed unlinked interaction: {virus_key}\n New Host from virus: {virus_json[virus_key]["host"]["lineage_names"]}')
                # unlinked_interactions.append(virus_key)
                break
    with open(output_virus_path, "w") as f:
        json.dump(virus_json, f, indent=2)