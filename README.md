Commands to note for token refresh: 

Use for Enphase token refresh: 

replace the &code=... from signing into enphase api and doing redirect uri thing

&redirect_uri=https://api.enphaseenergy.com/oauth/redirect_uri

replace the Authorization: Basic... with The client id and client secret in base64encoded 

curl --location --request POST "https://api.enphaseenergy.com/oauth/token?grant_type=authorization_code&redirect_uri=https://api.enphaseenergy.com/oauth/redirect_uri&code=pYBnKS" --header "Authorization: Basic NTIyOTcxYWY3ZGU1ZGEyZDdmM2ZlNTMwMWJhNWY0MTM6NTY3M2ExMmYyZmFiZTM0OWQ1MDUyMzZkYjhiOGMzNDU="


THIS WORKED


