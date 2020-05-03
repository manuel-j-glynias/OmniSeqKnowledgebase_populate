import csv
# import requests
import datetime
import sys
import os
from graphql_utils import send_mutation, send_query, get_authors, get_journals, get_literature_references, PMID_extractor,  \
    replace_characters, get_gene_id_from_entrez_id, get_omnigene_id_from_entrez_id, get_omnigene_descriptions, \
    create_myGeneInfo_gene, create_omniGene, create_uniprot_entry, PubMed_extractor, get_jax_gene_ids, get_editor_ids, \
    createEditableStatement_with_date

from informatics_utils import fetch_gene_id_by_gene_name, fetch_gene_info_by_gene_id, populate_omni_gene, \
    create_hgnc_gene_name_dict

# gene_name,gene_description,editor,edit_date,references
def read_one_curation_file(file_name:str, all_genes:list):
    skip = True;
    content_dict = {}
    with open(file_name) as csvfile:
        readCSV = csv.reader(csvfile)
        for row in readCSV:
            if skip:
                skip=False
            else:
                content = {'gene' : row[0],
                                'statement': replace_characters(row[1]),
                                   'editor': row[2],
                                   'edit_date': row[3],
                                    'field' : row[4]
                                   }
                if len(row)>5:
                    content['references'] = row[5]
                if content['gene'] not in all_genes:
                    all_genes.append(content['gene'])
                if content['editor'] != 'loader':
                    content_dict[content['gene']] = content

    return content_dict

def read_curation_data()->list:
    all_genes = []
    description_dict = read_one_curation_file('out/descriptions.csv',all_genes)
    oncogenic_categories_dict = read_one_curation_file('out/oncogenic_categories.csv',all_genes)
    synonyms_dict = read_one_curation_file('out/synonyms.csv',all_genes)
    curation_data = []
    for gene in all_genes:
        des = None;
        cat = None;
        syn = None;
        if gene in description_dict:
            des = description_dict[gene]
        if gene in oncogenic_categories_dict:
            cat = oncogenic_categories_dict[gene]
        if gene in synonyms_dict:
            syn = synonyms_dict[gene]
        curation_item = {'gene':gene, 'description':des, 'oncogenic_category':cat, 'synonmyms':syn}
        curation_data.append(curation_item)
    return curation_data



# deleteOmniGeneGeneDescription(geneDescription: [ID!]!id: ID!): String
# Deletes GeneDescription from OmniGene entity

# addOmniGeneGeneDescription(geneDescription: [ID!]!id: ID!): String
# Adds GeneDescription to OmniGene entity

def write_new_gene_description(gene_id, old_description_id:str, field:str, statement:str, editor_id,edit_date:str,pmid_extractor:callable,reference_dict:dict,journal_dict:dict,author_dict:dict )->str:
    s = f'''deleteOmniGeneGeneDescription(geneDescription:[\\"{old_description_id}\\"], id:\\"{gene_id}\\"),'''
    (m, id1) = createEditableStatement_with_date(statement, field, editor_id, edit_date, pmid_extractor, reference_dict, journal_dict, author_dict)
    s += m
    s += f'addOmniGeneGeneDescription(geneDescription:[\\"{id1}\\"], id:\\"{gene_id}\\" ),'
    return s

def write_new_oncogenic_category(gene_id, old_oncogenic_category_id:str, field:str, statement:str, editor_id,edit_date:str,pmid_extractor:callable,reference_dict:dict,journal_dict:dict,author_dict:dict )->str:
    s = f'''deleteOmniGeneOncogenicCategory(oncogenicCategory:[\\"{old_oncogenic_category_id}\\"], id:\\"{gene_id}\\"),'''
    (m, id1) = createEditableStatement_with_date(statement, field, editor_id,edit_date, pmid_extractor,reference_dict,journal_dict,author_dict)
    s += m
    s += f'addOmniGeneOncogenicCategory(oncogenicCategory:[\\"{id1}\\"], id:\\"{gene_id}\\" ),'
    return s

def write_new_synonym_string(gene_id, old_synonym_string_id:str, field:str, statement:str, editor_id,edit_date:str,pmid_extractor:callable,reference_dict:dict,journal_dict:dict,author_dict:dict )->str:
    s = f'''deleteOmniGeneSynonymsString(synonymsString:[\\"{old_synonym_string_id}\\"], id:\\"{gene_id}\\"),'''
    (m, id1) = createEditableStatement_with_date(statement, field, editor_id,edit_date, pmid_extractor,reference_dict,journal_dict,author_dict)
    s += m
    s += f'addOmniGeneSynonymsString(synonymsString:[\\"{id1}\\"], id:\\"{gene_id}\\" ),'
    return s

