#!/usr/bin/env python3
"""
Test script for Tesphase integration - runs one cycle only
"""
import urllib.request
import urllib.parse
import json
from datetime import datetime
import base64
import hashlib 
import urllib 
import getpass
import requests
import smtplib
import time
from tesla_fleet_api import TeslaFleetAPI

TOKEN_FILE_PATH = "tokens.json"
CLIENT_ID = "522971af7de5da2d7f3fe5301ba5f413"
CLIENT_SECRET = "5673a12f2fabe349d505236db8b8c345" 
sender_email = "krakedlucifer91@gmail.com"
sender_password = "xfrlwexdeezdntjn"
receiver_email = "svishal@gmail.com"
receiver_email2 = "s.akshat@gmail.com"

# Tesla Fleet API vehicle ID (Grey car - Model Y)
VEHICLE_ID = "1493134009886258"
ChargeAmps = 0

def emailNotif(subject, body): 
    print(f"EMAIL NOTIFICATION: {subject}")
    print(f"Body: {body}")
    # Comment out actual email sending for testing
    # message = f"Subject: {subject}\n\n{body}"
    # try:
    #     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #         server.login(sender_email, sender_password)
    #         server.sendmail(sender_email, receiver_email, message)
    #     print("Email sent successfully!")
    # except Exception as e:
    #     print(f"Failed to send email. Error: {e}")

def emailNotif2(subject, body): 
    print(f"EMAIL NOTIFICATION 2: {subject}")
    print(f"Body: {body}")
    # Comment out actual email sending for testing

def load_tokens():
    with open(TOKEN_FILE_PATH, "r") as token_file:
        return json.load(token_file)

def save_tokens(tokens, new_access, new_refresh):
    with open(TOKEN_FILE_PATH, "w") as token_file:
        tokens["access_tokenEnphase"] = new_access
        if new_refresh:
            tokens["refresh_tokenEnphase"] = new_refresh
        json.dump(tokens, token_file, indent=4)

