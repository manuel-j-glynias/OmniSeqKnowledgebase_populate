import csv
import datetime
import mysql.connector
from mysql.connector import Error

from graphql_utils import send_query


def get_current_data(server:str)->list:
    query = '''
{
  OmniGene(orderBy: name_asc) {
    name
    geneDescription {
      ...es_fields
    }
    oncogenicCategory {
      ...es_fields
    }
    synonymsString {
      ...es_fields
    }
  }
}
fragment es_fields on EditableStatement {
  statement
  editor {
    name
  }
  edit_date
  references {
    ... on LiteratureReference {
      PMID
      DOI
      title
      journal {
        name
      }
      volume
      first_page
      last_page
      publication_Year
      abstract
      authors {
        surname
        first_initial
      }
    }
  }
}
    '''

    response = send_query(query, server)
    return response['data']['OmniGene']

def get_current_data_fields(server:str)->list:
    query = '''
{
  OmniGene(orderBy: name_asc) {
    name
    geneDescription {
      field
    }
    oncogenicCategory {
      field
    }
    synonymsString {
      field
    }
  }
}
    '''
    response = send_query(query, server)
    return response['data']['OmniGene']

def get_history(server:str)->list:
    query = f'''{{EditableStatement{{
    field
    statement
    edit_date
    editor{{
      name
    }}
  }}
}}'''
    response = send_query(query, server)
    return response['data']['EditableStatement']


def write_descriptions(descriptions:list):
    csv_file = "out/descriptions.csv"
    csv_columns = ['gene_name','gene_description','editor','edit_date','references']
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in descriptions:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def write_oncogenic_categories(oncogenic_categories:list):
    csv_file = "out/oncogenic_categories.csv"
    csv_columns = ['gene_name','oncogenicCategory','editor','edit_date']
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in oncogenic_categories:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def write_synonyms(synonyms:list):
    csv_file = "out/synonyms.csv"
    csv_columns = ['gene_name','synonymsString','editor','edit_date']
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in synonyms:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def write_references(references:list):
    csv_file = "out/references.csv"
    csv_columns = ['PMID', 'DOI', 'title','journal_name','volume','first_page','last_page','publication_Year', 'authors_names']
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, extrasaction='ignore')
            writer.writeheader()
            for data in references:
                writer.writerow(data)
    except IOError:
        print("I/O error")



def write_history(history_list:list):
    csv_file = "out/history.csv"
    csv_columns = ['gene_name', 'kind', 'editor_name', 'edit_date', 'statement']
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, extrasaction='ignore')
            writer.writeheader()
            for data in history_list:
                writer.writerow(data)
    except IOError:
        print("I/O error")

# 'geneDescription_omnigene_7249'

def convert_field(field:str):
    f = 'GeneDescription'
    if 'SynonymsString' in field:
        f = 'SynonymsString'
    elif 'OncogenicCategory' in field:
        f = 'OncogenicCategory'
    return f


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

# gene_name,oncogenicCategory,editor,edit_date
def create_oncogenic_categories_table(my_cursor):
    table_name = 'oncogenic_categories'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE oncogenic_categories ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'gene_name varchar(250) NOT NULL, ' \
                                   'oncogenic_category varchar(250), ' \
                                   'editor varchar(250), ' \
                                   'edit_date_string  varchar(250), ' \
                                   'edited_date DATETIME, ' \
                                   'PRIMARY KEY (id)' \
                                   ')'

        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_oncogenic_category(my_db,my_cursor,gene_name,oncogenic_category,editor,edit_date_string,edited_date):

    mySql_insert_query = f"INSERT INTO oncogenic_categories (gene_name, oncogenic_category,editor, edit_date_string,edited_date) " \
                         f"VALUES ('{gene_name}', '{oncogenic_category}','{editor}','{edit_date_string}','{edited_date}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    print("Record inserted successfully into oncogenic_categories table")

