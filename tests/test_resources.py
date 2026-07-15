import os
import sys
from pathlib import Path

# Add the src directory to Python path so ckan_client can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import requests_mock
from io import BytesIO
from unittest.mock import mock_open, patch
from ckan_client.client import CkanClient
from ckan_client.actions.resources import ResourcesMixin


class TestableClient(CkanClient, ResourcesMixin):
    """Combined client for testing - mixes CkanClient with ResourcesMixin."""
    pass


@pytest.fixture
def base_url():
    """Fixture providing a test CKAN base URL."""
    return "https://fmfss22twc.execute-api.us-east-1.amazonaws.com/dev"


@pytest.fixture
def client(base_url):
    """Fixture providing a TestableClient instance."""
    # Use dummy token for mocked tests
    api_token = os.getenv("CKAN_API_TOKEN", "dummy-token-for-testing")
    return TestableClient(base_url=base_url, api_token=api_token)


class TestResourceCreate:
    """Tests for resource_create method."""
    
    def test_create_resource_without_file(self, requests_mock, client, base_url):
        """Test creating a resource with URL only (no file upload)."""
        # Arrange
        expected_response = {
            "success": True,
            "result": {
                "id": "res123",
                "package_id": "pkg123",
                "url": "https://example.com/data.csv",
                "name": "Data File",
                "format": "CSV"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_create",
            json=expected_response
        )
        
        # Act
        result = client.resource_create(
            package_id="pkg123",
            url="https://example.com/data.csv",
            name="Data File",
            format="CSV"
        )
        
        # Assert
        assert result["id"] == "res123"
        assert result["package_id"] == "pkg123"
        assert result["url"] == "https://example.com/data.csv"
        assert requests_mock.call_count == 1
        
        # Verify the request payload
        request = requests_mock.last_request
        assert request.json() == {
            "package_id": "pkg123",
            "url": "https://example.com/data.csv",
            "name": "Data File",
            "format": "CSV"
        }
    
    def test_create_resource_with_file(self, requests_mock, client, base_url):
        """Test creating a resource with file upload."""
        # Arrange
        expected_response = {
            "success": True,
            "result": {
                "id": "res456",
                "package_id": "pkg123",
                "name": "Uploaded File",
                "format": "CSV"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_create",
            json=expected_response
        )
        
        # Mock file operations
        mock_file_content = b"col1,col2\nval1,val2"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            # Act
            result = client.resource_create(
                package_id="pkg123",
                file_path="/tmp/data.csv",
                name="Uploaded File",
                format="CSV"
            )
        
        # Assert
        assert result["id"] == "res456"
        assert result["package_id"] == "pkg123"
        assert result["name"] == "Uploaded File"
    
    def test_create_resource_minimal(self, requests_mock, client, base_url):
        """Test creating a resource with minimal required fields."""
        expected_response = {
            "success": True,
            "result": {
                "id": "res789",
                "package_id": "pkg999"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_create",
            json=expected_response
        )
        
        # Act - only package_id is required
        result = client.resource_create(package_id="pkg999")
        
        # Assert
        assert result["id"] == "res789"
        assert result["package_id"] == "pkg999"
        
        # Verify minimal payload
        request = requests_mock.last_request
        assert request.json() == {"package_id": "pkg999"}
    
    def test_create_resource_with_metadata(self, requests_mock, client, base_url):
        """Test creating a resource with rich metadata."""
        expected_response = {
            "success": True,
            "result": {
                "id": "res_meta",
                "package_id": "pkg123",
                "name": "Sales Data",
                "description": "Q1 2024 sales figures",
                "format": "XLSX",
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_create",
            json=expected_response
        )
        
        # Act
        result = client.resource_create(
            package_id="pkg123",
            name="Sales Data",
            description="Q1 2024 sales figures",
            format="XLSX",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            url="https://example.com/sales.xlsx"
        )
        
        # Assert
        assert result["name"] == "Sales Data"
        assert result["format"] == "XLSX"
        assert result["description"] == "Q1 2024 sales figures"


class TestResourceUpdate:
    """Tests for resource_update method."""
    
    def test_update_resource_metadata(self, requests_mock, client, base_url):
        """Test updating resource metadata without file."""
        resource_id = "res123"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "name": "Updated Name",
                "description": "Updated description"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_update",
            json=expected_response
        )
        
        # Act
        result = client.resource_update(
            id=resource_id,
            name="Updated Name",
            description="Updated description"
        )
        
        # Assert
        assert result["id"] == resource_id
        assert result["name"] == "Updated Name"
        
        # Verify payload includes id
        request = requests_mock.last_request
        payload = request.json()
        assert payload["id"] == resource_id
        assert payload["name"] == "Updated Name"
    
    def test_update_resource_with_file(self, requests_mock, client, base_url):
        """Test updating a resource with new file upload."""
        resource_id = "res456"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "name": "Updated with new file"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_update",
            json=expected_response
        )
        
        # Mock file operations
        mock_file_content = b"new,data\n1,2"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            # Act
            result = client.resource_update(
                id=resource_id,
                file_path="/tmp/new_data.csv",
                name="Updated with new file"
            )
        
        # Assert
        assert result["id"] == resource_id
        assert result["name"] == "Updated with new file"
    
    def test_update_resource_format(self, requests_mock, client, base_url):
        """Test updating resource format and mimetype."""
        resource_id = "res789"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "format": "JSON",
                "mimetype": "application/json"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_update",
            json=expected_response
        )
        
        # Act
        result = client.resource_update(
            id=resource_id,
            format="JSON",
            mimetype="application/json"
        )
        
        # Assert
        assert result["format"] == "JSON"
        assert result["mimetype"] == "application/json"
    
    def test_update_multiple_fields(self, requests_mock, client, base_url):
        """Test updating multiple resource fields at once."""
        resource_id = "res_multi"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "name": "New Name",
                "description": "New Description",
                "format": "PDF",
                "url": "https://example.com/new.pdf"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_update",
            json=expected_response
        )
        
        # Act
        result = client.resource_update(
            id=resource_id,
            name="New Name",
            description="New Description",
            format="PDF",
            url="https://example.com/new.pdf"
        )
        
        # Assert
        assert result["name"] == "New Name"
        assert result["description"] == "New Description"
        assert result["format"] == "PDF"