def enphase(): 
    
    def refresh_access_token(refresh_tokenEnph):
        refresh_url = "https://api.enphaseenergy.com/oauth/token"
        
        # Encode the client credentials for the Authorization header
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        credentials_bytes = credentials.encode('ascii')
        base64_credentials = base64.b64encode(credentials_bytes).decode('ascii')
        auth_header = f"Basic {base64_credentials}"

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_tokenEnph
        }
        
        data_encoded = urllib.parse.urlencode(data).encode('ascii')

        try:
            refresh_request = urllib.request.Request(refresh_url, data=data_encoded, headers=headers, method="POST")
            print("Refreshing Enphase token...")
            
            with urllib.request.urlopen(refresh_request) as refresh_response:
                refresh_data = json.loads(refresh_response.read().decode())
                print("Refresh response:", refresh_data)
                
                new_access_token = refresh_data.get("access_token")
                new_refresh_token = refresh_data.get("refresh_token")
                
                if new_access_token:
                    tokens = load_tokens()
                    print("NEW ENPHASE ACCESS TOKEN OBTAINED")
                    tokens["access_tokenEnphase"] = new_access_token
                    if new_refresh_token:
                        tokens["refresh_tokenEnphase"] = new_refresh_token
                    save_tokens(tokens, new_access_token, new_refresh_token)
                    return new_access_token
                else:
                    print("No access token in refresh response")
                    return None

        except urllib.error.URLError as e:
            print(f"Failed to refresh Enphase access_token. Error: {e}")
            if hasattr(e, 'read'):
                error_response = e.read().decode()
                print(f"Error response: {error_response}")
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
        # Get production data
        completeRequest_production = url_production + "?" + "&".join(f"{key}={value}" for key, value in myParam_production.items())
        request_production = urllib.request.Request(completeRequest_production, headers=headers)
        
        with urllib.request.urlopen(request_production) as response_production:
            data_production = json.loads(response_production.read().decode())
            last_interval_production = data_production["intervals"][-1]
            end_at_production = last_interval_production.get('end_at')
            wh_del_production = last_interval_production.get('wh_del')
            production_time = datetime.fromtimestamp(end_at_production).strftime('%Y-%m-%d %H:%M:%S')
            finProduction = wh_del_production * 4  # Convert 15-min to hourly watts
            print(f"Solar Production: {finProduction}W")

    except urllib.error.URLError as e:
        if "HTTP Error 401: Unauthorized" not in str(e):
            emailNotif("TESPHASE URL ERROR", f"Enphase production request failed: {e}")
        print("Enphase access token issue. Attempting refresh...")
        if refresh_tokenEnph:
            access_tokenEnph = refresh_access_token(refresh_tokenEnph)
            if access_tokenEnph:
                print("Token refreshed, restarting...")
                return enphase()  # Recursive call instead of main()
            else:
                return None
        else:
            print("Refresh token is missing")
            return None

    # Get consumption data
    url_consumption = "https://api.enphaseenergy.com/api/v4/systems/4383764/telemetry/consumption_meter"
    myParam_consumption = {"key": "dfdfbbbd4d5687ed46eb2e0f81056bf9"}

    try:
        completeRequest_consumption = url_consumption + "?" + "&".join(f"{key}={value}" for key, value in myParam_consumption.items())
        request_consumption = urllib.request.Request(completeRequest_consumption, headers=headers)
        
        with urllib.request.urlopen(request_consumption) as response_consumption:
            data_consumption = json.loads(response_consumption.read().decode())
            last_interval_consumption = data_consumption["intervals"][-1]
            end_at_consumption = last_interval_consumption.get('end_at')
            wh_del_consumption = last_interval_consumption.get('enwh')
            consumption_time = datetime.fromtimestamp(end_at_consumption).strftime('%Y-%m-%d %H:%M:%S')
            finConsumption = wh_del_consumption * 4  # Convert 15-min to hourly watts
            print(f"Home Consumption: {finConsumption}W")
            
            # Parse times for validation
            production_time = datetime.strptime(production_time, '%Y-%m-%d %H:%M:%S')
            consumption_time = datetime.strptime(consumption_time, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            
            # Calculate time differences
            productionTimeDiff = abs(current_time - production_time).total_seconds() / 60
            consumptionTimeDiff = abs(current_time - consumption_time).total_seconds() / 60
            
            # Check blackout hours (4 PM - 9 PM)
            now = datetime.now().time()
            startBlackout = datetime.strptime("16:00:00", "%H:%M:%S").time()
            endBlackout = datetime.strptime("21:00:00", "%H:%M:%S").time()
            
            if startBlackout <= now <= endBlackout: 
                if finConsumption >= 2000:
                    emailNotif("TESPHASE BLACKOUT WARNING", "High power usage during blackout hours! STOP USING POWER")
                    emailNotif2("TESPHASE BLACKOUT WARNING", "High power usage during blackout hours! STOP USING POWER")
                    return None
                else: 
                    print("In blackout hours - monitoring only")
                    return None
                 
            # Validate data freshness (must be < 30 minutes old)
            if (productionTimeDiff <= 30) and (consumptionTimeDiff <= 30):
                print(f"Data age: {productionTimeDiff:.1f} minutes")
                
                # Calculate excess power available for Tesla charging
                leftoverCharge = finProduction - finConsumption
                ChargeAmps = leftoverCharge / 240  # Convert watts to amps (240V system)
                
                print(f"Excess Power: {leftoverCharge}W")
                print(f"Tesla Charging Amps: {ChargeAmps:.2f}A")
                
                return ChargeAmps
            else: 
                print("ERROR: Data too old (>30 minutes)")
                emailNotif("TESPHASE DATA ERROR", "Solar data is more than 30 minutes old - not reliable for charging")
                emailNotif2("TESPHASE DATA ERROR", "Solar data is more than 30 minutes old - not reliable for charging")
                return None

    except urllib.error.URLError as e:
        if "HTTP Error 401: Unauthorized" not in str(e):
            emailNotif("TESPHASE URL ERROR", f"Enphase consumption request failed: {e}")
        print("Enphase consumption API error")
        return None

def tesla_fleet_control(charge_amps):
    """
    Control Tesla charging using the Fleet API - TEST VERSION
    """
    try:
        print("=== TESLA FLEET API CONTROL (TEST MODE) ===")
        fleet_api = TeslaFleetAPI()
        
        # Wake up the vehicle
        print("Waking up vehicle...")
        wake_result = fleet_api.wake_up_vehicle(VEHICLE_ID)
        if wake_result:
            print("✅ Vehicle wake-up command sent")
        else:
            print("❌ Failed to wake up vehicle")
            return False
        
        # Wait longer for vehicle to wake up
        print("Waiting 15 seconds for vehicle to wake up...")
        time.sleep(15)
        
        # Get current charging state with retry logic
        print("Getting vehicle charging state...")
        charge_state = None
        for attempt in range(3):
            try:
                charge_state = fleet_api.get_charging_state(VEHICLE_ID)
                if charge_state:
                    break
                else:
                    print(f"Attempt {attempt + 1}: No charging state data, retrying...")
                    time.sleep(5)
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error getting charging state: {e}")
                time.sleep(5)
        
        if not charge_state:
            print("❌ Failed to get charging state after multiple attempts")
            print("This might be normal if the vehicle is in deep sleep")
            emailNotif("TESPHASE INFO", "Tesla vehicle not responding - might be in deep sleep")
            return False
        
        current_charging_state = charge_state.get('charging_state', 'Unknown')
        current_charge_amps = charge_state.get('charge_amps', 0)
        battery_level = charge_state.get('battery_level', 0)
        
        print(f"✅ Current Status: {current_charging_state}")
        print(f"Current Charge Rate: {current_charge_amps}A")
        print(f"Battery Level: {battery_level}%")
        
        # Decision logic based on available solar power
        if charge_amps is None:
            print("No solar data available - not controlling charging")
            return False
        
        print(f"Solar power available: {charge_amps:.2f}A")
        
        # TEST MODE: Just log what we would do, don't actually change anything
        if current_charging_state == "Charging":
            print("🔋 Vehicle is currently charging")
            
            if charge_amps < 5:
                print("🧪 TEST MODE: Would stop charging (insufficient solar power)")
                emailNotif("TESPHASE TEST", f"Would stop charging - insufficient solar power ({charge_amps:.1f}A available)")
            else:
                target_amps = min(int(charge_amps), 25)
                if abs(target_amps - current_charge_amps) > 2:
                    print(f"🧪 TEST MODE: Would adjust charge rate to {target_amps}A")
                    emailNotif("TESPHASE TEST", f"Would adjust charge rate to {target_amps}A (solar: {charge_amps:.1f}A)")
                else:
                    print(f"✅ Charge rate already optimal ({current_charge_amps}A)")
                    
        elif current_charging_state in ["Stopped", "Complete", "Disconnected"]:
            print(f"🔌 Vehicle charging is {current_charging_state.lower()}")
            
            if charge_amps > 5:
                target_amps = min(int(charge_amps), 25)
                print(f"🧪 TEST MODE: Would start charging at {target_amps}A")
                emailNotif("TESPHASE TEST", f"Would start charging at {target_amps}A (solar: {charge_amps:.1f}A)")
            else:
                print(f"☀️ Insufficient solar power ({charge_amps:.1f}A) - would not start charging")
                
        else:
            print(f"⚠️ Unknown charging state: {current_charging_state}")
            emailNotif("TESPHASE WARNING", f"Unknown Tesla charging state: {current_charging_state}")
            
        return True
        
    except Exception as e:
        print(f"❌ Tesla Fleet API error: {e}")
        emailNotif("TESPHASE ERROR", f"Tesla Fleet API error: {e}")
        return False

def main():
    # Main execution flow
    print("=== TESPHASE SMART CHARGING SYSTEM (TEST MODE) ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get solar data from Enphase
    print("\n1. Getting solar data from Enphase...")
    charge_amps = enphase()
    
    # Control Tesla charging based on solar data
    print("\n2. Testing Tesla Fleet API integration...")
    if charge_amps is not None:
        tesla_fleet_control(charge_amps)
    else:
        print("No valid solar data - skipping Tesla control")
    
    print("\n=== TEST CYCLE COMPLETE ===")

if __name__ == "__main__":
    main()