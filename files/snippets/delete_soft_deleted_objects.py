# flake8: noqa
# Delete all soft-deleted workflow edges and services:

controller.delete_soft_deleted_objects()
print(f"Soft-deleted objects successfully deleted")
