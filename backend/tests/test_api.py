"""
Unit tests for the Flask API endpoints.
Tests all API routes and their responses.
"""

import pytest
import json
from app import app


class TestPasswordCheckerAPI:
    """Test suite for password checker API."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    # ====== CHECK ENDPOINT TESTS ======
    
    def test_check_endpoint_success(self, client):
        """Test successful password check."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 'TestPass123!'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'strength' in data
        assert 'score' in data
    
    def test_check_endpoint_missing_password(self, client):
        """Test check endpoint with missing password field."""
        response = client.post('/api/check',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_check_endpoint_no_json(self, client):
        """Test check endpoint without JSON body."""
        response = client.post('/api/check')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_check_endpoint_strong_password(self, client):
        """Test check endpoint with strong password."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 'Str0ng!@#$Passw0rd2024'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['strength'] == 'strong'
    
    def test_check_endpoint_weak_password(self, client):
        """Test check endpoint with weak password."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 'weak'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['strength'] == 'weak'
    
    def test_check_endpoint_empty_password(self, client):
        """Test check endpoint with empty password."""
        response = client.post('/api/check',
                             data=json.dumps({'password': ''}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['strength'] == 'weak'
    
    def test_check_endpoint_response_structure(self, client):
        """Test that response has all required fields."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 'TestPass123!'}),
                             content_type='application/json')
        
        data = json.loads(response.data)
        required_fields = ['strength', 'score', 'feedback', 'criteria', 'suggestions', 'entropy', 'status', 'timestamp']
        
        for field in required_fields:
            assert field in data
    
    def test_check_endpoint_non_string_password(self, client):
        """Test check endpoint with non-string password."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 12345}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_check_endpoint_password_too_long(self, client):
        """Test check endpoint with password exceeding max length."""
        long_password = 'a' * 501
        response = client.post('/api/check',
                             data=json.dumps({'password': long_password}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_check_endpoint_unicode_password(self, client):
        """Test check endpoint with unicode characters."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 'Pässwörd123!'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'strength' in data
    
    # ====== HEALTH CHECK ENDPOINT TESTS ======
    
    def test_health_endpoint_success(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_health_endpoint_response_structure(self, client):
        """Test health check response structure."""
        response = client.get('/api/health')
        
        data = json.loads(response.data)
        required_fields = ['status', 'service', 'version', 'timestamp']
        
        for field in required_fields:
            assert field in data
    
    # ====== INFO ENDPOINT TESTS ======
    
    def test_info_endpoint_success(self, client):
        """Test info endpoint."""
        response = client.get('/api/info')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'name' in data
        assert 'version' in data
    
    def test_info_endpoint_criteria_listed(self, client):
        """Test that info endpoint lists all criteria."""
        response = client.get('/api/info')
        
        data = json.loads(response.data)
        assert 'criteria' in data
        assert len(data['criteria']) > 0
    
    def test_info_endpoint_endpoints_listed(self, client):
        """Test that info endpoint lists all available endpoints."""
        response = client.get('/api/info')
        
        data = json.loads(response.data)
        assert 'endpoints' in data
        assert '/api/check' in data['endpoints']
        assert '/api/health' in data['endpoints']
    
    # ====== ERROR HANDLING TESTS ======
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_method_not_allowed(self, client):
        """Test method not allowed error."""
        response = client.get('/api/check')  # GET instead of POST
        
        assert response.status_code == 405
    
    # ====== CONTENT TYPE TESTS ======
    
    def test_check_endpoint_json_response(self, client):
        """Test that response is valid JSON."""
        response = client.post('/api/check',
                             data=json.dumps({'password': 'test'}),
                             content_type='application/json')
        
        assert response.content_type == 'application/json'
        # Should not raise exception
        json.loads(response.data)
    
    # ====== MULTIPLE REQUEST TESTS ======
    
    def test_multiple_sequential_requests(self, client):
        """Test multiple sequential password checks."""
        passwords = ['weak', 'Medium1', 'Str0ng!@#', 'AnotherTest123!']
        
        for pwd in passwords:
            response = client.post('/api/check',
                                 data=json.dumps({'password': pwd}),
                                 content_type='application/json')
            assert response.status_code == 200
    
    def test_concurrent_request_compatibility(self, client):
        """Test that API handles different passwords correctly."""
        # Simulate sequence that could happen concurrently
        responses = []
        
        for i in range(5):
            response = client.post('/api/check',
                                 data=json.dumps({'password': f'Password{i}!@#'}),
                                 content_type='application/json')
            responses.append(response)
        
        assert all(r.status_code == 200 for r in responses)
    
    # ====== SCORE RANGE TESTS ======
    
    def test_score_always_0_to_100(self, client):
        """Test that score is always between 0 and 100."""
        passwords = ['', 'a', 'test', 'TestPass123!', 'VeryStr0ng!@#$%^&*()Password2024']
        
        for pwd in passwords:
            response = client.post('/api/check',
                                 data=json.dumps({'password': pwd}),
                                 content_type='application/json')
            data = json.loads(response.data)
            assert 0 <= data['score'] <= 100


class TestPasswordCheckerAPIIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_api_workflow_get_info_then_check(self, client):
        """Test workflow: get info, then check password."""
        # Get API info
        info_response = client.get('/api/info')
        assert info_response.status_code == 200
        
        # Check password
        check_response = client.post('/api/check',
                                    data=json.dumps({'password': 'TestPass123!'}),
                                    content_type='application/json')
        assert check_response.status_code == 200
    
    def test_api_workflow_health_check_then_check(self, client):
        """Test workflow: health check, then check password."""
        # Health check
        health_response = client.get('/api/health')
        assert health_response.status_code == 200
        
        # Password check
        check_response = client.post('/api/check',
                                    data=json.dumps({'password': 'Secure!@#$Pass123'}),
                                    content_type='application/json')
        assert check_response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
