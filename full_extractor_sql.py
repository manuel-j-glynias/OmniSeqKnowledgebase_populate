import csv
import datetime
import mysql.connector
from mysql.connector import Error

from graphql_utils import send_query

def get_current_author_data(server:str)->list:
    query = '{Author { id, surname, first_initial } }'

    response = send_query(query, server)
    return response['data']['Author']

def get_current_journal_data(server:str)->list:
    query = '{ Journal { id,name } }'

    response = send_query(query, server)
    return response['data']['Journal']

def get_current_literature_reference_data(server:str)->list:
    query = '{ LiteratureReference { id, PMID,DOI,title,journal{id},volume,first_page,last_page,publication_Year,shortReference,abstract,authors {id}} }'

    response = send_query(query, server)
    return response['data']['LiteratureReference']

def get_current_internet_reference_data(server:str)->list:
    query = '{ InternetReference { id, accessed_date,web_address,shortReference} }'

    response = send_query(query, server)
    return response['data']['InternetReference']


def get_current_user_data(server:str)->list:
    query = '{ User {id, name, password, isAdmin } }'

    response = send_query(query, server)
    return response['data']['User']

def get_current_editable_statement_data(server:str)->list:
    query = '{ EditableStatement { id, field, statement, edit_date,  deleted, editor { id }, references { id, __typename } } }'
    response = send_query(query, server)
    return response['data']['EditableStatement']

def get_current_jax_gene_data(server:str)->list:
    query = '{ JaxGene { id, name, canonicalTranscript, chromosome, entrezId, jaxId, synonyms, description { id } } }'
    response = send_query(query, server)
    return response['data']['JaxGene']

def get_current_myGene_info_gene_data(server:str)->list:
    query = '{ MyGeneInfo_Gene {id, name, chromosome, strand, start, end, entrezId, description { id }}}'
    response = send_query(query, server)
    return response['data']['MyGeneInfo_Gene']


def get_current_uniprot_entry_data(server:str)->list:
    query = '{ Uniprot_Entry {id, name,  accessionNumber, uniprot_id, function { id }, gene { id} }}'
    response = send_query(query, server)
    return response['data']['Uniprot_Entry']


def get_current_omnigene_data(server:str)->list:
    query = '{ OmniGene {id, name, panelName, geneDescription {id}, oncogenicCategory {id }, synonymsString {id }, myGeneInfoGene {id}, jaxGene {id}, uniprot_entry { id }} }'
    response = send_query(query, server)
    return response['data']['OmniGene']


def get_db_connection():
    my_db = mysql.connector.connect(
        host="localhost",
        user="python_user",
        passwd="Omni2020"
    )
    return my_db

def drop_database(my_cursor,db_name):
    if does_db_exist(my_cursor,db_name):
        my_cursor.execute('DROP DATABASE ' + db_name)

def create_and_select_database(my_cursor, db_name):
    if not does_db_exist(my_cursor, db_name):
        my_cursor.execute('CREATE DATABASE ' + db_name)
        print(f"{db_name} Database created successfully")
    my_cursor.execute('USE ' + db_name)


def does_db_exist(my_cursor,db_name):
    exists = False
    my_cursor.execute("SHOW DATABASES")
    for x in my_cursor:
        if x[0] == db_name:
            exists = True
            break
    return exists

def does_table_exist(my_cursor,table_name):
    exists = False
    my_cursor.execute("SHOW TABLES")
    for x in my_cursor:
        if x[0] == table_name:
            exists = True
            break
    return exists



def create_authors_table(my_cursor):
    table_name = 'authors'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE authors ( ' \
                                   'surname varchar(250) NOT NULL, ' \
                                   'first_initial varchar(100), ' \
                                   'graph_id varchar(100), ' \
                                  'PRIMARY KEY (graph_id)' \
                                   ')'
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

