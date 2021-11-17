from simple_ddl_parser import DDLParser


def test_dataset_in_output():
    expected = {
        "domains": [],
        "ddl_properties": [],
        "schemas": [],
        "sequences": [],
        "tables": [
            {
                "alter": {},
                "checks": [],
                "columns": [
                    {
                        "check": None,
                        "default": None,
                        "name": "x",
                        "nullable": True,
                        "references": None,
                        "size": None,
                        "type": "INT64",
                        "unique": False,
                    }
                ],
                "dataset": "mydataset",
                "index": [],
                "partitioned_by": [],
                "primary_key": [],
                "table_name": "newtable",
                "tablespace": None,
            }
        ],
        "types": [],
    }

    ddl = """
    CREATE TABLE mydataset.newtable ( x INT64 )
    """
    result = DDLParser(ddl).run(group_by_type=True, output_mode="bigquery")
    assert expected == result


def test_simple_struct():
    ddl = """
    CREATE TABLE mydataset.newtable
     (
       x INT64 ,
       y STRUCT<a ARRAY<STRING>,b BOOL>
     )
    """
    parse_results = DDLParser(ddl).run(group_by_type=True, output_mode="bigquery")
    expected = {
        "tables": [
            {
                "columns": [
                    {
                        "name": "x",
                        "type": "INT64",
                        "size": None,
                        "references": None,
                        "unique": False,
                        "nullable": True,
                        "default": None,
                        "check": None,
                    },
                    {
                        "name": "y",
                        "type": "STRUCT < a ARRAY < STRING >, b BOOL >",
                        "size": None,
                        "references": None,
                        "unique": False,
                        "nullable": True,
                        "default": None,
                        "check": None,
                    },
                ],
                "primary_key": [],
                "alter": {},
                "checks": [],
                "index": [],
                "partitioned_by": [],
                "tablespace": None,
                "table_name": "newtable",
                "dataset": "mydataset",
            }
        ],
        "types": [],
        "ddl_properties": [],
        "sequences": [],
        "domains": [],
        "schemas": [],
    }

    assert expected == parse_results


def test_schema_options():
    ddl = """
    CREATE SCHEMA IF NOT EXISTS name-name
    OPTIONS (
    location="path"
    );
    """
    parse_result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [
            {
                "properties": {"options": [{"location": '"path"'}]},
                "schema_name": "name-name",
            }
        ],
        "sequences": [],
        "tables": [],
        "types": [],
    }
    assert expected == parse_result


def test_two_options_values():
    ddl = """
    CREATE SCHEMA IF NOT EXISTS name-name
    OPTIONS (
    location="path",
    second_option=second_value
    );
    """
    parse_result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [
            {
                "properties": {
                    "options": [
                        {"location": '"path"'},
                        {"second_option": "second_value"},
                    ]
                },
                "schema_name": "name-name",
            }
        ],
        "sequences": [],
        "tables": [],
        "types": [],
    }
    assert expected == parse_result


def test_long_string_in_option():
    ddl = """
    CREATE SCHEMA IF NOT EXISTS name-name
    OPTIONS (
    description="Calendar table records reference list of calendar dates and related attributes used for reporting."
    );
    """
    result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [
            {
                "properties": {
                    "options": [
                        {
                            "description": '"Calendar table '
                            "records reference "
                            "list of calendar "
                            "dates and related "
                            "attributes used for "
                            'reporting."'
                        }
                    ]
                },
                "schema_name": "name-name",
            }
        ],
        "sequences": [],
        "tables": [],
        "types": [],
    }
    assert expected == result


def test_option_in_create_table():

    ddl = """
    CREATE TABLE name.hub.REF_CALENDAR (
    calendar_dt DATE,
    )
    OPTIONS (
    description="Calendar table records reference list of calendar dates and related attributes used for reporting."
    );
    """
    result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [],
        "sequences": [],
        "tables": [
            {
                "alter": {},
                "checks": [],
                "columns": [
                    {
                        "check": None,
                        "default": None,
                        "name": "calendar_dt",
                        "nullable": True,
                        "references": None,
                        "size": None,
                        "type": "DATE",
                        "unique": False,
                    }
                ],
                "index": [],
                "options": [
                    {
                        "description": '"Calendar table records reference '
                        "list of calendar dates and related "
                        'attributes used for reporting."'
                    }
                ],
                "partitioned_by": [],
                "primary_key": [],
                "schema": "hub",
                "project": "name",
                "table_name": "REF_CALENDAR",
                "tablespace": None,
            }
        ],
        "types": [],
    }
    assert expected == result


