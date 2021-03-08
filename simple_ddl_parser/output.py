import os
import json
from typing import Dict, List


def add_alter_to_table(tables_dict: Dict, statement: Dict) -> Dict:
    table_id = (statement["alter_table_name"], statement["schema"])
    target_table = tables_dict.get(table_id)
    if target_table is None:
        raise ValueError(
            f"Found ALTER statement to not existed TABLE {statement['alter_table_name']} with SCHEMA {statement['schema']}"
        )
    if "columns" in statement:
        alter_columns = []
        for num, column in enumerate(statement["columns"]):

            if isinstance(statement["references"]["column"], str):
                statement["references"]["column"] = [statement["references"]["column"]]
            column_reference = statement["references"]["column"][num]
            alter_column = {
                "name": column,
                "references": {
                    "column": column_reference,
                    "table": statement["references"]["table"],
                    "schema": statement["references"]["schema"],
                },
            }
            alter_columns.append(alter_column)
        if not target_table["alter"].get("columns"):
            target_table["alter"]["columns"] = alter_columns
        else:
            target_table["alter"]["columns"].extend(alter_columns)
    return tables_dict


def result_format(result: List[Dict]) -> List[Dict]:
    final_result = []
    tables_dict = {}
    for table in result:
        table_data = {"columns": [], "primary_key": None, "alter": {}}
        if len(table) == 1 and "alter_table_name" in table[0]:
            tables_dict = add_alter_to_table(tables_dict, table[0])
        else:
            for item in table:
                if item.get("table_name"):
                    table_data["table_name"] = item["table_name"]
                    table_data["schema"] = item["schema"]
                elif not item.get("type") and item.get("primary_key"):
                    table_data["primary_key"] = item["primary_key"]
                elif not item.get("type") and item.get("unique"):
                    table_data["unique"] = item["unique"]
                else:
                    table_data["columns"].append(item)
            tables_dict[(table_data["table_name"], table_data["schema"])] = table_data

            if not table_data["primary_key"]:
                table_data = check_pk_in_columns(table_data)
            else:
                table_data = remove_pk_from_columns(table_data)

            if table_data.get("unique"):
                table_data = add_unique_columns(table_data)
            
            for column in table_data["columns"]:
                if column["name"] in table_data["primary_key"]:
                    column["nullable"] = False
            final_result.append(table_data)
    return final_result

def add_unique_columns(table_data: Dict) -> Dict:
    for column in table_data["columns"]:
        if column['name'] in table_data["unique"]:
            column['unique'] = True
    del table_data["unique"]
    return table_data

def remove_pk_from_columns(table_data: Dict) -> Dict:
    for column in table_data["columns"]:
        del column["primary_key"]
    return table_data


def check_pk_in_columns(table_data: Dict) -> Dict:
    pk = []
    for column in table_data["columns"]:
        if column["primary_key"]:
            pk.append(column["name"])
        del column["primary_key"]
    table_data["primary_key"] = pk
    return table_data


def dump_data_to_file(table_name: str, dump_path: str, data: List[Dict]) -> None:
    """ method to dump json schema """
    if not os.path.isdir(dump_path):
        os.makedirs(dump_path, exist_ok=True)
    with open("{}/{}_schema.json".format(dump_path, table_name), "w+") as schema_file:
        json.dump(data, schema_file, indent=1)
