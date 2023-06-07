# This script use the SQLAlchemy _do_orm_execute event to analyze
# what SQL queries were executed (type and SQL statement)
# flake8: noqa

print(f"Number of Queries: {db.orm_statements.total()}\n")

for query, count in db.orm_statements.most_common():
    print(f"{count}: {query}")
    query_time = db.orm_statements_runtime[query]
    print(f"Execution time ({count} query): {query_time}\n\n")

db.monitor_orm_statements = False