# gene_name,synonymsString,editor,edit_date
def create_synonyms_table(my_cursor):
    table_name = 'synonyms'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE synonyms ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'gene_name varchar(250) NOT NULL, ' \
                                   'synonym varchar(250), ' \
                                   'editor varchar(250), ' \
                                   'edit_date_string  varchar(250), ' \
                                    'edited_date DATETIME, ' \
                                  'PRIMARY KEY (id)' \
                                   ')'

        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_synonym(my_db,my_cursor,gene_name,synonym,editor,edit_date_string,edited_date):

    mySql_insert_query = f"INSERT INTO synonyms (gene_name, synonym,editor, edit_date_string,edited_date) " \
                         f"VALUES ('{gene_name}', '{synonym}','{editor}','{edit_date_string}','{edited_date}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    print("Record inserted successfully into synonyms table")


def create_descriptions_table(my_cursor):
    table_name = 'descriptions'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE descriptions ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'gene_name varchar(250) NOT NULL, ' \
                                   'description varchar(8000), ' \
                                   'editor varchar(250), ' \
                                   'edit_date_string  varchar(250), ' \
                                    'edited_date DATETIME, ' \
                                  'PRIMARY KEY (id)' \
                                   ')'

        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_description(my_db,my_cursor,gene_name,description,editor,edit_date_string,edited_date):
    description = description.replace("'","")
    mySql_insert_query = f"INSERT INTO descriptions (gene_name, description,editor, edit_date_string,edited_date) " \
                         f"VALUES ('{gene_name}', '{description}','{editor}','{edit_date_string}','{edited_date}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    print("Record inserted successfully into descriptions table")

# PMID,DOI,title,journal_name,volume,first_page,last_page,publication_Year,authors_names
def create_references_table(my_cursor):
    table_name = 'refs'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE refs ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'PMID varchar(250) NOT NULL, ' \
                                   'DOI varchar(250), ' \
                                   'title varchar(250), ' \
                                   'journal_name  varchar(250), ' \
                                    'volume  varchar(250), ' \
                                   'first_page  varchar(250), ' \
                                   'last_page  varchar(250), ' \
                                   'publication_Year  varchar(250), ' \
                                   'authors_names  varchar(250), ' \
                                 'PRIMARY KEY (id)' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')


def insert_reference(my_db,my_cursor,PMID,DOI,title,journal_name,volume,first_page,last_page,publication_Year,authors_names):
    title = title.replace("'","")

    mySql_insert_query = f"INSERT INTO refs (PMID,DOI,title,journal_name,volume,first_page,last_page,publication_Year,authors_names) " \
                         f"VALUES ('{PMID}', '{DOI}','{title}','{journal_name}','{volume}','{first_page}','{last_page}','{publication_Year}','{authors_names}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    print("Record inserted successfully into references table")


def get_id_from_pmid(pmid,my_cursor):
    id = None
    try:
        where_clase = f"WHERE refs.PMID='{pmid}' "
        query = 'SELECT refs.id  FROM refs ' + where_clase
        my_cursor.execute(query)
        row = my_cursor.fetchone()
        if row is not None:
            id = row[0]
    except mysql.connector.Error as error:
        print("Failed in MySQL: {}".format(error))
    return id


def get_id_from_gene_name(gene_name,my_cursor):
    id = None
    try:
        where_clase = f"WHERE descriptions.gene_name='{gene_name}' "
        query = 'SELECT descriptions.id  FROM descriptions ' + where_clase
        my_cursor.execute(query)
        row = my_cursor.fetchone()
        if row is not None:
            id = row[0]
    except mysql.connector.Error as error:
        print("Failed in MySQL: {}".format(error))
    return id

def create_description_ref_table(my_cursor):
    table_name = 'description_ref'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE description_ref ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'description_id MEDIUMINT, ' \
                                   'ref_id MEDIUMINT, ' \
                                  'PRIMARY KEY (id), ' \
                                   'FOREIGN KEY (description_id) ' \
                                   'REFERENCES descriptions (id), ' \
                                   'FOREIGN KEY (ref_id) ' \
                                   'REFERENCES refs (id) ' \
                                   ')'
        print(mySql_Create_Table_Query)
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')



