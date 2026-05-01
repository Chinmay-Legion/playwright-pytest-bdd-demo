"""Small helper functions shared by SauceDemo BDD step modules."""


def data_table_to_dicts(datatable: list[list[str]]) -> list[dict[str, str]]:
    """Convert a pytest-bdd data table into a list of row dictionaries."""

    headers = datatable[0]
    rows = datatable[1:]
    return [dict(zip(headers, row)) for row in rows]


def product_names_from_datatable(datatable: list[list[str]]) -> list[str]:
    """Read a one-column product_name data table into a simple product list."""

    return [row["product_name"] for row in data_table_to_dicts(datatable)]
