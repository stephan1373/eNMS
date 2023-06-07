# This script use the SQLAlchemy _do_orm_execute event to analyze
# what SQL queries were executed (type and SQL statement)
# flake8: noqa

print(f"Number of Queries: {db.orm_statements.total()}\n")

for query, count in db.orm_statements.most_common():
    print(f"{count}: {query}")