def insert_description_ref(my_db,my_cursor,description_id,ref_id):

    mySql_insert_query = f"INSERT INTO description_ref (description_id,ref_id) " \
                         f"VALUES ('{description_id}', '{ref_id}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    print("Record inserted successfully into description_ref table")

def create_history_table(my_cursor):
    table_name = 'history'
    if not does_table_exist(my_cursor, table_name):
        mySql_Create_Table_Query = 'CREATE TABLE history ( ' \
                                   'id MEDIUMINT NOT NULL AUTO_INCREMENT, ' \
                                   'gene_name varchar(250) NOT NULL, ' \
                                   'kind varchar(250), ' \
                                   'statement varchar(8000), ' \
                                   'editor varchar(250), ' \
                                   'edit_date_string  varchar(250), ' \
                                    'edited_date DATETIME, ' \
                                  'PRIMARY KEY (id)' \
                                   ')'
        result = my_cursor.execute(mySql_Create_Table_Query)
        print(f'{table_name} Table created successfully')

def insert_history(my_db,my_cursor,gene_name,kind,statement,editor,edit_date_string,edited_date):
    statement = statement.replace("'","")
    mySql_insert_query = f"INSERT INTO history (gene_name, kind, statement, editor, edit_date_string,edited_date) " \
                         f"VALUES ('{gene_name}', '{kind}', '{statement}','{editor}','{edit_date_string}','{edited_date}') "

    result = my_cursor.execute(mySql_insert_query)
    my_db.commit()
    print("Record inserted successfully into history table")


def extract_current_data(server:str,my_db,my_cursor):
    descriptions: list = []
    oncogenic_categories: list = []
    synonyms: list = []
    reference_dict: dict = {}
    response: list = get_current_data(server)
    for entry in response:
        # print(entry)
        handle_gene_descriptions(descriptions, entry, reference_dict,my_db,my_cursor)

        handle_categories(entry, oncogenic_categories,my_db,my_cursor)

        handle_synonyms(entry, synonyms,my_db,my_cursor)
    write_descriptions(descriptions)
    write_oncogenic_categories(oncogenic_categories)
    write_synonyms(synonyms)
    write_references(reference_dict.values())


def handle_synonyms(entry, synonyms,my_db,my_cursor):
    synonym_entry = entry['synonymsString']
    editor = synonym_entry['editor']['name']
    edit_date = synonym_entry['edit_date']
    date_time_obj = datetime.datetime.strptime(edit_date, '%Y-%m-%d-%H-%M-%S-%f')
    synonym: dict = {'gene_name': entry['name'], 'synonymsString': synonym_entry['statement'], 'editor': editor,
                     'edit_date': edit_date}
    syn_list = synonym_entry['statement'].split(',')
    for syn in syn_list:
        insert_synonym(my_db, my_cursor, entry['name'], syn, editor, edit_date,date_time_obj)
    # print(synonym)
    synonyms.append(synonym)


def handle_categories(entry, oncogenic_categories,my_db,my_cursor):
    category = entry['oncogenicCategory']
    editor = category['editor']['name']
    edit_date = category['edit_date']
    date_time_obj = datetime.datetime.strptime(edit_date, '%Y-%m-%d-%H-%M-%S-%f')
    oncogenic_category: dict = {'gene_name': entry['name'], 'oncogenicCategory': category['statement'],
                                'editor': editor, 'edit_date': edit_date}
    insert_oncogenic_category(my_db,my_cursor,entry['name'],category['statement'],editor,edit_date,date_time_obj)
    oncogenic_categories.append(oncogenic_category)


