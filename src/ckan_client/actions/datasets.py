class DatasetsMixin:
    def dataset_create(self, **kwargs) -> dict:
        return self.call_action("package_create", kwargs)

    def dataset_update(self, id: str, **kwargs) -> dict:
        return self.call_action("package_update", {"id": id, **kwargs})

    def dataset_patch(self, id: str, **kwargs) -> dict:
        # CKAN's package_patch only overwrites the fields you pass —
        # unlike package_update, which requires the full object.
        return self.call_action("package_patch", {"id": id, **kwargs})

    def dataset_delete(self, id: str, purge: bool = False) -> dict:
        action = "dataset_purge" if purge else "package_delete"
        return self.call_action(action, {"id": id})