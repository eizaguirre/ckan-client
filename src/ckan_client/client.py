import requests
from .exceptions import CkanError, CkanActionError

class CkanClient:
    def __init__(self, base_url: str, api_token: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": api_token})
        self.timeout = timeout

    @classmethod
    def from_databricks_secrets(cls, scope: str, base_url: str, dbutils=None):
        token = dbutils.secrets.get(scope=scope, key="api-token")
        return cls(base_url=base_url, api_token=token)

    def call_action(self, action: str, payload: dict | None = None, files=None) -> dict:
        url = f"{self.base_url}/api/3/action/{action}"
        resp = self.session.post(
            url,
            json=payload if not files else None,
            data=payload if files else None,
            files=files,
            timeout=self.timeout,
        )
        return self._handle_response(resp)

    def _handle_response(self, resp: requests.Response) -> dict:
        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()
            raise CkanError(f"Non-JSON response: {resp.text[:200]}")
        if not data.get("success", False):
            raise CkanActionError(data.get("error", {}), status_code=resp.status_code)
        return data["result"]
