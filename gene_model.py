import os
import json
import csv

from informatics_utils import create_hgnc_gene_name_dict, fetch_gene_id_by_gene_name, fetch_gene_info_by_gene_id, \
    populate_omni_gene


from graphql_utils import erase_neo4j, write_users, send_mutation, get_editor_id, createEditableStatement, \
    create_jax_description, get_authors, get_journals, get_literature_references, PMID_extractor, get_jax_descriptions, \
    get_omnigenes, replace_characters, create_myGeneInfo_gene, create_uniprot_entry, create_omniGene, PubMed_extractor, \
    get_jax_gene_ids

JAX_PATH: str = '/Users/mglynias/jax_march_2020/api-export/'

def get_list_of_files(path: str) -> list:
    json_files = []
    for entry in os.scandir(path):
        if entry.is_file():
            json_files.append(entry.path)
    return json_files

def read_one_gene_jax_json(path) -> dict:
    gene_dict: dict = None
    with open(path, 'r') as afile:
        gene_data: dict = json.loads(afile.read())
        ckb_id: str = str(gene_data['id'])
        gene: str = str(gene_data['geneSymbol'])
        entrezId: str = str(gene_data['entrezId'])
        synonyms: list = gene_data['synonyms']
        chromosome: str = gene_data['chromosome']
        canonicalTranscript: str = gene_data['canonicalTranscript']
        if 'geneDescriptions' in gene_data:
            descriptions_array: list = gene_data['geneDescriptions']
            if len(descriptions_array)>0:
                description: str = replace_characters(descriptions_array[0]['description'])
                references: list = descriptions_array[0]['references']
                gene_dict = {'ckb_id': ckb_id,
                        'gene':gene,
                        'description': description,
                        # 'references': references,
                        'entrezId' :entrezId,
                        'synonyms': synonyms,
                        'canonicalTranscript': canonicalTranscript,
                        'chromosome': chromosome}
    return gene_dict

def get_gene_id_from_jax_id(jax_id:str)->str:
    return 'jax_gene_' +jax_id


def write_one_jax_gene(gene: dict,editor_id:str,pmid_extractor:callable,reference_dict:dict,journals_dict:dict,authors_dict:dict,omnigene_dict:dict)->str:
    id: str = get_gene_id_from_jax_id(str(gene['ckb_id']))
    synonyms: str = '['
    for syn in gene['synonyms']:
        synonyms += f'\\"{syn}\\",'
    synonyms += ']'

    gene_name = gene['gene']
    s = f'''{id} : createJaxGene(canonicalTranscript: \\"{gene['canonicalTranscript']}\\", chromosome: \\"{gene['chromosome']}\\",entrezId: \\"{gene['entrezId']}\\", id: \\"{id}\\", jaxId: \\"{gene['ckb_id']}\\", name: \\"{gene_name}\\", synonyms: {synonyms}),'''
    # statement: \\"{gene['description']}\\",
    field: str = 'geneDescription_' + id
    m, es_id= createEditableStatement(gene['description'],field,editor_id,pmid_extractor,reference_dict,journals_dict,authors_dict)
    s += m
    # addJaxGeneDescription(description: [ID!]!id: ID!): String
    s += f'addJaxGeneDescription(description:[\\"{es_id}\\"], id:\\"{id}\\"),'
    if gene_name in omnigene_dict:
        gene_id = omnigene_dict[gene_name]
        s += f'addOmniGeneJaxGene(id:\\"{gene_id}\\", jaxGene:[\\"{id}\\"] ),'

    return s