# sql = "INSERT INTO TABLE_A (COL_A,COL_B) VALUES (%s, %s)"
# cursor.execute(sql, (val1, val2))
def insert_author(my_db,my_cursor,surname,first_initial,graph_id):
    # mySql_insert_query = f"INSERT INTO authors (surname, first_initial, graph_id) " \
    #                      f"VALUES ('{surname}', '{first_initial}', '{graph_id}') "
    #
    # result = my_cursor.execute(mySql_insert_query)
    mySql_insert_query = "INSERT IGNORE INTO authors (surname, first_initial, graph_id) VALUES (%s, %s, %s)"
    result = my_cursor.execute(mySql_insert_query, (surname,first_initial,graph_id))
    my_db.commit()
    # print("Record inserted successfully into authors table")

def create_journals_table(my_cursor):
    table_name = 'journals'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE journals ( ' \
                                   'name varchar(250) NOT NULL, ' \
                                   'graph_id varchar(100), ' \
                                  'PRIMARY KEY (graph_id)' \
                                   ')'
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_journal(my_db,my_cursor,name,graph_id):
    mySql_insert_query = "INSERT INTO journals (name, graph_id) VALUES (%s, %s)"
    result = my_cursor.execute(mySql_insert_query,(name,graph_id))
    my_db.commit()
    # print("Record inserted successfully into journals table")


