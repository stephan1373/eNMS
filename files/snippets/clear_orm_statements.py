# This script clears the content of the dict used
# for analyzing ORM statements. 
# flake8: noqa

db.monitor_orm_statements = True
db.orm_statements.clear()
db.orm_statements_runtime.clear()
