import csv
import requests
import datetime
import sys

def read_oncgenes_tumor_suppressors(file_name: str) -> dict:
    skip = True;
    gene_categories = {}
    with open(file_name) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if skip:
                skip=False
            else:
                gene_categories[row[0]] = row[1]
    return gene_categories

def fetch_gene_id_by_gene_name(gene_name:str)->str:
    entrezgene_id = None
    requestURL = "http://mygene.info/v3/query?species=human&q=symbol:" + gene_name
    r = requests.get(requestURL, headers={"Accept": "application/json"})
    if not r.ok:
        r.raise_for_status()
        sys.exit()

    responseBody = r.json()
    # print(responseBody)
    if 'hits' in responseBody and len(responseBody['hits'])>0 and 'entrezgene' in responseBody['hits'][0]:
        entrezgene_id = responseBody['hits'][0]['entrezgene']
    return entrezgene_id


def fetch_gene_info_by_gene_id(gene_id:str)->dict:
  requestURL = "http://mygene.info/v3/gene/" + gene_id
  r = requests.get(requestURL, headers={ "Accept" : "application/json"})
  if not r.ok:
    r.raise_for_status()
    sys.exit()

  responseBody = r.json()
  # pprint.pprint(responseBody)
  return responseBody


def create_mygene_reference(gene_id):
  reference = {}
  reference['type'] = 'InternetReference'
  reference['url'] = "http://mygene.info/v3/gene/" + gene_id
  reference['accessed_date'] = datetime.datetime.now()
  return reference


def fetch_uniprot_by_acc_num(id):
  requestURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&accession=" + id
  r = requests.get(requestURL, headers={ "Accept" : "application/json"})
  if not r.ok:
    r.raise_for_status()
    sys.exit()
  responseBody = r.json()
  # pprint.pprint(responseBody)
  return responseBody[0]


def get_sp_info(uniprot_accession:str)->dict:
    sp_info = {'function': '', 'name':''}

    sp: dict = fetch_uniprot_by_acc_num(uniprot_accession)
    sp_info['acc_num'] = sp['accession']
    sp_info['id'] = 'uniprot_' + sp['accession']
    sp_info['uniprot_id'] = sp['id']
    if 'recommendedName' in sp['protein']:
        sp_info['name'] = sp['protein']['recommendedName']['fullName']['value']
    elif 'submittedName' in sp['protein']:
        sp_info['name'] = sp['protein']['submittedName'][0]['fullName']['value']

    for comment in sp['comments']:
        if comment['type'] == 'FUNCTION':
            if len(comment['text'])>0 and 'value' in comment['text'][0]:
                sp_info['function'] = comment['text'][0]['value']
            break

    return sp_info

def create_hgnc_gene_name_dict()->dict:
    genes = {}
    genes['C10orf54'] = 'VSIR'
    genes['C11orf30'] = 'EMSY'
    genes['FAM123B'] = 'AMER1'
    genes['FAM175A'] = 'ABRAXAS1'
    genes['FAM46C'] = 'TENT5C'
    genes['GPR124'] = 'ADGRA2'
    genes['H3F3A'] = 'H3-3A'
    genes['H3F3B'] = 'H3-3B'
    genes['H3F3C'] = 'H3-5'
    genes['HIST1H1C'] = 'H1-2'
    genes['HIST1H3B'] = 'H3C2'
    genes['HIST1H2BB'] = 'H2BC3'
    genes['HIST1H2BD'] = 'H2BC5'
    genes['HIST1H3A'] = 'H3C1'
    genes['HIST1H3E'] = 'H3C6'
    genes['HIST1H3F'] = 'H3C7'
    genes['HIST1H3G'] = 'H3C8'
    genes['HIST1H3H'] = 'H3C10'
    genes['HIST1H3I'] = 'H3C11'
    genes['HIST1H3J'] = 'H3C12'
    genes['HIST2H3A'] = 'H3C15'
    genes['HIST2H3C'] = 'H3C14'
    genes['HIST2H3D'] = 'H3C13'
    genes['HIST3H3'] = 'H3-4'
    genes['LOC101926927'] = 'withdrawn'
    genes['MARCH9'] = 'MARCHF9'
    genes['MLL'] = 'KMT2A'
    genes['MRE11A'] = 'MRE11'
    genes['MYCL1'] = 'MYCL'
    genes['PAK7'] = 'PAK5'
    genes['PARK2'] = 'PRKN'
    genes['RFWD2'] = 'COP1'
    genes['TCEB1'] = 'ELOC'
    genes['WISP3'] = 'CCN6'
    return genes




def populate_omni_gene(gene_info, omni_gene):
    genomic_pos = gene_info['genomic_pos_hg19']
    if isinstance(genomic_pos, list):
        genomic_pos = genomic_pos[0]
    omni_gene['chrom'] = genomic_pos['chr']
    omni_gene['strand'] = 'FORWARD'
    if genomic_pos['strand'] == -1:
        omni_gene['strand'] = 'REVERSE'
    omni_gene['start'] = genomic_pos['start']
    omni_gene['end'] = genomic_pos['end']
    omni_gene['reference'] = create_mygene_reference(omni_gene['entrez_gene_id'])
    if 'summary' in gene_info:
        omni_gene['summary'] = gene_info['summary']
    else:
        omni_gene['summary'] = 'chromosome: ' + str(omni_gene['chrom']) + ' from ' + str(omni_gene['start']) + ' to ' + str(omni_gene['end'])
    if 'alias' in gene_info:
        omni_gene['synonyms'] = gene_info['alias']
    omni_gene['synonyms'] = []
    if 'uniprot' in gene_info:
        if 'Swiss-Prot' in gene_info['uniprot']:
            if isinstance(gene_info['uniprot']['Swiss-Prot'], list):
                uniprot_accession = gene_info['uniprot']['Swiss-Prot'][0]
            else:
                uniprot_accession = gene_info['uniprot']['Swiss-Prot']
            omni_gene['sp_info'] = get_sp_info(uniprot_accession)