def create_omniGene_for_update(omni_gene:dict, jax_gene_dict:dict, curation_item:dict, editor_ids:dict,pmid_extractor:callable, reference_dict:dict, journal_dict:dict, author_dict:dict)->(str,str,str,str):
    id = get_omnigene_id_from_entrez_id(omni_gene['entrez_gene_id'])
    gene: str = omni_gene['symbol']
    panel_name = omni_gene['panel_name']
    s = f'{id}: createOmniGene(id: \\"{id}\\", name: \\"{gene}\\", panelName:\\"{panel_name}\\" ),'

    # create geneDescription EditableStatement
    field1: str = 'geneDescription_' + id
    if curation_item['description'] != None:
        gene_description = curation_item['description']['statement']
        editor_id = editor_ids[curation_item['description']['editor']]
        edit_date = curation_item['description']['edit_date']
    else:
        gene_description = '(Insert Gene Description)'
        editor_id = editor_ids['loader']
        now = datetime.datetime.now()
        edit_date: str = now.strftime("%Y-%m-%d-%H-%M-%S-%f")

    statement1: str = gene_description
    (m, id1) = createEditableStatement_with_date(statement1,field1,editor_id,edit_date,pmid_extractor, reference_dict, journal_dict, author_dict)
    s += m
    s += f'addOmniGeneGeneDescription(geneDescription:[\\"{id1}\\"], id:\\"{id}\\" ),'

    if curation_item['oncogenic_category'] != None:
        statement2 = curation_item['oncogenic_category']['statement']
        editor_id = editor_ids[curation_item['oncogenic_category']['editor']]
        edit_date = curation_item['oncogenic_category']['edit_date']
    else:
        statement2 = 'Neither'
        editor_id = editor_ids['loader']
        now = datetime.datetime.now()
        edit_date: str = now.strftime("%Y-%m-%d-%H-%M-%S-%f")

        # create OncogenicCategory EditableStatement
    field2: str = 'OncogenicCategory_' + id
    (m, id2) = createEditableStatement_with_date(statement2,field2,editor_id,edit_date,pmid_extractor, reference_dict, journal_dict, author_dict)
    s += m
    s += f'addOmniGeneOncogenicCategory(id:\\"{id}\\", oncogenicCategory:[\\"{id2}\\"] ),'


    if curation_item['synonmyms'] != None:
        statement3 = curation_item['synonmyms']['statement']
        editor_id = editor_ids[curation_item['synonmyms']['editor']]
        edit_date = curation_item['synonmyms']['edit_date']
    else:
        statement3 = gene
        editor_id = editor_ids['loader']
        now = datetime.datetime.now()
        edit_date: str = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
    field3: str = 'SynonymsString_' + id
    (m, id3) = createEditableStatement_with_date(statement3, field3, editor_id,edit_date,pmid_extractor, reference_dict, journal_dict, author_dict)
    s += m
    s += f'addOmniGeneSynonymsString(id:\\"{id}\\", synonymsString:[\\"{id3}\\"] ),'

    # addOmniGeneJaxGene(id: ID!jaxGene: [ID!]!): String
# Adds JaxGene to OmniGene entity
#     jaxGene = get_gene_id_from_jax_id(omni_gene['entrez_gene_id'])
    if gene in jax_gene_dict:
        jaxGene = jax_gene_dict[gene]
        s += f'addOmniGeneJaxGene(id:\\"{id}\\", jaxGene:[\\"{jaxGene}\\"] ),'
    else:
        print("no jax gene for ",gene)
# addOmniGeneMyGeneInfoGene(id: ID!myGeneInfoGene: [ID!]!): String
# Adds MyGeneInfoGene to OmniGene entity
    myGeneInfoGene = get_gene_id_from_entrez_id(omni_gene['entrez_gene_id'])
    s += f'addOmniGeneMyGeneInfoGene(id:\\"{id}\\", myGeneInfoGene:[\\"{myGeneInfoGene}\\"] ),'

    # addOmniGeneUniprot_entry(id: ID!uniprot_entry: [ID!]!): String
    # Adds Uniprot_entry to OmniGene entity
    if 'sp_info' in omni_gene:
        uniprot_id:str = omni_gene['sp_info']['id']
        s += f'addOmniGeneUniprot_entry(id:\\"{id}\\", uniprot_entry:[\\"{uniprot_id}\\"] ),'
    else:
        print("no Uniprot_entry for ", gene)

    return s, id, id2, id3

