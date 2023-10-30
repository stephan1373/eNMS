# Delete all soft-deleted workflow edges and services:
# flake8: noqa

soft_deleted_edges = db.fetch_all("workflow_edge", soft_deleted=True)
for edge in soft_deleted_edges:
    db.delete_instance(edge)
db.session.commit()
soft_deleted_services = db.fetch_all("service", soft_deleted=True)
for service in soft_deleted_services:
    db.delete_instance(service)
db.session.commit()

print(f"Soft-deleted objects successfully deleted")
