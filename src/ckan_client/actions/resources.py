class ResourcesMixin:
    def resource_create(self, package_id: str, file_path: str | None = None, **kwargs) -> dict:
        payload = {"package_id": package_id, **kwargs}
        if file_path:
            with open(file_path, "rb") as f:
                return self.call_action("resource_create", payload, files={"upload": f})
        return self.call_action("resource_create", payload)

    def resource_update(self, id: str, file_path: str | None = None, **kwargs) -> dict:
        payload = {"id": id, **kwargs}
        if file_path:
            with open(file_path, "rb") as f:
                return self.call_action("resource_update", payload, files={"upload": f})
        return self.call_action("resource_update", payload)

    def resource_patch(self, id: str, **kwargs) -> dict:
        return self.call_action("resource_patch", {"id": id, **kwargs})

    def resource_delete(self, id: str) -> dict:
        return self.call_action("resource_delete", {"id": id})