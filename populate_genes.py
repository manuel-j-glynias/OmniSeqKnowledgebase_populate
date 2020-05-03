from extractor_sql import extract_from_server
from gene_model import build_initial_gene_model
from graphql_utils import erase_neo4j
from jax_updater import update_jax
from update_curations import update


def main():
    schema__graphql = 'schema.graphql'
    server_write:str = 'localhost'
    # server_write: str = '165.227.89.140'
    server_read: str = '165.227.89.140'

    extract_from_server(server_read)

    erase_neo4j(schema__graphql, server_write)

    build_initial_gene_model(server_write)
    update_jax(server_write)
    update(server_write)



if __name__ == "__main__":
    main()