from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


class GQLClient():
    """
    A small wrapper class to make executing GraphQL queries and mutations from files easier.

    Args:
        gql_endpoint: The URI of the GraphQL endpoint the user needs to query.
    
    Attributes:
        transport: A RequestsHTTPTransport object from the 'gql' library.
        client: A Client object from the 'gql' library.

    """

    def __init__(self, gql_endpoint):
        self.transport = RequestsHTTPTransport(
            url=gql_endpoint,
            use_json=True,
            headers={
                "Content-type": "application/json",
            },
            verify=False,
            retries=3,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

    def execute(self, filepath: str, variables: dict):
        """
        A method to execute a GraphQL query or mutation from a file.

        Args:
            filepath: The path to where a query/mutation is saved.
            variables: A map of variable names and values to be inserted into the query.

        Returns:
            The response object of GraphQL command request.
        """
        file = open(filepath, "r")
        command = gql(file.read().rstrip())
        return self.client.execute(command, variable_values=variables)