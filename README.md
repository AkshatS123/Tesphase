Commands to note for token refresh: 

Use for Enphase token refresh: 

replace the &code=... from signing into enphase api and doing redirect uri thing
replace the Authorization: Basic... with The client id and client secret in base64encoded 


curl --location --request POST "https://api.enphaseenergy.com/oauth/token?grant_type=authorization_code&redirect_uri=https://api.enphaseenergy.com/oauth/redirect_uri&code=PAgwKU" --header "Authorization: Basic NzU5OTQxMjU4NGNmNjNkNzdlN2I3N2UwMzhkMDYwMzIzNjhjMmIwNDYzZjQ3ZGJhZmI0YmMzZGMxZmU1YzRmZA="