# Delete all soft-deleted workflow edges and services:
# flake8: noqa

db.delete(
    "workflow_edge",
    all_matches=True,
    allow_none=True,
    soft_deleted=True,
)
db.session.commit()
db.delete(
    "service",
    all_matches=True,
    allow_none=True,
    soft_deleted=True,
)
db.session.commit()
