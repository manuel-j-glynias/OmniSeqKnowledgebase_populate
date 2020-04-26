
from gene_model import build_initial_gene_model
from graphql_utils import erase_neo4j
from jax_updater import update_jax
from update_curations import update


def main():
    schema__graphql = 'schema.graphql'
    server:str = 'localhost'
    # server: str = '165.227.89.140'

    erase_neo4j(schema__graphql, server)
    build_initial_gene_model(server)
    update_jax(server)
    # update(server)



if __name__ == "__main__":
    main()