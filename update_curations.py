import csv
# import requests
import datetime
import sys
import os
from graphql_utils import send_mutation, send_query, get_editor_id, createEditableStatement, create_jax_description, \
    get_authors, get_journals, get_literature_references, PMID_extractor, get_jax_descriptions, get_omnigenes, \
    replace_characters, get_gene_id_from_entrez_id, get_omnigene_id_from_entrez_id, get_omnigene_descriptions, \
    create_myGeneInfo_gene, create_omniGene, create_uniprot_entry, PubMed_extractor, get_jax_gene_ids

from informatics_utils import fetch_gene_id_by_gene_name, fetch_gene_info_by_gene_id, populate_omni_gene, \
    create_hgnc_gene_name_dict


def read_edits(file_name:str):
    skip = True;
    edits = []
    with open(file_name) as csvfile:
        readCSV = csv.reader(csvfile, delimiter='\t')
        for row in readCSV:
            if skip:
                skip=False
            else:
                gene_categories = {'gene' : row[0],
                                'description': replace_characters(row[5])}
                edits.append(gene_categories)

    return edits



# deleteOmniGeneGeneDescription(geneDescription: [ID!]!id: ID!): String
# Deletes GeneDescription from OmniGene entity

# addOmniGeneGeneDescription(geneDescription: [ID!]!id: ID!): String
# Adds GeneDescription to OmniGene entity

def write_new_gene_description(gene_id, old_description_id:str, field:str, statement:str, editor_id,pmid_extractor:callable,reference_dict:dict,journal_dict:dict,author_dict:dict )->str:
    s = f'''deleteOmniGeneGeneDescription(geneDescription:[\\"{old_description_id}\\"], id:\\"{gene_id}\\"),'''
    (m, id1) = createEditableStatement(statement, field, editor_id,pmid_extractor,reference_dict,journal_dict,author_dict)
    s += m
    s += f'addOmniGeneGeneDescription(geneDescription:[\\"{id1}\\"], id:\\"{gene_id}\\" ),'
    # print(s)
    return s
    # responseBody = send_mutation(s, server)
    # print(responseBody)


def create_omni_gene(gene_name:str, gene_description:str, editor_id:str,jax_gene_dict,pmid_extractor:callable,sp_pmid_extractor:callable, reference_dict:dict,journal_dict:dict,author_dict:dict,hgnc_gene_name_dict)->str:
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
    if entrez_gene_id is None:
        print("no entrz gene id for", gene_name)
    else:
        gene_info = fetch_gene_info_by_gene_id(entrez_gene_id)
        populate_omni_gene(gene_info, omni_gene)
        print(omni_gene)
        s = create_myGeneInfo_gene(omni_gene,editor_id,pmid_extractor,reference_dict,journal_dict,author_dict)
        s += create_uniprot_entry(omni_gene,editor_id,sp_pmid_extractor,reference_dict,journal_dict,author_dict)
        s += create_omniGene(omni_gene,jax_gene_dict,gene_description,editor_id,pmid_extractor,reference_dict,journal_dict,author_dict)
        return s

def update(server:str):
    editor:str = 'Carrie.Hoefer@omniseq.com'
    editor_id:str = get_editor_id(editor,server)
    print(editor_id)
    edits = read_edits('data/GeneDescriptions2.tsv')
    authors_dict:dict = get_authors(server)
    reference_dict:dict = get_literature_references(server)
    journals_dict:dict = get_journals(server)
    jax_gene_dict:dict = get_jax_gene_ids(server)

    omnigene_dict = get_omnigene_descriptions(server)
    hgnc_gene_name_dict = create_hgnc_gene_name_dict()

    for edit in edits:
        gene_name:str = edit['gene']
        if gene_name in hgnc_gene_name_dict:
            gene_name = hgnc_gene_name_dict[gene_name]

        print(gene_name)
        # gene_id, old_description_id,field = get_id_old_id_and_field(edit['gene'], server)
        if gene_name not in omnigene_dict:
            gene_description:str = edit['description']
            s = create_omni_gene(edit['gene'],gene_description,editor_id,jax_gene_dict,PMID_extractor,PubMed_extractor,reference_dict,journals_dict,authors_dict,hgnc_gene_name_dict)
            print(s)
            send_mutation(s,server)
        else:
            item = omnigene_dict[gene_name]
            s = write_new_gene_description(item['id'],item['statement'],item['field'],edit['description'], editor_id,PMID_extractor,reference_dict,journals_dict,authors_dict)
            print(s)
            send_mutation(s,server)
        print()



