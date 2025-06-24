import urllib.request
import json
from datetime import datetime
import base64
import hashlib 
import base64
import urllib 
import json
import getpass
import requests
import smtplib
import time

TOKEN_FILE_PATH = "tokens.json"
CLIENT_ID = "7599412584cf63d77e7b77e038d06032"
CLIENT_SECRET = "368c2b0463f47dbafb4bc3dc1fe5c4fd"
sender_email = "krakedlucifer91@gmail.com"
sender_password = "xfrlwexdeezdntjn"
receiver_email = "svishal@gmail.com"
receiver_email2 = "s.akshat@gmail.com"


Model3 = "1492930803269392"
ModelY = "1493134009886258"
ChargeAmps = 0


def main():
    def emailNotif(subject, body): 
        message = f"Subject: {subject}\n\n{body}"
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")
    
    def emailNotif2(subject, body): 
        message = f"Subject: {subject}\n\n{body}"
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email2, message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")
        # Function to load tokens from the file

    def load_tokens():
        with open(TOKEN_FILE_PATH, "r") as token_file:
            return json.load(token_file)

    # Function to save tokens to the file
    def save_tokens(tokens, new_access, new_refresh):
        with open(TOKEN_FILE_PATH, "w") as token_file:
            tokens["access_tokenEnphase"] = new_access
            #tokens["refresh_tokenEnphase"] = new_refresh
            #save_tokens(tokens)
            #json.dump([{"access_tokenEnphase": new_access, "refresh_tokenEnphase" : new_refresh}])

    def enphase(): 
        
        def refresh_access_token(refresh_tokenEnph):
            refresh_url = "https://api.enphaseenergy.com/oauth/token"
            refresh_params = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_tokenEnph
            }

            # Encode the client credentials for the Authorization header
            credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
            credentials_bytes = credentials.encode('ascii')
            base64_credentials = base64.b64encode(credentials_bytes).decode('ascii')
            auth_header = f"Basic {base64_credentials}"

            headers = {"Authorization": auth_header}

            try:
                refresh_request_url = refresh_url + "?" + "&".join(f"{key}={value}" for key, value in refresh_params.items())
                # Remove invalid characters from the URL
                refresh_request_url = refresh_request_url.replace(" ", "").replace("\n", "").split("--header")[0]
                refresh_request = urllib.request.Request(refresh_request_url, headers=headers, method="POST")
                print("Refreshing token. URL:", refresh_request.full_url)  # Print the URL
                with urllib.request.urlopen(refresh_request) as refresh_response:
                    refresh_data = json.loads(refresh_response.read().decode())
                    print(refresh_data)
                    new_access_token = refresh_data.get("access_token")
                    new_refresh_token = refresh_data.get("refresh_token")
                    # Update the tokens in the JSON file
                    tokens = load_tokens()
                    print("TESING PART HERRE NEW ACESS TOKEN:")
                    print(new_access_token)
                    tokens["access_tokenEnphase"] = new_access_token
                    tokens["refresh_tokenEnphase"] = new_refresh_token
                    save_tokens(tokens, new_access_token, new_refresh_token)  # Save the updated tokens to the JSON file


                return new_access_token
            except urllib.error.URLError as e:
                print("Failed to refresh access_token.")
                return None
        
        tokens = load_tokens()
        access_tokenEnph = tokens.get("access_tokenEnphase")
        refresh_tokenEnph = tokens.get("refresh_tokenEnphase")
        url_production = "https://api.enphaseenergy.com/api/v4/systems/4383764/telemetry/production_meter"
        myParam_production = {"key": "dfdfbbbd4d5687ed46eb2e0f81056bf9"}
        headers = {
            "Authorization": f"Bearer {access_tokenEnph}"
        }

        try:
            # Make the full URL with the parameters for production_meter
            completeRequest_production = url_production + "?" + "&".join(f"{key}={value}" for key, value in myParam_production.items())

            # Push the request with the complete URL for production_meter
            request_production = urllib.request.Request(completeRequest_production, headers=headers)
            # Make the GET request for production_meter
            with urllib.request.urlopen(request_production) as response_production:
                # response.read reads the response data from the server as binary data, then
                # .decode() is turning that back into readable string for us
                data_production = json.loads(response_production.read().decode())
                # json.loads is there to make the data into a python data structure instead of JSON.
                # Now the variable data_production will hold all of our string info, including the dictionary of production data we need.
                last_interval_production = data_production["intervals"][-1]
                # Doing this to take out only the last most recent portion of the dictionary, so we only have the most recent time report.
                end_at_production = last_interval_production.get('end_at')
                wh_del_production = last_interval_production.get('wh_del')
                # Getting the time and the production value
                production_time = datetime.fromtimestamp(end_at_production).strftime('%Y-%m-%d %H:%M:%S')
                # Found online to convert epoch time to readable time
                finProduction = wh_del_production * 4
                print(f"production, {finProduction}")
                #WH returned is per 15 mins. Times 4 for hourly power
                

        except urllib.error.URLError as e:
            if "HTTP Error 401: Unauthorized" not in str(e):
                emailNotif("TESPHASE URL ERROR",f"Enphase reuqest curl didn't go through, produced an error besides Access_token missing, Specified error here: {e}" )
            print("Access token is missing. Obtaining a new one...")
            if refresh_tokenEnph:
                print("IM IN HERE")
                '''
                access_tokenEnph = refresh_access_token(refresh_tokenEnph)
                if access_tokenEnph:
                    print("should have generated new access and refresh into file, running again...")
                    main()
                else:
                    return
                '''
            else:
                print("Refresh token is missing. Please provide a valid refresh token.")
                return

        # Consumption Meter URL
        url_consumption = "https://api.enphaseenergy.com/api/v4/systems/4383764/telemetry/consumption_meter"
        myParam_consumption = {"key": "dfdfbbbd4d5687ed46eb2e0f81056bf9"}

        try:
            # Make the full URL with the parameters for consumption_meter
            completeRequest_consumption = url_consumption + "?" + "&".join(f"{key}={value}" for key, value in myParam_consumption.items())

            # Push the request with the complete URL for consumption_meter
            request_consumption = urllib.request.Request(completeRequest_consumption, headers=headers)
            # Make the GET request for consumption_meter
            with urllib.request.urlopen(request_consumption) as response_consumption:
                # response.read reads the response data from the server as binary data, then
                # .decode() is turning that back into readable string for us
                data_consumption = json.loads(response_consumption.read().decode())
                # json.loads is there to make the data into a python data structure instead of JSON.
                # Now the variable data_consumption will hold all of our string info, including the dictionary of consumption data we need.
                #print(data_consumption)
                last_interval_consumption = data_consumption["intervals"][-1]
                #print(last_interval_consumption)
                end_at_consumption = last_interval_consumption.get('end_at')
                wh_del_consumption = last_interval_consumption.get('enwh')
                # Getting the time and the consumption value
                consumption_time = datetime.fromtimestamp(end_at_consumption).strftime('%Y-%m-%d %H:%M:%S')
                # Found online to convert epoch time to readable time
                finConsumption = wh_del_consumption * 4
                print(f"consumption, {finConsumption}")
                production_time = datetime.strptime(production_time, '%Y-%m-%d %H:%M:%S')
                consumption_time = datetime.strptime(consumption_time, '%Y-%m-%d %H:%M:%S')
                #this will get the currenttime in real time
                current_timeProduction = datetime.now()
                productionTimeDiff = abs(current_timeProduction - production_time).total_seconds()/60
                consumptionTimeDiff = abs(current_timeProduction - production_time).total_seconds()/60
                now = datetime.now().time()
                startBlackout = datetime.strptime("16:00:00", "%H:%M:%S").time()  # 4:00 PM
                endBlackout = datetime.strptime("21:00:00", "%H:%M:%S").time()    # 9:00 PM
                if startBlackout <= now <= endBlackout: 
                    if(finConsumption >= 2000):
                        emailNotif("TESPHASE", "In Blackout Hours, STOP USING POWER")
                        emailNotif2("TESPHASE", "In Blackout Hours, STOP USING POWER")
                        return
                    else: 
                        return
                     
                #print(production_time)
                #print(productionTimeDiff)
                #print(consumptionTimeDiff)
                
                #here we have to compare if the time diffrence between the data time and real time is more than 30 min to see if data even useful. 
                if((productionTimeDiff <=30) and (consumptionTimeDiff <= 30)):
                    #PUT EMAIL NOTIFICATION IF 30 MIN or MORE
                    print(productionTimeDiff)
                    #print(f"End Time for Production: {production_time}")
                    #print(f"Production Value: {finProduction}")
                    #print(f"End Time for Consumption: {consumption_time}")
                    #print(f"Consumption Value: {finConsumption}")
                    # Doing this to take out only the last most recent portion of the dictionary, so we only have the most recent time report.
                    leftoverCharge = finProduction - finConsumption
                    ChargeAmps =  (leftoverCharge / 240)
                    print(f"leftover WH to charge car: {leftoverCharge}")
                    print(f"charge the tesla at: {ChargeAmps} Amps")
                    return ChargeAmps
                else: 
                    print("ERROR: Data not usable, time difrence exceeds 30 mins")
                    emailNotif("TESPHASE", "DATA NOT USABLE, TIME DIFFERENCE > 30")
                    emailNotif2("TESPHASE","DATA NOT USABLE, TIME DIFFERENCE > 30")
                    print("email notification sent to specified email")
                    #send an email here


        except urllib.error.URLError as e:
            if "HTTP Error 401: Unauthorized" not in str(e):
                emailNotif("TESPHASE URL ERROR",f"Enphase reuqest curl didn't go through, produced an error besides Access_token missing, Specified error here: {e}" )
            print("Access token is missing. Obtaining a new one...")
            if refresh_tokenEnph:
                print("IM IN HERE")
                #access_tokenEnph = refresh_access_token(refresh_tokenEnph)
                if access_tokenEnph:
                    print("should have generated new access and refresh into file, running again...")
                    main()
                else:
                    return
            else:
                print("Refresh token is missing. Please provide a valid refresh token.")
                return
    
    
    def Tesla(): 
        tokens = load_tokens()
        access_tokenTes = tokens.get("access_tokenTesla")
        refresh_tokenTes = tokens.get("refresh_tokenTesla")

        def wake_up(access_tokenTes, Model):
            url = f"https://owner-api.teslamotors.com/api/1/vehicles/{Model}/wake_up"
            headers = {
                "Authorization": f"Bearer {access_tokenTes}"
            }

            try:
                response = requests.post(url, headers=headers)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx errors
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None

        def get_vehicle_data(access_tokenTes,Model):
            url = f"https://owner-api.teslamotors.com/api/1/vehicles/{Model}/vehicle_data"
            headers = {
                "Authorization": f"Bearer {access_tokenTes}"
            }

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx errors
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred: {e}")
                return None
        
        def refresh_access_token(refresh_tokenTes):
            print("in the method")
            url = "https://auth.tesla.com/oauth2/v3/token"
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "grant_type": "refresh_token",
                "client_id": "ownerapi",
                "refresh_token": refresh_tokenTes,
                "scope": "openid email offline_access"
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()  # Raise an exception for 4xx and 5xx errors
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while refreshing access token: {e}")
                emailNotif("Tesphase", "Failed to refresh access token for enphase")
                #Put Email notification if failed to connect
                return None
        
        def get_charging_state(json_response):
            try:
                charging_state = json_response["response"]["charge_state"]["charging_state"]
                return charging_state
            except KeyError:
                print("Error: Charging state not found in the response.")
                return None

        def get_charge_amps(json_response):
            try:
                charge_amps = json_response["response"]["charge_state"]["charge_amps"]
                return charge_amps
            except KeyError:
                print("Error: Charge amps not found in the response.")
                return None
        def stopCharge(accessTemp, carModel): 
            base_url = "https://owner-api.teslamotors.com/api/1/vehicles/"
            endpoint = f"{carModel}/command/charge_stop"
            headers = {"Authorization": f"Bearer {accessTemp}"}
            url = base_url + endpoint
            try:
                response = requests.post(url, headers=headers)
                response.raise_for_status() 
                return response.json()  # If the API returns JSON data in response you can parse it and return it if needed
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                return None
            
        def startCharge(accessTemp, carModel): 
            base_url = "https://owner-api.teslamotors.com/api/1/vehicles/"
            endpoint = f"{carModel}/command/charge_start"
            headers = {"Authorization": f"Bearer {accessTemp}"}
            url = base_url + endpoint
            try:
                response = requests.post(url, headers=headers)
                response.raise_for_status() 
                print("CHARGING SHOUDL HAVE STARTED")
                return response.json()  # If the API returns JSON data in response you can parse it and return it if needed
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                return None
            
        def setChargingAmperage(Model, accessTemp, amps):
            base_url = "https://owner-api.teslamotors.com/api/1/vehicles/"
            endpoint = f"{base_url}{Model}/command/set_charging_amps"
            headers = {
                "Authorization": f"Bearer {accessTemp}",
                "Content-Type": "application/json"
            }
            payload = {
                "charging_amps": amps
            }
            payload_json = json.dumps(payload)
            try:
                response = requests.post(endpoint, headers=headers, data=payload_json)
                if response.status_code >= 200 and response.status_code < 300:
                    print("Charging amperage set successfully.")
                                    #Cross Checking set amps is read-back the same value
                #read_back_amps = get_charge_amps()
                #if doesn't match with amps, then send email, call mayday, stop charging and break.
                else:
                    print(f"Failed to set charging amperage, status code: {response.status_code}")
                    print(response.json()) 

            except requests.exceptions.RequestException as e:
                print(f"Error occurred during the API request: {e}")
            

        # Make the API request and get the JSON response
        wake_up(access_tokenTes, ModelY)
        wake_up(access_tokenTes, Model3)
        json_responseY = get_vehicle_data(access_tokenTes, ModelY)
        json_response3 = get_vehicle_data(access_tokenTes, Model3)

