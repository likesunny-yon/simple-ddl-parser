import os
import json
from copy import deepcopy
from typing import Dict, List, Union, Tuple
from simple_ddl_parser.output import dialects as d


output_modes = ["mssql", "mysql", "oracle", "hql", "sql"]


def get_table_from_tables_data(
    tables_dict: Dict, table_id: Tuple[str, str], statement: Dict
) -> Dict:

    target_table = tables_dict.get(table_id)
    if target_table is None:
        raise ValueError(
            f"Found ALTER statement to not existed TABLE {table_id[0]} with SCHEMA {table_id[1]}"
        )
    return target_table


def add_index_to_table(tables_dict: Dict, statement: Dict, output_mode: str) -> Dict:

    table_id = (statement["table_name"], statement["schema"])
    target_table = get_table_from_tables_data(tables_dict, table_id, statement)
    del statement["schema"]
    del statement["table_name"]
    if output_mode != "mssql":
        del statement["clustered"]
    target_table["index"].append(statement)
    return tables_dict


def add_alter_to_table(tables_dict: Dict, statement: Dict) -> Dict:
    # todo: refactor
    table_id = (statement["alter_table_name"], statement["schema"])
    target_table = get_table_from_tables_data(tables_dict, table_id, statement)
    if "columns" in statement:
        alter_columns = []
        for num, column in enumerate(statement["columns"]):
            column_reference = statement["references"]["columns"][num]
            alter_column = {
                "name": column["name"],
                "constraint_name": column.get("constraint_name"),
            }
            alter_column["references"] = deepcopy(statement["references"])
            alter_column["references"]["column"] = column_reference
            del alter_column["references"]["columns"]
            alter_columns.append(alter_column)
        if not target_table["alter"].get("columns"):
            target_table["alter"]["columns"] = alter_columns
        else:
            target_table["alter"]["columns"].extend(alter_columns)
    elif "check" in statement:
        if not target_table["alter"].get("checks"):
            target_table["alter"]["checks"] = []
        statement["check"]["statement"] = " ".join(statement["check"]["statement"])
        target_table["alter"]["checks"].append(statement["check"])
    elif "unique" in statement:
        target_table = set_alter_to_table_data('unique', statement, target_table)
        target_table = set_unique_columns_from_alter(statement, target_table)
    elif "default" in statement:
        target_table = set_alter_to_table_data('default', statement, target_table)
        target_table = set_default_columns_from_alter(statement, target_table)
    return tables_dict


def set_default_columns_from_alter(statement: Dict, target_table: Dict):
    for column in target_table["columns"]:
        for column_name in statement["default"]["columns"]:
            if column["name"] == column_name:
                column["default"] = statement["default"]['value']
    return target_table

    
def set_unique_columns_from_alter(statement: Dict, target_table: Dict) -> Dict:
    for column in target_table["columns"]:
        for column_name in statement["unique"]["columns"]:
            if column["name"] == column_name:
                column["unique"] = True
    return target_table

def set_alter_to_table_data(key: str, statement: Dict, target_table: Dict) -> Dict:
    if not target_table["alter"].get(key+'s'):
        target_table["alter"][key+'s'] = []
    target_table["alter"][key+'s'].append(statement[key])
    return target_table
    
def set_checks_to_table(table_data: Dict, check: Union[List, Dict]) -> Dict:
    if isinstance(check, list):
        check = {"constraint_name": None, "statement": " ".join(check)}
    table_data["checks"].append(check)
    return table_data


def result_format(
    result: List[Dict], output_mode: str, group_by_type: bool
) -> List[Dict]:
    final_result = []
    tables_dict = {}
    for table in result:
        table_data = {
            "columns": [],
            "primary_key": None,
            "alter": {},
            "checks": [],
            "index": [],
            "partitioned_by": [],
        }
        table_data = d.populate_dialects_table_data(output_mode, table_data)
        not_table = False
        if len(table) == 1 and "index_name" in table[0]:
            tables_dict = add_index_to_table(tables_dict, table[0], output_mode)

        elif len(table) == 1 and "alter_table_name" in table[0]:
            tables_dict = add_alter_to_table(tables_dict, table[0])
        else:
            for item in table:
                if item.get("sequence_name") or item.get("type_name"):
                    table_data = item
                    not_table = True
                    continue
                elif item.get("table_name"):
                    table_data.update(item)
                    table_data = set_unique_columns(table_data)
            if not not_table:
                if table_data.get("table_name"):
                    tables_dict[
                        (table_data["table_name"], table_data["schema"])
                    ] = table_data
                else:
                    print(
                        "\n Something goes wrong. Possible you try to parse unsupported statement \n "
                    )
                if not table_data.get("primary_key"):
                    table_data = check_pk_in_columns(table_data)
                else:
                    table_data = remove_pk_from_columns(table_data)

                if table_data.get("unique"):
                    table_data = add_unique_columns(table_data)

                for column in table_data["columns"]:
                    if column["name"] in table_data["primary_key"]:
                        column["nullable"] = False
            # todo: this is hack, need to remove it
            if "references" in table_data:
                del table_data["references"]
            if "ref_columns" in table_data:
                for col_ref in table_data["ref_columns"]:
                    name = col_ref["name"]
                    for column in table_data["columns"]:
                        if name == column["name"]:
                            del col_ref["name"]
                            column["references"] = col_ref
                del table_data["ref_columns"]
            d.dialects_clean_up(output_mode, table_data)

            final_result.append(table_data)
    if group_by_type:
        final_result = group_by_type_result(final_result)
    return final_result


def set_unique_columns(table_data: Dict) -> Dict:

    unique_keys = ["unique_statement", "constraints"]

    for key in unique_keys:
        if table_data.get(key, None):
            for column in table_data["columns"]:
                if key == "constraints":
                    unique = table_data[key].get("unique", [])
                    if unique:
                        check_in = unique["columns"]
                    else:
                        check_in = []
                else:
                    check_in = table_data[key]
                if column["name"] in check_in:
                    column["unique"] = True
    if "unique_statement" in table_data:
        del table_data["unique_statement"]
    return table_data


def group_by_type_result(final_result: List[Dict]) -> Dict[str, List]:
    result_as_dict = {"tables": [], "types": [], "sequences": []}
    keys_map = {
        "table_name": "tables",
        "sequence_name": "sequences",
        "type_name": "types",
    }
    for item in final_result:
        for key in keys_map:
            if key in item:
                result_as_dict[keys_map.get(key)].append(item)
                break

    return result_as_dict


def add_unique_columns(table_data: Dict) -> Dict:
    for column in table_data["columns"]:
        if column["name"] in table_data["unique"]:
            column["unique"] = True
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
