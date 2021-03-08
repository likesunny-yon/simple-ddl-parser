## Simple DDL Parser

![badge1](https://img.shields.io/pypi/v/simple-ddl-parser) ![badge2](https://img.shields.io/pypi/l/simple-ddl-parser) ![badge3](https://img.shields.io/pypi/pyversions/simple-ddl-parser) 


### How to install

```bash

    pip install simple-ddl-parser

```

Parser tested on different DDLs for PostgreSQL & Hive.
Types that are used in your DB does not matter, so parser must also work successfuly to any DDL for SQL DB.

If you have samples that cause an error - please open the issue (but don't forget to add ddl example), I will be glad to fix it.

This parser take as input SQL DDL statements or files, for example like this:

```sql

    create table prod.super_table
(
    data_sync_id bigint not null default 0,
    id_ref_from_another_table int REFERENCES another_table (id)
    sync_count bigint not null REFERENCES count_table (count),
    sync_mark timestamp  not  null,
    sync_start timestamp  not null default now(),
    sync_end timestamp  not null,
    message varchar(2000) null,
    primary key (data_sync_id, sync_start)
);

```

And produce output like this (information about table name, schema, columns, types and properties):

```python

    [
        {
            "columns": [
                {
                    "name": "data_sync_id", "type": "bigint", "size": None, 
                    "nullable": False, "default": None, "references": None,
                },
                {
                    "name": "id_ref_from_another_table", "type": "int", "size": None,
                    "nullable": False, "default": None, "references": {"table": "another_table", "schema": None, "column": "id"},
                },
                {
                    "name": "sync_count", "type": "bigint", "size": None,
                    "nullable": False, "default": None, "references": {"table": "count_table", "schema": None, "column": "count"},
                },
                {
                    "name": "sync_mark", "type": "timestamp", "size": None,
                    "nullable": False, "default": None, "references": None,
                },
                {
                    "name": "sync_start", "type": "timestamp", "size": None,
                    "nullable": False, "default": None, "references": None,
                },
                {
                    "name": "sync_end", "type": "timestamp", "size": None,
                    "nullable": False, "default": None, "references": None,
                },
                {
                    "name": "message", "type": "varchar", "size": 2000,
                    "nullable": False, "default": None, "references": None,
                },
            ],
            "primary_key": ["data_sync_id", "sync_start"],
            "table_name": "super_table",
            "schema": "prod",
        }
    ]
```

Or one more example


```sql

CREATE TABLE "paths" (
  "id" int PRIMARY KEY,
  "title" varchar NOT NULL,
  "description" varchar(160),
  "created_at" timestamp,
  "updated_at" timestamp
);


```

and result

```python
        [{
        'columns': [
            {'name': 'id', 'type': 'int', 'nullable': False, 'size': None, 'default': None, 'references': None}, 
            {'name': 'title', 'type': 'varchar', 'nullable': False, 'size': None, 'default': None, 'references': None}, 
            {'name': 'description', 'type': 'varchar', 'nullable': False, 'size': 160, 'default': None, 'references': None}, 
            {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'size': None, 'default': None, 'references': None}, 
            {'name': 'updated_at', 'type': 'timestamp', 'nullable': False, 'size': None, 'default': None, 'references': None}], 
        'primary_key': ['id'], 
        'table_name': 'paths', 'schema': None
        }]

```

If you pass file or text block with more when 1 CREATE TABLE statement when result will be list of such dicts. For example:

Input:

```sql

CREATE TABLE "countries" (
  "id" int PRIMARY KEY,
  "code" varchar(4) NOT NULL,
  "name" varchar NOT NULL
);

CREATE TABLE "path_owners" (
  "user_id" int,
  "path_id" int,
  "type" int DEFAULT 1
);

```
Output:

```python

    [
        {'columns': [
            {'name': 'id', 'type': 'int', 'size': None, 'nullable': False, 'default': None, 'references': None}, 
            {'name': 'code', 'type': 'varchar', 'size': 4, 'nullable': False, 'default': None, 'references': None}, 
            {'name': 'name', 'type': 'varchar', 'size': None, 'nullable': False, 'default': None, 'references': None}], 
         'primary_key': ['id'], 
         'table_name': 'countries', 
         'schema': None}, 
        {'columns': [
            {'name': 'user_id', 'type': 'int', 'size': None, 'nullable': False, 'default': None, 'references': None}, 
            {'name': 'path_id', 'type': 'int', 'size': None, 'nullable': False, 'default': None, 'references': None}, 
            {'name': 'type', 'type': 'int', 'size': None, 'nullable': False, 'default': 1, 'references': None}], 
         'primary_key': [], 
         'table_name': 'path_owners', 
         'schema': None}
    ]

```

## How to use

### From python code

```python
    from simple_ddl_parser import DDLParser


    parse_results = DDLParser("""create table dev.data_sync_history(
        data_sync_id bigint not null,
        sync_count bigint not null,
        sync_mark timestamp  not  null,
        sync_start timestamp  not null,
        sync_end timestamp  not null,
        message varchar(2000) null,
        primary key (data_sync_id, sync_start)
    ); """).run()

    print(parse_results) 

```

### To parse from file

```python
    
    from simple_ddl_parser import parse_from_file

    result = parse_from_file('tests/test_one_statement.sql')
    print(result)

```

### From command line

simple-ddl-parser is installed to environment as command **sdp**

```bash

    sdp path_to_ddl_file

    # for example:

    sdp tests/test_two_tables.sql
    
```

You will see the output in **schemas** folder in file with name **test_two_tables_schema.json**

If you want to have also output in console - use **-v** flag for verbose.

```bash
    
    sdp tests/test_two_tables.sql -v
    
```

If you don't want to dump schema in file and just print result to the console, use **--no-dump** flag:


```bash
    
    sdp tests/test_two_tables.sql --no-dump
    
```

### More examples & tests

You can find in **tests/functional** folder.

### Dump result in json

To dump result in json use argument .run(dump=True)

You also can provide a path where you want to have a dumps with schema with argument

### TODO in next Releases

1. Support for separate ALTER TABLE statements for Foreigein keys like

```sql

    ALTER TABLE "material_attachments" ADD FOREIGN KEY ("material_id") REFERENCES "materials" ("id");

```
2. Support for parse CREATE INDEX statements
3. Add to command line args: to pass folder with ddls to convert, pass path to get the output results
4. Support ARRAYs


### Historical context

This library is an extracted parser code from https://github.com/xnuinside/fakeme (Library for fake relation data generation, that I used in several work projects, but did not have time to make from it normal open source library)

For one of the work projects I needed to convert SQL ddl to Python ORM models in auto way and I tried to use https://github.com/andialbrecht/sqlparse but it works not well enough with ddl for my case (for example, if in ddl used lower case - nothing works, primary keys inside ddl are mapped as column name not reserved word and etc.).
So I remembered about Parser in Fakeme and just extracted it & improved. 


## How to contribute

Please describe issue that you want to solve and open the PR, I will review it as soon as possible.

Any questions? Ping me in Telegram: https://t.me/xnuinside 