def test_options_in_column():
    ddl = """
    CREATE TABLE name.hub.REF_CALENDAR (
    calendar_dt DATE OPTIONS(description="Field Description")
    )
    OPTIONS (
    description="Calendar table records reference list of calendar dates and related attributes used for reporting."
    );
    """
    result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [],
        "sequences": [],
        "tables": [
            {
                "alter": {},
                "checks": [],
                "columns": [
                    {
                        "check": None,
                        "default": None,
                        "name": "calendar_dt",
                        "nullable": True,
                        "options": [{"description": '"Field Description"'}],
                        "references": None,
                        "size": None,
                        "type": "DATE",
                        "unique": False,
                    }
                ],
                "index": [],
                "options": [
                    {
                        "description": '"Calendar table records reference '
                        "list of calendar dates and related "
                        'attributes used for reporting."'
                    }
                ],
                "partitioned_by": [],
                "primary_key": [],
                "project": "name",
                "schema": "hub",
                "table_name": "REF_CALENDAR",
                "tablespace": None,
            }
        ],
        "types": [],
    }
    assert expected == result


def test_cluster_by_without_brackets():
    ddl = """
    CREATE TABLE name.hub.REF_CALENDAR (
    calendar_dt DATE OPTIONS(description="Field Description")
    )
    CLUSTER BY year_reporting_week_no
    OPTIONS (
    description="Calendar table records reference list of calendar dates and related attributes used for reporting."
    );

    """
    result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [],
        "sequences": [],
        "tables": [
            {
                "alter": {},
                "checks": [],
                "cluster_by": ["year_reporting_week_no"],
                "columns": [
                    {
                        "check": None,
                        "default": None,
                        "name": "calendar_dt",
                        "nullable": True,
                        "options": [{"description": '"Field Description"'}],
                        "references": None,
                        "size": None,
                        "type": "DATE",
                        "unique": False,
                    }
                ],
                "index": [],
                "options": [
                    {
                        "description": '"Calendar table records reference '
                        "list of calendar dates and related "
                        'attributes used for reporting."'
                    }
                ],
                "partitioned_by": [],
                "primary_key": [],
                "project": "name",
                "schema": "hub",
                "table_name": "REF_CALENDAR",
                "tablespace": None,
            }
        ],
        "types": [],
    }
    assert expected == result


def test_two_options_in_create_table():

    ddl = """
    CREATE TABLE mydataset.newtable
    (
    x INT64 OPTIONS(description="An optional INTEGER field")
    )
    OPTIONS(
    expiration_timestamp="2023-01-01 00:00:00 UTC",
    description="a table that expires in 2023",
    )

    """
    result = DDLParser(ddl).run(group_by_type=True)
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [],
        "sequences": [],
        "tables": [
            {
                "alter": {},
                "checks": [],
                "columns": [
                    {
                        "check": None,
                        "default": None,
                        "name": "x",
                        "nullable": True,
                        "options": [{"description": '"An optional INTEGER ' 'field"'}],
                        "references": None,
                        "size": None,
                        "type": "INT64",
                        "unique": False,
                    }
                ],
                "index": [],
                "options": [
                    {"expiration_timestamp": '"2023-01-01 00:00:00 UTC"'},
                    {"description": '"a table that expires in 2023"'},
                ],
                "partitioned_by": [],
                "primary_key": [],
                "schema": "mydataset",
                "table_name": "newtable",
                "tablespace": None,
            }
        ],
        "types": [],
    }
    assert expected == result


def test_table_name_with_project_id():

    ddl = """
    CREATE SCHEMA IF NOT EXISTS project.calender
    OPTIONS (
    location="project-location"
    );
    CREATE TABLE project_id.calender.REF_CALENDAR (
    calendar_dt DATE,
    calendar_dt_id INT,
    fiscal_half_year_reporting_week_no INT
    )
    OPTIONS (
    description="Calendar table records reference list of calendar dates and related attributes used for reporting."
    )
    PARTITION BY DATETIME_TRUNC(fiscal_half_year_reporting_week_no, DAY)
    CLUSTER BY calendar_dt



    """
    result = DDLParser(ddl).run(group_by_type=True, output_mode="bigquery")
    expected = {
        "ddl_properties": [],
        "domains": [],
        "schemas": [],
        "sequences": [],
        "tables": [
            {
                "alter": {},
                "checks": [],
                "cluster_by": ["calendar_dt"],
                "columns": [
                    {
                        "check": None,
                        "default": None,
                        "name": "calendar_dt",
                        "nullable": True,
                        "references": None,
                        "size": None,
                        "type": "DATE",
                        "unique": False,
                    },
                    {
                        "check": None,
                        "default": None,
                        "name": "calendar_dt_id",
                        "nullable": True,
                        "references": None,
                        "size": None,
                        "type": "INT",
                        "unique": False,
                    },
                    {
                        "check": None,
                        "default": None,
                        "name": "fiscal_half_year_reporting_week_no",
                        "nullable": True,
                        "references": None,
                        "size": None,
                        "type": "INT",
                        "unique": False,
                    },
                ],
                "dataset": "calender",
                "index": [],
                "options": [
                    {
                        "description": '"Calendar table records reference '
                        "list of calendar dates and related "
                        'attributes used for reporting."'
                    }
                ],
                "partition_by": {
                    "columns": ["fiscal_half_year_reporting_week_no", "DAY"],
                    "type": "DATETIME_TRUNC",
                },
                "partitioned_by": [],
                "primary_key": [],
                "project": "project_id",
                "table_name": "REF_CALENDAR",
                "tablespace": None,
            }
        ],
        "types": [],
    }
    assert expected == result
