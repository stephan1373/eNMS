# Delete corrupted services.
# Corrupted services are services that used to belong to a workflow and
# were removed from the workflow relationship without being deleted.
# They have the following characteristics:
# - They don't belong to a workflow
# - They are not shared
# - Their scoped name differ from their name
# flake8: noqa

for service in db.fetch_all("service", shared=False):
    if service.workflows or service.name == service.scoped_name:
        continue
    print(f"Deleting '{service}'")
    db.session.delete(service)
db.session.commit()
