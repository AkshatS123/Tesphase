import json
import requests
import base64
import hashlib
import time
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import urllib.parse

class TeslaFleetAPI:
    def __init__(self, token_file_path="tokens.json"):
        self.token_file_path = token_file_path
        self.base_url = "https://fleet-api.prd.vn.cloud.tesla.com"
        self.auth_url = "https://fleet-auth.prd.vn.cloud.tesla.com"
        
        # Load configuration
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from tokens.json file"""
        try:
            with open(self.token_file_path, 'r') as f:
                data = json.load(f)
                return data.get('tesla_fleet_api', {})
        except FileNotFoundError:
            print(f"Token file {self.token_file_path} not found")
            return {}
    
    def save_config(self, new_tokens):
        """Save updated tokens to the config file"""
        try:
            with open(self.token_file_path, 'r') as f:
                data = json.load(f)
            
            # Update Fleet API tokens
            if 'tesla_fleet_api' not in data:
                data['tesla_fleet_api'] = {}
            
            data['tesla_fleet_api'].update(new_tokens)
            
            with open(self.token_file_path, 'w') as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def generate_authorization_url(self, redirect_uri, state=None):
        """Generate the authorization URL for OAuth flow"""
        if not state:
            state = base64.urlsafe_b64encode(hashlib.sha256(str(time.time()).encode()).digest()).decode()[:16]
        
        params = {
            'response_type': 'code',
            'client_id': self.config.get('client_id'),
            'redirect_uri': redirect_uri,
            'scope': 'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds',
            'state': state
        }
        
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.auth_url}/oauth2/v3/authorize?{query_string}"
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, authorization_code, redirect_uri):
        """Exchange authorization code for access and refresh tokens"""
        url = f"{self.auth_url}/oauth2/v3/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
            'code': authorization_code,
            'redirect_uri': redirect_uri
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Save tokens
            self.save_config({
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'token_expiry': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
            })
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error exchanging code for tokens: {e}")
            return None
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.config.get('refresh_token'):
            print("No refresh token available")
            return None
            
        url = f"{self.auth_url}/oauth2/v3/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
            'refresh_token': self.config.get('refresh_token')
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Save new tokens
            self.save_config({
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token', self.config.get('refresh_token')),
                'token_expiry': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
            })
            
            # Update config
            self.config = self.load_config()
            
            return token_data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return None
    
    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary"""
        # Check if token exists and is not expired
        if not self.config.get('access_token'):
            return None
            
        expiry_str = self.config.get('token_expiry')
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now() >= expiry - timedelta(minutes=5):  # Refresh 5 minutes before expiry
                print("Token expired, refreshing...")
                return self.refresh_access_token()
        
        return self.config.get('access_token')
    
    def make_api_request(self, endpoint, method='GET', data=None):
        """Make an authenticated API request"""
        token = self.get_valid_token()
        if not token:
            print("No valid token available")
            return None
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                response = requests.request(method, url, headers=headers, json=data)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def get_vehicles(self):
        """Get list of vehicles"""
        return self.make_api_request('/api/1/vehicles')
    
    def get_vehicle_data(self, vehicle_id):
        """Get vehicle data"""
        return self.make_api_request(f'/api/1/vehicles/{vehicle_id}/vehicle_data')
    
    def wake_up_vehicle(self, vehicle_id):
        """Wake up a vehicle"""
        return self.make_api_request(f'/api/1/vehicles/{vehicle_id}/wake_up', method='POST')
    
    def get_charging_state(self, vehicle_id):
        """Get charging state for a vehicle"""
        vehicle_data = self.get_vehicle_data(vehicle_id)
        if vehicle_data and 'response' in vehicle_data:
            return vehicle_data['response'].get('charge_state', {})
        return None
    
    def start_charging(self, vehicle_id):
        """Start charging a vehicle"""
        return self.make_api_request(f'/api/1/vehicles/{vehicle_id}/command/charge_start', method='POST')
    
    def stop_charging(self, vehicle_id):
        """Stop charging a vehicle"""
        return self.make_api_request(f'/api/1/vehicles/{vehicle_id}/command/charge_stop', method='POST')
    
    def set_charging_amps(self, vehicle_id, charging_amps):
        """Set charging amperage for a vehicle"""
        data = {'charging_amps': charging_amps}
        return self.make_api_request(f'/api/1/vehicles/{vehicle_id}/command/set_charging_amps', method='POST', data=data)
    
    def get_vehicle_by_name_or_id(self, identifier):
        """Get vehicle by name or ID"""
        vehicles = self.get_vehicles()
        if not vehicles or 'response' not in vehicles:
            return None
            
        for vehicle in vehicles['response']:
            if (str(vehicle.get('id')) == str(identifier) or 
                vehicle.get('display_name', '').lower() == identifier.lower() or
                vehicle.get('vin') == identifier):
                return vehicle
        return None


# Usage example and setup functions
def setup_oauth_flow():
    """Helper function to set up OAuth flow"""
    fleet_api = TeslaFleetAPI()
    
    redirect_uri = "https://your-domain.com/callback"  # Replace with your redirect URI
    auth_url, state = fleet_api.generate_authorization_url(redirect_uri)
    
    print("Step 1: Go to this URL to authorize your application:")
    print(auth_url)
    print(f"\nStep 2: After authorization, you'll be redirected to: {redirect_uri}")
    print("Step 3: Copy the 'code' parameter from the callback URL")
    print("Step 4: Run exchange_code_for_tokens() with the code")
    
    return fleet_api, state

def test_fleet_api():
    """Test the Fleet API integration"""
    fleet_api = TeslaFleetAPI()
    
    # Test getting vehicles
    vehicles = fleet_api.get_vehicles()
    if vehicles:
        print("Vehicles:", json.dumps(vehicles, indent=2))
    else:
        print("Failed to get vehicles")
    
    return fleet_api

if __name__ == "__main__":
    # Uncomment the line below to start OAuth setup
    # setup_oauth_flow()
    
    # Uncomment the line below to test the API
    # test_fleet_api()
    pass