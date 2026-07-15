import os
import sys
from pathlib import Path

# Add the src directory to Python path so ckan_client can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import requests_mock
from ckan_client.client import CkanClient
from ckan_client.actions.datasets import DatasetsMixin


class TestableClient(CkanClient, DatasetsMixin):
    """Combined client for testing - mixes CkanClient with DatasetsMixin."""
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


class TestDatasetCreate:
    """Tests for dataset_create method."""
    
    def test_create_minimal_dataset(self, requests_mock, client, base_url):
        """Test creating a dataset with minimal fields."""
        # Arrange
        expected_response = {
            "success": True,
            "result": {
                "id": "abc123",
                "name": "test-dataset",
                "title": "Test Dataset"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_create",
            json=expected_response
        )
        
        # Act
        result = client.dataset_create(
            name="test-dataset",
            title="Test Dataset"
        )
        
        # Assert
        assert result["id"] == "abc123"
        assert result["name"] == "test-dataset"
        assert requests_mock.call_count == 1
        
        # Verify the request payload
        request = requests_mock.last_request
        assert request.json() == {
            "name": "test-dataset",
            "title": "Test Dataset"
        }
    
    def test_create_dataset_with_metadata(self, requests_mock, client, base_url):
        """Test creating a dataset with rich metadata."""
        expected_response = {
            "success": True,
            "result": {
                "id": "xyz789",
                "name": "sales-data",
                "title": "Sales Data 2024",
                "notes": "Annual sales dataset",
                "tags": [{"name": "sales"}, {"name": "finance"}]
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_create",
            json=expected_response
        )
        
        # Act
        result = client.dataset_create(
            name="sales-data",
            title="Sales Data 2024",
            notes="Annual sales dataset",
            tags=[{"name": "sales"}, {"name": "finance"}]
        )
        
        # Assert
        assert result["id"] == "xyz789"
        assert result["name"] == "sales-data"
        assert len(result["tags"]) == 2


class TestDatasetUpdate:
    """Tests for dataset_update method."""
    
    def test_update_dataset_title(self, requests_mock, client, base_url):
        """Test updating a dataset's title."""
        dataset_id = "abc123"
        expected_response = {
            "success": True,
            "result": {
                "id": dataset_id,
                "name": "test-dataset",
                "title": "Updated Title"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_update",
            json=expected_response
        )
        
        # Act
        result = client.dataset_update(
            id=dataset_id,
            title="Updated Title",
            name="test-dataset"
        )
        
        # Assert
        assert result["id"] == dataset_id
        assert result["title"] == "Updated Title"
        
        # Verify the request includes the ID
        request = requests_mock.last_request
        payload = request.json()
        assert payload["id"] == dataset_id
        assert payload["title"] == "Updated Title"
    
    def test_update_multiple_fields(self, requests_mock, client, base_url):
        """Test updating multiple dataset fields at once."""
        dataset_id = "xyz789"
        expected_response = {
            "success": True,
            "result": {
                "id": dataset_id,
                "name": "updated-name",
                "title": "Updated Title",
                "notes": "Updated description",
                "private": True
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_update",
            json=expected_response
        )
        
        # Act
        result = client.dataset_update(
            id=dataset_id,
            name="updated-name",
            title="Updated Title",
            notes="Updated description",
            private=True
        )
        
        # Assert
        assert result["name"] == "updated-name"
        assert result["private"] is True


class TestDatasetPatch:
    """Tests for dataset_patch method."""
    
    def test_patch_single_field(self, requests_mock, client, base_url):
        """Test patching only a single field (title)."""
        dataset_id = "abc123"
        expected_response = {
            "success": True,
            "result": {
                "id": dataset_id,
                "title": "Patched Title"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_patch",
            json=expected_response
        )
        
        # Act
        result = client.dataset_patch(
            id=dataset_id,
            title="Patched Title"
        )
        
        # Assert
        assert result["id"] == dataset_id
        assert result["title"] == "Patched Title"
        
        # Verify only the changed field is sent (plus id)
        request = requests_mock.last_request
        payload = request.json()
        assert payload == {
            "id": dataset_id,
            "title": "Patched Title"
        }
    
    def test_patch_vs_update_difference(self, requests_mock, client, base_url):
        """Test that patch only sends specified fields, unlike update."""
        dataset_id = "xyz789"
        expected_response = {
            "success": True,
            "result": {
                "id": dataset_id,
                "notes": "Updated notes only"
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_patch",
            json=expected_response
        )
        
        # Act - only updating notes, not the full object
        result = client.dataset_patch(
            id=dataset_id,
            notes="Updated notes only"
        )
        
        # Assert
        assert result["id"] == dataset_id
        
        # Verify only id and notes are in the payload
        request = requests_mock.last_request
        payload = request.json()
        assert set(payload.keys()) == {"id", "notes"}
    
    def test_patch_multiple_fields(self, requests_mock, client, base_url):
        """Test patching multiple fields at once."""
        dataset_id = "test123"
        expected_response = {
            "success": True,
            "result": {
                "id": dataset_id,
                "title": "New Title",
                "notes": "New Description",
                "private": False
            }
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_patch",
            json=expected_response
        )
        
        # Act
        result = client.dataset_patch(
            id=dataset_id,
            title="New Title",
            notes="New Description",
            private=False
        )
        
        # Assert
        assert result["title"] == "New Title"
        assert result["notes"] == "New Description"
        assert result["private"] is False


class TestDatasetDelete:
    """Tests for dataset_delete method."""
    
    def test_delete_dataset_default(self, requests_mock, client, base_url):
        """Test deleting a dataset (soft delete by default)."""
        dataset_id = "abc123"
        expected_response = {
            "success": True,
            "result": {"id": dataset_id}
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_delete",
            json=expected_response
        )
        
        # Act
        result = client.dataset_delete(id=dataset_id)
        
        # Assert
        assert result["id"] == dataset_id
        
        # Verify correct endpoint was called (package_delete, not dataset_purge)
        request = requests_mock.last_request
        assert "package_delete" in request.url
        assert request.json() == {"id": dataset_id}
    
    def test_delete_dataset_with_purge_false(self, requests_mock, client, base_url):
        """Test soft delete explicitly with purge=False."""
        dataset_id = "xyz789"
        expected_response = {
            "success": True,
            "result": {"id": dataset_id}
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_delete",
            json=expected_response
        )
        
        # Act
        result = client.dataset_delete(id=dataset_id, purge=False)
        
        # Assert
        assert result["id"] == dataset_id
        assert "package_delete" in requests_mock.last_request.url
    
    def test_delete_dataset_with_purge_true(self, requests_mock, client, base_url):
        """Test hard delete (purge) of a dataset."""
        dataset_id = "purge123"
        expected_response = {
            "success": True,
            "result": {"id": dataset_id}
        }
        requests_mock.post(
            f"{base_url}/api/3/action/dataset_purge",
            json=expected_response
        )
        
        # Act
        result = client.dataset_delete(id=dataset_id, purge=True)
        
        # Assert
        assert result["id"] == dataset_id
        
        # Verify correct endpoint was called (dataset_purge, not package_delete)
        request = requests_mock.last_request
        assert "dataset_purge" in request.url
        assert request.json() == {"id": dataset_id}


class TestDatasetMethodsIntegration:
    """Integration tests covering method interactions and edge cases."""
    
    def test_call_action_integration(self, requests_mock, client, base_url):
        """Test that all methods properly call the underlying call_action."""
        expected_response = {"success": True, "result": {"id": "test"}}
        
        # Mock all endpoints
        requests_mock.post(
            f"{base_url}/api/3/action/package_create",
            json=expected_response
        )
        requests_mock.post(
            f"{base_url}/api/3/action/package_update",
            json=expected_response
        )
        requests_mock.post(
            f"{base_url}/api/3/action/package_patch",
            json=expected_response
        )
        requests_mock.post(
            f"{base_url}/api/3/action/package_delete",
            json=expected_response
        )
        
        # Act - call all methods
        client.dataset_create(name="test")
        client.dataset_update(id="test", name="test")
        client.dataset_patch(id="test", title="test")
        client.dataset_delete(id="test")
        
        # Assert - all endpoints were called
        assert requests_mock.call_count == 4
        
        # Verify each endpoint was called once
        called_urls = [req.url for req in requests_mock.request_history]
        assert any("package_create" in url for url in called_urls)
        assert any("package_update" in url for url in called_urls)
        assert any("package_patch" in url for url in called_urls)
        assert any("package_delete" in url for url in called_urls)
    
    def test_empty_kwargs(self, requests_mock, client, base_url):
        """Test methods handle empty additional kwargs gracefully."""
        expected_response = {
            "success": True,
            "result": {"id": "test123"}
        }
        requests_mock.post(
            f"{base_url}/api/3/action/package_patch",
            json=expected_response
        )
        
        # Act - patch with only required id, no other fields
        result = client.dataset_patch(id="test123")
        
        # Assert
        assert result["id"] == "test123"
        
        # Verify only id is in the payload
        request = requests_mock.last_request
        assert request.json() == {"id": "test123"}
