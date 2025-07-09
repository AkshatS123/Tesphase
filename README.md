# Tesphase - Tesla & Enphase Integration

## Tesla Fleet API Integration

### Domain Setup
- **Public Key Location**: `.well-known/fleet-api-public-key.pem`
- **GitHub Pages URL**: `https://akshats123.github.io/Tesphase`
- **Public Key URL**: `https://akshats123.github.io/Tesphase/.well-known/fleet-api-public-key.pem`

### Key Files
- `private_key.pem` - **KEEP PRIVATE** (excluded from git)
- `public_key.pem` - Safe to share (used for Tesla domain verification)

### Tesla App Registration
1. Go to https://developer.tesla.com
2. Register application with domain: `https://akshats123.github.io/Tesphase`
3. Configure billing method (required as of Jan 1, 2025)
4. Select required scopes (vehicle_device_data, vehicle_location, etc.)

### Integration Status (July 9, 2025)
- ✅ **OAuth Authentication** - Complete and working
- ✅ **API Client** - Fully implemented with token refresh
- ✅ **Domain Verification** - Public key hosted and verified
- ✅ **Partner Account Registration** - Successfully registered in NA region
- ✅ **Vehicle Access** - Tesla Fleet API fully operational
- ✅ **Tesla Integration** - Ready for production use

## Enphase API Integration

### Token Refresh Commands

Use for Enphase token refresh: 

replace the &code=... from signing into enphase api and doing redirect uri thing

&redirect_uri=https://api.enphaseenergy.com/oauth/redirect_uri

replace the Authorization: Basic... with The client id and client secret in base64encoded 

curl --location --request POST "https://api.enphaseenergy.com/oauth/token?grant_type=authorization_code&redirect_uri=https://api.enphaseenergy.com/oauth/redirect_uri&code=pYBnKS" --header "Authorization: Basic NTIyOTcxYWY3ZGU1ZGEyZDdmM2ZlNTMwMWJhNWY0MTM6NTY3M2ExMmYyZmFiZTM0OWQ1MDUyMzZkYjhiOGMzNDU="

THIS WORKED