#working on this to catch update if refresh token expires 
        if False:
            response_data = refresh_access_token(refresh_tokenTes)
            print("HEREEEE")
            access_tokenTes = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")
            if access_tokenTes:
                print("Refreshed Access Token:", access_tokenTes)
                tokens = load_tokens()
                tokens["access_tokenTesla"] = access_tokenTes
                save_tokens(tokens)

            else:
                ("Access_token not found in the repsonse")
                
        else: 
            if json_responseY:
                    chargeAmpsTemp = enphase()
                    charging_state = get_charging_state(json_responseY)
                    charging_rate = get_charge_amps(json_responseY)
                    if charging_rate: 
                            print("charging_rate:", charging_rate)
                    if charging_state:
                            print("Charging State:", charging_state)
                            if(charging_state == "Charging"): 
                                print("Model Y is charging")
                                if ((chargeAmpsTemp+charging_rate) <5): 
                                    print(chargeAmpsTemp)
                                    stopCharge(access_tokenTes,ModelY)
                                    emailNotif("Testing", "charging would have turned off now, less than 5 amps left")
                                    emailNotif2("Testing", "charging would have turned off now, less than 5 amps left")
                                    print("Charging turned off now, because less than 5 total amps leftover")
                                else: 
                                    ChargeValue = int(charging_rate + chargeAmpsTemp)
                                    if(ChargeValue > 25): 
                                        setChargingAmperage(ModelY, access_tokenTes,25)
                                        print("CHARGING RATE CHANGED")
                                        emailNotif("Testing", f"charging rate would have changed to {25} car is already charging")
                                        emailNotif2("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                                    else: 
                                        setChargingAmperage(ModelY,access_tokenTes,ChargeValue)
                                        print("CHARGING RATE CHANGED")
                                        emailNotif("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                                        emailNotif2("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                            else: 
                                if(chargeAmpsTemp == None): 
                                    emailNotif('TESPHASE', "none of cars plugged in")
                                elif((chargeAmpsTemp) > 5 and (charging_state == "Stopped")): 
                                    startCharge(access_tokenTes,ModelY)
                                    ChargeValue = int(chargeAmpsTemp + charging_rate)
                                    if(ChargeValue > 25): 
                                        setChargingAmperage(ModelY, access_tokenTes,25)
                                        print("CHARGING RATE CHANGED, setting to only 25.")
                                        emailNotif("Testing", f"charging would have started now, and rate set to {ChargeValue}")
                                        emailNotif2("Testing", f"charging would have started now and rate set to {ChargeValue}")
                                    else: 
                                        setChargingAmperage(ModelY,access_tokenTes,ChargeValue)
                                        print("CHARGING RATE CHANGED, setting to chargeamps var value")
                                        emailNotif("Testing", f"charging would have started now, and rate set to {ChargeValue}")
                                        emailNotif2("Testing", f"charging would have started now and rate set to {ChargeValue}")
                                        print("CHARGING RATE CHANGED, setting to chargeamps var value")
            

            if json_response3:
                    chargeAmpsTemp = enphase() 
                    charging_state = get_charging_state(json_response3)
                    charging_rate = get_charge_amps(json_response3)
                    if charging_rate: 
                            print("charging_rate:", charging_rate)
                    if charging_state:
                            print("Charging State:", charging_state)
                            if(charging_state == "Charging"): 
                                print("Model 3 is charging")
                                #print(ChargeAmps)
                                if ((charging_rate + chargeAmpsTemp) <5): 
                                    print(charging_rate+chargeAmpsTemp)
                                    emailNotif("Testing", "charging would have turned off now, less than 5 amps left")
                                    emailNotif2("Testing", "charging would have turned off now, less than 5 amps left")
                                    stopCharge(access_tokenTes,Model3)
                                    #print("Charging turned off now")
                                else: 
                                    ChargeValue = int(charging_rate + chargeAmpsTemp)
                                    if(ChargeValue > 25): 
                                        setChargingAmperage(Model3, access_tokenTes,25)
                                        emailNotif("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                                        emailNotif2("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                                        print("CHARGING RATE CHANGED")
                                    else: 
                                        setChargingAmperage(Model3,access_tokenTes,ChargeValue)
                                        print("CHARGING RATE CHANGED")
                                        print(chargeAmpsTemp)
                                        print(charging_rate)
                                        emailNotif("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                                        emailNotif2("Testing", f"charging rate would have changed to {ChargeValue} car is already charging")
                            else: 
                                if(chargeAmpsTemp == None): 
                                    emailNotif('TESPHASE', "none of cars plugged in")
                                elif((chargeAmpsTemp) > 5 and (charging_state == "Stopped")): 
                                    startCharge(access_tokenTes,ModelY)
                                    print("STARTING CHARTGING")
                                    #send email possibly?
                                    ChargeValue = int(chargeAmpsTemp)
                                    if(ChargeValue > 25): 
                                        setChargingAmperage(ModelY, access_tokenTes,25)
                                        print("CHARGING RATE CHANGED, set to only 25")
                                        emailNotif("Testing", f"charging would have started now, and rate set to {ChargeValue}")
                                        emailNotif2("Testing", f"charging would have started now and rate set to {ChargeValue}")
                                    else: 
                                        setChargingAmperage(ModelY,access_tokenTes,ChargeValue)
                                        print("CHARGING RATE CHANGED, set to chargeamps value")
                                        emailNotif("Testing", f"charging would have started now, and rate set to {ChargeValue}")
                                        emailNotif2("Testing", f"charging would have started now and rate set to {ChargeValue}")
                                    

                            #if charging_state == "Charging": 
    enphase()  
    Tesla()                      #call enphase and check whether to adjust or not
        
    
        
    
if __name__ == "__main__":
    while True: 
        main()
        time.sleep(900)