def handle_gene_descriptions(descriptions, entry, reference_dict,my_db,my_cursor):
    gene_description: dict = entry['geneDescription']
    editor = gene_description['editor']['name']
    edit_date = gene_description['edit_date']
    date_time_obj = datetime.datetime.strptime(edit_date, '%Y-%m-%d-%H-%M-%S-%f')
    references = gene_description['references']
    pmids: list = []
    description: dict = {'gene_name': entry['name'], 'gene_description': gene_description['statement'],
                         'editor': editor, 'edit_date': edit_date, 'references': pmids}
    insert_description(my_db,my_cursor,entry['name'],gene_description['statement'],editor,edit_date,date_time_obj)
    description_id = get_id_from_gene_name(entry['name'],my_cursor)
    print(description_id, entry['name'])

    for ref in references:
        if 'PMID' in ref:
            pmids.append(ref['PMID'])
            if ref['PMID'] not in reference_dict:
                ref['journal_name'] = ref['journal']['name']
                authors_names = ''
                if 'authors' in ref:
                    if len(ref['authors']) > 2:
                        authors_names = ref['authors'][0]['surname'] + ' et al.'
                    elif len(ref['authors']) == 2:
                        authors_names = ref['authors'][0]['surname'] + ' & ' + ref['authors'][1]['surname']
                    else:
                        authors_names = ref['authors'][0]['surname']
                ref['authors_names'] = authors_names
                insert_reference(my_db, my_cursor, ref['PMID'], ref['DOI'], ref['title'], ref['journal_name'], ref['volume'], ref['first_page'], ref['last_page'],
                                 ref['publication_Year'], ref['authors_names'])
                reference_dict[ref['PMID']] = ref

            ref_id = get_id_from_pmid(ref['PMID'],my_cursor)
            print(ref_id,ref['PMID'])
            insert_description_ref(my_db,my_cursor,description_id,ref_id)

    descriptions.append(description)

def extract_history(server:str,my_db,my_cursor):
    response = get_current_data_fields(server)
    history_list:list = []
    gene_dict = {}

    for entry in response:
        gene_description: dict = entry['geneDescription']
        oncogenicCategory: dict = entry['oncogenicCategory']
        synonymsString: dict = entry['synonymsString']
        field = gene_description['field']
        gene_dict[field] = entry['name']
        field = oncogenicCategory['field']
        gene_dict[field] = entry['name']
        field = synonymsString['field']
        gene_dict[field] = entry['name']

    history_response = get_history(server)
    for h_item in history_response:
        field = h_item['field']
        if field in gene_dict:
            gene = gene_dict[field]
            kind = convert_field(field)
            editor_name = h_item['editor']['name']
            history = {'gene_name': gene, 'kind':kind, 'statement':h_item['statement'], 'editor_name':editor_name, 'edit_date': h_item['edit_date']}
            # csv_columns = ['gene_name', 'kind', 'editor_name', 'edit_date', 'statement']
            edit_date = h_item['edit_date']
            date_time_obj = datetime.datetime.strptime(edit_date, '%Y-%m-%d-%H-%M-%S-%f')
            insert_history(my_db, my_cursor, gene, kind, h_item['statement'], editor_name, edit_date, date_time_obj)
            history_list.append(history)
    write_history(history_list)

def main():
    # server:str = 'localhost'
    server: str = '165.227.89.140'
    my_db = None
    my_cursor = None
    try:
        my_db = get_db_connection()
        my_cursor = my_db.cursor(buffered=True)
        drop_database(my_cursor,'OmniSeqKnowledgebase')
        create_and_select_database(my_cursor, 'OmniSeqKnowledgebase')
        create_oncogenic_categories_table(my_cursor)
        create_synonyms_table(my_cursor)
        create_descriptions_table(my_cursor)
        create_references_table(my_cursor)
        create_description_ref_table(my_cursor)
        create_history_table(my_cursor)

        extract_current_data(server,my_db,my_cursor)
        extract_history(server,my_db,my_cursor)
    except mysql.connector.Error as error:
        print("Failed in MySQL: {}".format(error))
    finally:
        if (my_db.is_connected()):
            my_cursor.close()



if __name__ == "__main__":
    main()
