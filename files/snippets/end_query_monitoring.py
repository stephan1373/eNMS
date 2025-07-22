# flake8: noqa
# This script use the SQLAlchemy _do_orm_execute event to analyze
# what SQL queries were executed (SQL statement) and how much
# time each query took.

print(f"Number of Queries: {db.orm_statements.total()}\n")

for query, count in db.orm_statements.most_common():
    print(f"{count}: {query}\n")
    query_time = db.orm_statements_runtime[query]
    print(f"Execution time ({count} query): {query_time}\n")
    tracebacks = "\n\n".join(
        f"{count}: {traceback}"
        for traceback, count in db.orm_statements_tracebacks[query].items()
    )
    print(f"Tracebacks:\n{tracebacks}\n\n")

db.monitor_orm_statements = False