class TestResourcePatch:
    """Tests for resource_patch method."""
    
    def test_patch_single_field(self, requests_mock, client, base_url):
        """Test patching only a single field."""
        resource_id = "res123"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "name": "Patched Name"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_patch",
            json=expected_response
        )
        
        # Act
        result = client.resource_patch(
            id=resource_id,
            name="Patched Name"
        )
        
        # Assert
        assert result["id"] == resource_id
        assert result["name"] == "Patched Name"
        
        # Verify only changed field is sent (plus id)
        request = requests_mock.last_request
        payload = request.json()
        assert payload == {
            "id": resource_id,
            "name": "Patched Name"
        }
    
    def test_patch_description_only(self, requests_mock, client, base_url):
        """Test patching only description field."""
        resource_id = "res456"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "description": "New description only"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_patch",
            json=expected_response
        )
        
        # Act
        result = client.resource_patch(
            id=resource_id,
            description="New description only"
        )
        
        # Assert
        assert result["description"] == "New description only"
        
        # Verify only id and description in payload
        request = requests_mock.last_request
        payload = request.json()
        assert set(payload.keys()) == {"id", "description"}
    
    def test_patch_multiple_fields(self, requests_mock, client, base_url):
        """Test patching multiple fields."""
        resource_id = "res789"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "name": "Multi Patch",
                "format": "CSV",
                "description": "Multiple updates"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_patch",
            json=expected_response
        )
        
        # Act
        result = client.resource_patch(
            id=resource_id,
            name="Multi Patch",
            format="CSV",
            description="Multiple updates"
        )
        
        # Assert
        assert result["name"] == "Multi Patch"
        assert result["format"] == "CSV"
        assert result["description"] == "Multiple updates"
    
    def test_patch_vs_update_difference(self, requests_mock, client, base_url):
        """Test that patch only sends specified fields, unlike update."""
        resource_id = "res_compare"
        expected_response = {
            "success": True,
            "result": {
                "id": resource_id,
                "format": "XML"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_patch",
            json=expected_response
        )
        
        # Act - only updating format
        result = client.resource_patch(
            id=resource_id,
            format="XML"
        )
        
        # Assert
        assert result["id"] == resource_id
        
        # Verify minimal payload
        request = requests_mock.last_request
        payload = request.json()
        assert set(payload.keys()) == {"id", "format"}


class TestResourceDelete:
    """Tests for resource_delete method."""
    
    def test_delete_resource(self, requests_mock, client, base_url):
        """Test deleting a resource."""
        resource_id = "res123"
        expected_response = {
            "success": True,
            "result": {"id": resource_id}
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_delete",
            json=expected_response
        )
        
        # Act
        result = client.resource_delete(id=resource_id)
        
        # Assert
        assert result["id"] == resource_id
        
        # Verify correct endpoint and payload
        request = requests_mock.last_request
        assert "resource_delete" in request.url
        assert request.json() == {"id": resource_id}
    
    def test_delete_multiple_resources(self, requests_mock, client, base_url):
        """Test deleting multiple resources sequentially."""
        resource_ids = ["res1", "res2", "res3"]
        
        # Use a dynamic response that echoes back the request's id
        def json_callback(request, context):
            req_json = request.json()
            return {"success": True, "result": {"id": req_json["id"]}}
        
        requests_mock.post(
            f"{base_url}/api/3/action/resource_delete",
            json=json_callback
        )
        
        # Act - delete all resources
        results = [client.resource_delete(id=res_id) for res_id in resource_ids]
        
        # Assert
        assert len(results) == 3
        assert requests_mock.call_count == 3
        
        # Verify all were deleted
        for i, res_id in enumerate(resource_ids):
            assert results[i]["id"] == res_id


class TestResourceMethodsIntegration:
    """Integration tests covering method interactions and edge cases."""
    
    def test_call_action_integration(self, requests_mock, client, base_url):
        """Test that all methods properly call the underlying call_action."""
        expected_response = {"success": True, "result": {"id": "test"}}
        
        # Mock all endpoints
        requests_mock.post(
            f"{base_url}/api/3/action/resource_create",
            json=expected_response
        )
        requests_mock.post(
            f"{base_url}/api/3/action/resource_update",
            json=expected_response
        )
        requests_mock.post(
            f"{base_url}/api/3/action/resource_patch",
            json=expected_response
        )
        requests_mock.post(
            f"{base_url}/api/3/action/resource_delete",
            json=expected_response
        )
        
        # Act - call all methods
        client.resource_create(package_id="pkg123")
        client.resource_update(id="test")
        client.resource_patch(id="test")
        client.resource_delete(id="test")
        
        # Assert - all endpoints were called
        assert requests_mock.call_count == 4
        
        # Verify each endpoint was called once
        called_urls = [req.url for req in requests_mock.request_history]
        assert any("resource_create" in url for url in called_urls)
        assert any("resource_update" in url for url in called_urls)
        assert any("resource_patch" in url for url in called_urls)
        assert any("resource_delete" in url for url in called_urls)
    
    def test_empty_kwargs_patch(self, requests_mock, client, base_url):
        """Test patch with only required id, no other fields."""
        expected_response = {
            "success": True,
            "result": {"id": "test123"}
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_patch",
            json=expected_response
        )
        
        # Act
        result = client.resource_patch(id="test123")
        
        # Assert
        assert result["id"] == "test123"
        
        # Verify only id in payload
        request = requests_mock.last_request
        assert request.json() == {"id": "test123"}
    
    def test_file_and_url_together(self, requests_mock, client, base_url):
        """Test creating resource with both file_path and url."""
        expected_response = {
            "success": True,
            "result": {
                "id": "res_both",
                "package_id": "pkg123",
                "url": "https://example.com/file.csv"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/resource_create",
            json=expected_response
        )
        
        # Mock file operations
        mock_file_content = b"data"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            # Act - provide both file_path and url
            result = client.resource_create(
                package_id="pkg123",
                file_path="/tmp/file.csv",
                url="https://example.com/file.csv"
            )
        
        # Assert - when file_path is provided, it takes precedence
        assert result["id"] == "res_both"