def create_omni_gene(gene_name:str, curation_item:dict, editor_ids:dict,jax_gene_dict,pmid_extractor:callable,sp_pmid_extractor:callable, reference_dict:dict,journal_dict:dict,author_dict:dict,hgnc_gene_name_dict)->str:
    omni_gene: dict = {
        'symbol': gene_name,
        'panel_name': gene_name
    }
    if gene_name in hgnc_gene_name_dict:
        omni_gene['panel_name'] = gene_name
        omni_gene['synonym'] = gene_name
        gene_name = hgnc_gene_name_dict[gene_name]
        omni_gene['symbol'] = gene_name
    entrez_gene_id = fetch_gene_id_by_gene_name(gene_name)
    omni_gene['entrez_gene_id'] = entrez_gene_id
    editor_id = editor_ids['loader']
    if entrez_gene_id is None:
        print("no entrz gene id for", gene_name)
    else:
        gene_info = fetch_gene_info_by_gene_id(entrez_gene_id)
        populate_omni_gene(gene_info, omni_gene)
        print(omni_gene)
        s = create_myGeneInfo_gene(omni_gene,editor_id,pmid_extractor,reference_dict,journal_dict,author_dict)
        s += create_uniprot_entry(omni_gene,editor_id,sp_pmid_extractor,reference_dict,journal_dict,author_dict)
        m, omnigene_id, cat_id, syn_id = create_omniGene_for_update(omni_gene,jax_gene_dict,curation_item,editor_ids,pmid_extractor,reference_dict,journal_dict,author_dict)
        s += m
        return s


def update(server:str):
    editor_ids: dict = get_editor_ids(server)
    curation_data = read_curation_data()

    authors_dict:dict = get_authors(server)
    reference_dict:dict = get_literature_references(server)
    journals_dict:dict = get_journals(server)
    jax_gene_dict:dict = get_jax_gene_ids(server)

    omnigene_dict = get_omnigene_descriptions(server)
    hgnc_gene_name_dict = create_hgnc_gene_name_dict()

    for curation_item in curation_data:
        gene_name:str = curation_item['gene']

        if gene_name in hgnc_gene_name_dict:
            gene_name = hgnc_gene_name_dict[gene_name]
        print(gene_name)

        if gene_name not in omnigene_dict:
            print(gene_name + ' not in omnigene_dict')
            s = create_omni_gene(gene_name, curation_item, editor_ids, jax_gene_dict,
                                                           PMID_extractor,
                                                           PubMed_extractor, reference_dict, journals_dict,
                                                           authors_dict,
                                                           hgnc_gene_name_dict)
            print(s)
            send_mutation(s, server)
        else:
            omnigene_id = omnigene_dict[gene_name]['id']
            if curation_item['description'] is not None:
                old_description_id = omnigene_dict[gene_name]['description']['id']
                field = omnigene_dict[gene_name]['description']['field']
                gene_description = curation_item['description']['statement']
                editor_id = editor_ids[curation_item['description']['editor']]
                edit_date = curation_item['description']['edit_date']
                # def write_new_gene_description(gene_id, old_description_id:str, field:str, statement:str, editor_id,edit_date:str,pmid_extractor:callable,reference_dict:dict,journal_dict:dict,author_dict:dict )->str:
                s = write_new_gene_description(omnigene_id,old_description_id,field,gene_description, editor_id,edit_date,PMID_extractor,reference_dict,journals_dict,authors_dict)
                print(s)
                send_mutation(s, server)

            if curation_item['oncogenic_category'] is not None:
                old_category_id = omnigene_dict[gene_name]['oncogenic_category']['id']
                field = omnigene_dict[gene_name]['oncogenic_category']['field']
                oncogenic_category = curation_item['oncogenic_category']['statement']
                editor_id = editor_ids[curation_item['oncogenic_category']['editor']]
                edit_date = curation_item['oncogenic_category']['edit_date']
                s = write_new_oncogenic_category(omnigene_id, old_category_id, field,
                                               oncogenic_category, editor_id, edit_date,PMID_extractor, reference_dict,
                                               journals_dict, authors_dict)
                print(s)
                send_mutation(s, server)

            if curation_item['synonmyms'] is not None:
                old_synonmyms_id = omnigene_dict[gene_name]['synonyms']['id']
                field = omnigene_dict[gene_name]['synonyms']['field']
                synonmyms = curation_item['synonmyms']['statement']
                editor_id = editor_ids[curation_item['synonmyms']['editor']]
                edit_date = curation_item['synonmyms']['edit_date']
                s = write_new_synonym_string(omnigene_id, old_synonmyms_id, field,
                                                 synonmyms, editor_id, edit_date,PMID_extractor, reference_dict,
                                                 journals_dict, authors_dict)
                print(s)
                send_mutation(s, server)

        # gene_id, old_description_id,field = get_id_old_id_and_field(edit['gene'], server)
        # if gene_name not in omnigene_dict:
        #     gene_description:str = edit['description']
        #     s = create_omni_gene(edit['gene'],gene_description,editor_id,jax_gene_dict,PMID_extractor,PubMed_extractor,reference_dict,journals_dict,authors_dict,hgnc_gene_name_dict)
        #     print(s)
        #     send_mutation(s,server)
        # else:
        #     item = omnigene_dict[gene_name]
        #     s = write_new_gene_description(item['id'],item['statement'],item['field'],edit['description'], editor_id,PMID_extractor,reference_dict,journals_dict,authors_dict)
        #     print(s)
        #     send_mutation(s,server)
        print()