def write_jax_genes(server:str,reference_dict: dict,journal_dict: dict,author_dict: dict,auto_user_id:str,PMID_extractor:callable) -> None:
    # gene_categories = read_oncgenes_tumor_suppressors('data/OCP_oncogenes_tumorsuppressors.csv')
    json_files = get_list_of_files(JAX_PATH + 'genes')
    print('total=',len(json_files))
    count = 0
    last_good = -1
    for json_file in json_files:
        gene: dict = read_one_gene_jax_json(json_file)
        if gene is not None:
            if count > last_good:
                mutation_payload: str = ''
                # mutation_payload += write_one_jax_gene(gene,auto_user_id,gene_dict,reference_dict,journal_dict,author_dict,{})
                mutation_payload += write_one_jax_gene(gene,auto_user_id,PMID_extractor,reference_dict,journal_dict,author_dict,{})
                print(count,gene['gene'])
                send_mutation(mutation_payload, server)
            count += 1
        # if count > 100:
        #     break


def read_omni_genes(file_name: str)->list:
    gene_categories = []
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gene_data:dict = {'symbol':row['HGNC_Symbol'],
                              'category':row['GeneType'],
                              'category_source': row['GeneTypeSource']}

            gene_categories.append(gene_data)
    return gene_categories


def write_omni_genes(omini_genes:list, server:str,editor_id:str,jax_gene_dict,pmid_extractor:callable,sp_pmid_extractor:callable, reference_dict:dict,journal_dict:dict,author_dict:dict,hgnc_gene_name_dict)->None:
    hgnc_gene_name_dict = create_hgnc_gene_name_dict()
    for omni_gene in omini_genes:
        gene_name: str = omni_gene['symbol']

        omni_gene['panel_name'] = gene_name
        if gene_name in hgnc_gene_name_dict:
            omni_gene['panel_name'] = gene_name
            omni_gene['synonym'] = gene_name
            gene_name = hgnc_gene_name_dict[gene_name]
            omni_gene['symbol'] = gene_name
        entrez_gene_id = fetch_gene_id_by_gene_name(gene_name)
        omni_gene['entrez_gene_id'] = entrez_gene_id
        if entrez_gene_id is None:
            print("no entrz gene id for",gene_name)
        else:
            gene_info = fetch_gene_info_by_gene_id(entrez_gene_id)
            if 'genomic_pos_hg19' in gene_info:
                populate_omni_gene(gene_info, omni_gene)
                print(gene_name)
                s = create_myGeneInfo_gene(omni_gene, editor_id, pmid_extractor, reference_dict, journal_dict,
                                           author_dict)
                s += create_uniprot_entry(omni_gene, editor_id, sp_pmid_extractor, reference_dict, journal_dict,
                                          author_dict)
                s += create_omniGene(omni_gene, jax_gene_dict, omni_gene['summary'], editor_id, pmid_extractor,
                                     reference_dict, journal_dict, author_dict)
                send_mutation(s,server)
            else:
                print('no gene_info for',gene_name)


def build_initial_gene_model(server:str):
    # server:str = 'localhost'
    # server: str = '165.227.89.140'
    # schema__graphql = 'schema.graphql'

    users_dict = {'manuel.glynias@omniseq.com':'manuel',
                  'Carrie.Hoefer@omniseq.com':'carrie',
                  'Paul.DePietro@omniseq.com':'paul',
                  'Mary.Nesline@omniseq.com':'mary',
                  'loader':'loader',
                  'updater':'updater'
                  }

    # erase_neo4j(schema__graphql,server)
    write_users(users_dict,server)

    auto_user_id: str = get_editor_id('loader',server)
    print(auto_user_id)

    authors_dict = get_authors(server)
    reference_dict = get_literature_references(server)
    journals_dict = get_journals(server)
    hgnc_gene_name_dict = create_hgnc_gene_name_dict()


    write_jax_genes(server,reference_dict,journals_dict,authors_dict,auto_user_id,PMID_extractor)
    gene_dict = get_jax_gene_ids(server)
    omini_genes:list = read_omni_genes('data/tblOS_GLOBAL_GLOBAL_Ref_AllPanelsGenes.csv')
    write_omni_genes(omini_genes,server,auto_user_id,gene_dict,PMID_extractor,PubMed_extractor,reference_dict,journals_dict,authors_dict,hgnc_gene_name_dict)


