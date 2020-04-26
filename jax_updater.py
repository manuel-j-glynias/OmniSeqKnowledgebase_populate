
from gene_model import get_list_of_files, read_one_gene_jax_json, get_gene_id_from_jax_id
from graphql_utils import send_mutation,get_editor_id,createEditableStatement, create_jax_description,get_authors,get_journals,get_literature_references,PMID_extractor,get_jax_descriptions,get_omnigenes


JAX_PATH: str = '/Users/mglynias/jax_april_2020/api-export/'



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

def update_jax(server:str):
    # server:str = 'localhost'
    # server: str = '165.227.89.140'
    editor = 'updater'
    editor_id = get_editor_id(editor,server)
    print(editor_id)

    jax_dict = get_jax_descriptions(server)
    authors_dict = get_authors(server)
    reference_dict = get_literature_references(server)
    journals_dict = get_journals(server)
    omnigene_dict = get_omnigenes(server)

    json_files = get_list_of_files(JAX_PATH + 'genes')
    print('total=',len(json_files))
    change_count = 0
    new_count = 0
    for json_file in json_files:
        jax: dict = read_one_gene_jax_json(json_file)
        if jax is not None:
            gene = jax['gene']
            description = jax['description']
            if gene in jax_dict:
                item = jax_dict[gene]
                statement = item['statement']
                if description != statement:
                    change_count += 1
                    print(change_count, 'description changed for', gene)
                    print('new:' + description)
                    print('old:' + statement)
                    # pmid_extractor:callable,reference_dict:dict,journal_dict:dict,author_dict:dict
                    s = create_jax_description(item['id'],item['field'],description,editor_id,PMID_extractor,reference_dict,journals_dict,authors_dict)
                    print(s)
                    send_mutation(s, server)
                    print()
            else:
                new_count += 1
                print(new_count, '***new entry',gene)
                s = write_one_jax_gene(jax,editor_id,PMID_extractor,reference_dict,journals_dict,authors_dict,omnigene_dict)
                print(s)
                send_mutation(s, server)
                print()