def create_references_table(my_cursor):
    table_name = 'refs'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE refs ( ' \
                                   'PMID varchar(20) NOT NULL, ' \
                                   'DOI varchar(100), ' \
                                   'title varchar(1000), ' \
                                   'journal_graph_id varchar(100), ' \
                                   'volume  varchar(20), ' \
                                   'first_page  varchar(20), ' \
                                   'last_page  varchar(20), ' \
                                   'publication_Year  varchar(20), ' \
                                   'short_reference varchar(200), ' \
                                   'abstract  varchar(8000), ' \
                                   'graph_id varchar(100) PRIMARY KEY, ' \
                                   'CONSTRAINT refs_fk_journal_graph_id FOREIGN KEY (journal_graph_id) REFERENCES journals (graph_id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_reference(my_db,my_cursor,PMID,DOI,title,journal_graph_id,volume,first_page,last_page,publication_Year,short_reference,abstract,graph_id):
    mySql_insert_query = "INSERT INTO refs (PMID,DOI,title,journal_graph_id,volume,first_page,last_page,publication_Year,short_reference,abstract,graph_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(PMID,DOI,title,journal_graph_id,volume,first_page,last_page,publication_Year,short_reference,abstract,graph_id))
    my_db.commit()
    # print("Record inserted successfully into references table")

def create_author_ref_table(my_cursor):
    table_name = 'author_ref'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE author_ref ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'author_id varchar(100), ' \
                                   'ref_id varchar(100), ' \
                                  'PRIMARY KEY (id), ' \
                                   'FOREIGN KEY (author_id) ' \
                                   'REFERENCES authors (graph_id), ' \
                                   'FOREIGN KEY (ref_id) ' \
                                   'REFERENCES refs (graph_id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_author_ref(my_db,my_cursor,author_id,ref_id):

    mySql_insert_query = f"INSERT INTO author_ref (author_id,ref_id) " \
                         f"VALUES ('{author_id}', '{ref_id}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    # print("Record inserted successfully into author_ref table")

#    query = '{ InternetReference { id, accessed_date,web_address,shortReference} }'
def create_internet_references_table(my_cursor):
    table_name = 'internet_refs'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE internet_refs ( ' \
                                   'accessed_date varchar(100), ' \
                                   'web_address varchar(100), ' \
                                   'short_reference varchar(200), ' \
                                   'graph_id varchar(100) PRIMARY KEY ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_internet_reference(my_db,my_cursor,accessed_date,web_address,short_reference,graph_id):
    mySql_insert_query = "INSERT IGNORE INTO internet_refs (accessed_date,web_address,short_reference,graph_id) VALUES (%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(accessed_date,web_address,short_reference,graph_id))
    my_db.commit()
    print("Record inserted successfully into internet references table")

def create_user_table(my_cursor):
    table_name = 'users'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE users ( ' \
                                   'name varchar(100), ' \
                                   'password varchar(100), ' \
                                   'isAdmin varchar(50), ' \
                                   'graph_id varchar(100) PRIMARY KEY ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_user(my_db,my_cursor,name,password,isAdmin,graph_id):
    mySql_insert_query = "INSERT INTO users (name,password,isAdmin,graph_id) VALUES (%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(name,password,isAdmin,graph_id))
    my_db.commit()

#     query = '{ EditableStatement { id, field, statement, edit_date,  deleted, editor { id }, references { id } } }'
def create_editable_statement_table(my_cursor):
    table_name = 'editable_statements'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE editable_statements ( ' \
                                   'field varchar(100), ' \
                                   'statement varchar(8000), ' \
                                   'edit_date varchar(50), ' \
                                   'editor_id varchar(100), ' \
                                   'deleted varchar(50), ' \
                                   'graph_id varchar(100) PRIMARY KEY, ' \
                                    'CONSTRAINT es_fk_editor_id FOREIGN KEY (editor_id) REFERENCES users (graph_id) ' \
                                  ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_editable_statement(my_db,my_cursor,field, statement, edit_date,editor_id,deleted,graph_id):
    mySql_insert_query = "INSERT INTO editable_statements (field,statement,edit_date,editor_id,deleted,graph_id) VALUES (%s,%s,%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(field, statement, edit_date,editor_id,deleted,graph_id))
    my_db.commit()


def create_es_ref_table(my_cursor):
    table_name = 'es_ref'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE es_ref ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'es_id varchar(100), ' \
                                   'ref_id varchar(100), ' \
                                  'PRIMARY KEY (id), ' \
                                   'FOREIGN KEY (es_id) ' \
                                   'REFERENCES editable_statements (graph_id), ' \
                                   'FOREIGN KEY (ref_id) ' \
                                   'REFERENCES refs (graph_id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_es_ref(my_db,my_cursor,es_id,ref_id):

    mySql_insert_query = f"INSERT INTO es_ref (es_id,ref_id) " \
                         f"VALUES ('{es_id}', '{ref_id}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()



def create_es_internet_refs_table(my_cursor):
    table_name = 'es_internet_refs'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE es_internet_refs ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'es_id varchar(100), ' \
                                   'internet_ref_id varchar(100), ' \
                                  'PRIMARY KEY (id), ' \
                                   'FOREIGN KEY (es_id) ' \
                                   'REFERENCES editable_statements (graph_id), ' \
                                   'FOREIGN KEY (internet_ref_id) ' \
                                   'REFERENCES internet_refs (graph_id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_es_internet_refs(my_db,my_cursor,es_id,internet_ref_id):

    mySql_insert_query = f"INSERT INTO es_internet_refs (es_id,internet_ref_id) " \
                         f"VALUES ('{es_id}', '{internet_ref_id}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()

def create_jax_gene_table(my_cursor):
    table_name = 'jax_gene'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE jax_gene ( ' \
                                   'name varchar(100), ' \
                                   'canonicalTranscript varchar(50), ' \
                                   'chromosome varchar(50), ' \
                                   'entrezId varchar(50), ' \
                                   'jaxId varchar(50), ' \
                                    'description_Id varchar(50), ' \
                                  'graph_id varchar(100) PRIMARY KEY, ' \
                                    'CONSTRAINT jax_description_fk_es_id FOREIGN KEY (description_Id) REFERENCES editable_statements (graph_id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_jax_gene(my_db,my_cursor,name,canonicalTranscript,chromosome,entrezId,jaxId,description_id,graph_id):
    mySql_insert_query = "INSERT INTO jax_gene (name,canonicalTranscript,chromosome,entrezId,jaxId,description_id,graph_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(name,canonicalTranscript,chromosome,entrezId,jaxId,description_id,graph_id))
    my_db.commit()

def create_jax_synonym_table(my_cursor):
    table_name = 'jax_synonyms'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE jax_synonyms ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'name varchar(100) NOT NULL, ' \
                                   'jax_gene_id varchar(100), ' \
                                  'PRIMARY KEY (id),' \
                                   'CONSTRAINT jax_synonym_fk_gene_id FOREIGN KEY (jax_gene_id) REFERENCES jax_gene (graph_id) ' \
                                   ')'
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_jax_synonym(my_db,my_cursor,name,jax_gene_id):
    mySql_insert_query = "INSERT INTO jax_synonyms (name, jax_gene_id) VALUES (%s, %s)"
    result = my_cursor.execute(mySql_insert_query,(name,jax_gene_id))
    my_db.commit()

def create_mygene_info_gene_table(my_cursor):
    table_name = 'mygene_info_gene'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE mygene_info_gene ( ' \
                                   'name varchar(100), ' \
                                   'chromosome varchar(20), ' \
                                   'strand varchar(10), ' \
                                   'start_pos varchar(10), ' \
                                   'end_pos varchar(10), ' \
                                   'entrezId varchar(50), ' \
                                    'description_Id varchar(50), ' \
                                  'graph_id varchar(100) PRIMARY KEY, ' \
                                    'CONSTRAINT mgi_description_fk_es_id FOREIGN KEY (description_Id) REFERENCES editable_statements (graph_id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_mygene_info_gene(my_db,my_cursor,name,chromosome,strand, start, end, entrezId,description_id,graph_id):
    mySql_insert_query = "INSERT IGNORE INTO mygene_info_gene (name,chromosome,strand, start_pos, end_pos, entrezId,description_id,graph_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(name,chromosome,strand, str(start), str(end),entrezId,description_id,graph_id))
    my_db.commit()


def create_uniprot_entry_table(my_cursor):
    table_name = 'uniprot_entry'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE uniprot_entry ( ' \
                                   'name varchar(100), ' \
                                   'accessionNumber varchar(100), ' \
                                   'uniprot_id varchar(100), ' \
                                     'function_Id varchar(50), ' \
                                     'gene_Id varchar(50), ' \
                                  'graph_id varchar(100) PRIMARY KEY, ' \
                                    'CONSTRAINT function_fk_es_id FOREIGN KEY (function_Id) REFERENCES editable_statements (graph_id), ' \
                                     'CONSTRAINT uniprot_fk_gene_id FOREIGN KEY (gene_Id) REFERENCES mygene_info_gene (graph_id) ' \
                                  ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_uniprot_entry(my_db,my_cursor,name,accessionNumber,uniprot_id,function_id,gene_id,graph_id):
    mySql_insert_query = "INSERT IGNORE INTO uniprot_entry (name,accessionNumber,uniprot_id,function_id,gene_id,graph_id) VALUES (%s,%s,%s,%s,%s,%s)"
    result = my_cursor.execute(mySql_insert_query,(name,accessionNumber,uniprot_id,function_id,gene_id,graph_id))
    my_db.commit()


#     query = '{ OmniGene {id, name, panelName, geneDescription {id}, oncogenicCategory {id }, synonymsString {id }, myGeneInfoGene {id}, jaxGene {id}, uniprot_entry { id }} }'
def create_omnigene_table(my_cursor):
    table_name = 'omnigene'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE omnigene ( ' \
                                   'name varchar(100), ' \
                                   'panelName varchar(100), ' \
                                   'geneDescription_id varchar(100), ' \
                                     'oncogenicCategory_Id varchar(100), ' \
                                     'synonymsString_Id varchar(100), ' \
                                      'myGeneInfo_gene_Id varchar(100), ' \
                                      'jaxGene_gene_Id varchar(100), ' \
                                     'uniprot_entry_Id varchar(100), ' \
                                'graph_id varchar(100) PRIMARY KEY, ' \
                                    'CONSTRAINT geneDescription_fk_es_id FOREIGN KEY (geneDescription_id) REFERENCES editable_statements (graph_id), ' \
                                    'CONSTRAINT oncogenicCategory_fk_es_id FOREIGN KEY (oncogenicCategory_Id) REFERENCES editable_statements (graph_id), ' \
                                    'CONSTRAINT synonymsString_fk_es_id FOREIGN KEY (synonymsString_Id) REFERENCES editable_statements (graph_id), ' \
                                     'CONSTRAINT omni_fk_mygene FOREIGN KEY (myGeneInfo_gene_Id) REFERENCES mygene_info_gene (graph_id), ' \
                                     'CONSTRAINT omni_fk_jax FOREIGN KEY (jaxGene_gene_Id) REFERENCES jax_gene (graph_id), ' \
                                     'CONSTRAINT omni_fk_uniprot FOREIGN KEY (uniprot_entry_Id) REFERENCES uniprot_entry (graph_id) ' \
                                  ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_omnigene_entry(my_db,my_cursor,name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_Id,jaxGene_Id,uniprot_id,graph_id):
    if uniprot_id == '' and jaxGene_Id=='':
        mySql_insert_query = "INSERT INTO omnigene (name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_gene_Id,jaxGene_gene_Id,uniprot_entry_Id,graph_id) VALUES (%s,%s,%s,%s,%s,%s,NULL,NULL,%s)"
        result = my_cursor.execute(mySql_insert_query, (name, panelName, geneDescription_id, oncogenicCategory_Id, synonymsString_Id, myGeneInfo_Id, graph_id))
    elif uniprot_id=='':
        mySql_insert_query = "INSERT INTO omnigene (name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_gene_Id,jaxGene_gene_Id,uniprot_entry_Id,graph_id) VALUES (%s,%s,%s,%s,%s,%s,%s,NULL,%s)"
        result = my_cursor.execute(mySql_insert_query,(name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_Id,jaxGene_Id,graph_id))
    elif jaxGene_Id=='':
        mySql_insert_query = "INSERT INTO omnigene (name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_gene_Id,jaxGene_gene_Id,uniprot_entry_Id,graph_id) VALUES (%s,%s,%s,%s,%s,%s,NULL,%s,%s)"
        result = my_cursor.execute(mySql_insert_query,(name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_Id,uniprot_id,graph_id))
    else:
        mySql_insert_query = "INSERT IGNORE INTO omnigene (name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_gene_Id,jaxGene_gene_Id,uniprot_entry_Id,graph_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        result = my_cursor.execute(mySql_insert_query,(name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_Id,jaxGene_Id,uniprot_id,graph_id))
    my_db.commit()

def get_id_helper(obj,key):
    val = ''
    if key in obj:
        obj2 = obj[key]
        if obj2 != None and 'id' in obj2:
            val = obj2['id']
    return val


def main():
    server_read: str = '165.227.89.140'
    my_db = None
    my_cursor = None
    try:
        my_db = get_db_connection()
        my_cursor = my_db.cursor(buffered=True)

        # my_cursor.execute('USE ' + 'OmniSeqKnowledgebase')
        # my_cursor.execute('DROP TABLE ' + 'omnigene')
        drop_database(my_cursor, 'OmniSeqKnowledgebase')
        create_and_select_database(my_cursor, 'OmniSeqKnowledgebase')

        create_authors_table(my_cursor)
        create_journals_table(my_cursor)
        create_references_table(my_cursor)
        create_author_ref_table(my_cursor)
        create_internet_references_table(my_cursor)
        create_user_table(my_cursor)
        create_editable_statement_table(my_cursor)
        create_es_ref_table(my_cursor)
        create_es_internet_refs_table(my_cursor)
        create_jax_gene_table(my_cursor)
        create_jax_synonym_table(my_cursor)
        create_mygene_info_gene_table(my_cursor)
        create_uniprot_entry_table(my_cursor)
        create_omnigene_table(my_cursor)

        counter = 0
        print('authors')
        for author in get_current_author_data(server_read):
            # print(author)
            insert_author(my_db,my_cursor,author['surname'], author['first_initial'], author['id'])
            counter += 1
            if (counter % 1000==0):
                print(counter)


        print('journals')
        for journal in get_current_journal_data(server_read):
            # print(journal)
            insert_journal(my_db,my_cursor,journal['name'],journal['id'])

        counter = 0
        print('references')
        for reference in get_current_literature_reference_data(server_read):
            # print(reference)
            insert_reference(my_db,my_cursor,reference['PMID'], reference['DOI'],reference['title'],reference['journal']['id'],reference['volume'],reference['first_page'],
                             reference['last_page'],reference['publication_Year'],reference['shortReference'],reference['abstract'],reference['id'])
            for author in reference['authors']:
                author_id = author['id']
                insert_author_ref(my_db,my_cursor,author_id,reference['id'])
            counter += 1
            if (counter % 1000==0):
                print(counter)

        print('internet_references')
        for internet_reference in get_current_internet_reference_data(server_read):
            print(internet_reference)
            insert_internet_reference(my_db,my_cursor,internet_reference['accessed_date'], internet_reference['web_address'], internet_reference['shortReference'],internet_reference['id'])

        print('users')
        for user in get_current_user_data(server_read):
            print(user)
            isAdmin = 'TRUE'
            if user['isAdmin'] == False:
                isAdmin = 'FALSE'
            insert_user(my_db, my_cursor, user['name'], user['password'], isAdmin, user['id'])

        print('EditableStatements')
        for es in get_current_editable_statement_data(server_read):
            deleted = 'TRUE'
            if es['deleted'] == False:
                deleted = 'FALSE'
            insert_editable_statement(my_db, my_cursor,es['field'],es['statement'],es['edit_date'],es['editor']['id'],deleted,es['id'])
            for ref in es['references']:
                if ref['__typename'] == 'InternetReference':
                    insert_es_internet_refs(my_db, my_cursor,es['id'],ref['id'])
                else:
                    insert_es_ref(my_db, my_cursor,es['id'],ref['id'])

        print('JaxGenes')
        for jaxGene in get_current_jax_gene_data(server_read):
            transcript = jaxGene['canonicalTranscript'][0]
            if transcript=='None':
                transcript = ''
            insert_jax_gene(my_db, my_cursor, jaxGene['name'], transcript, jaxGene['chromosome'], jaxGene['entrezId'], jaxGene['jaxId'], jaxGene['description']['id'], jaxGene['id'])
            for syn in jaxGene['synonyms']:
                insert_jax_synonym(my_db, my_cursor, syn, jaxGene['id'])

        print('mygene_info_gene')
        for myGene in get_current_myGene_info_gene_data(server_read):
            insert_mygene_info_gene(my_db, my_cursor,myGene['name'],myGene['chromosome'],myGene['strand'],myGene['start'],myGene['end'],myGene['entrezId'],myGene['description']['id'],myGene['id'])

        print('uniprot_entry')
        for prot in get_current_uniprot_entry_data(server_read):
            insert_uniprot_entry(my_db, my_cursor,prot['name'],prot['accessionNumber'],prot['uniprot_id'],prot['function']['id'],prot['gene']['id'],prot['id'])

        print('omnigene')
        for omni in get_current_omnigene_data(server_read):
            print(omni)
            # def insert_omnigene_entry(my_db,my_cursor,name,panelName,geneDescription_id,oncogenicCategory_Id,synonymsString_Id,myGeneInfo_Id,jaxGene_Id,uniprot_id,graph_id):
            insert_omnigene_entry(my_db, my_cursor,omni['name'],omni['panelName'],get_id_helper(omni,'geneDescription'), get_id_helper(omni,'oncogenicCategory'),get_id_helper(omni,'synonymsString'),
                                  get_id_helper(omni,'myGeneInfoGene'),get_id_helper(omni,'jaxGene'),get_id_helper(omni,'uniprot_entry'),omni['id'])

    except mysql.connector.Error as error:
        print("Failed in MySQL: {}".format(error))
    finally:
        if (my_db.is_connected()):
            my_cursor.close()




if __name__ == "__main__":
    main()
