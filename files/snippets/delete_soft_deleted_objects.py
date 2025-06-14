# Delete all soft-deleted workflow edges and services:
# flake8: noqa

controller.delete_soft_deleted_objects()
print(f"Soft-deleted objects successfully deleted")
