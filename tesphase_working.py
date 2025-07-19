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
# receiver_email = "svishal@gmail.com"  # Commented out per request
receiver_email2 = "s.akshat@gmail.com"

# Tesla Fleet API vehicle ID (Grey car - Model Y)
VEHICLE_ID = "1493134009886258"
ChargeAmps = 0


def main():
    def emailNotif(subject, body): 
        message = f"Subject: {subject}\n\n{body}"
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email2, message)  # Using receiver_email2 only
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
                    main()
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
        Control Tesla charging using the Fleet API
        """
        try:
            print("=== TESLA FLEET API CONTROL ===")
            fleet_api = TeslaFleetAPI()
            
            # Wake up the vehicle
            print("Waking up vehicle...")
            wake_result = fleet_api.wake_up_vehicle(VEHICLE_ID)
            if wake_result:
                print("✅ Vehicle wake-up command sent")
            else:
                print("❌ Failed to wake up vehicle")
                return False
            
            # Wait for vehicle to wake up
            time.sleep(5)
            
            # Get current charging state
            print("Getting vehicle charging state...")
            charge_state = fleet_api.get_charging_state(VEHICLE_ID)
            
            if not charge_state:
                print("❌ Failed to get charging state")
                emailNotif("TESPHASE ERROR", "Failed to get Tesla charging state")
                return False
            
            current_charging_state = charge_state.get('charging_state', 'Unknown')
            current_charge_amps = charge_state.get('charge_amps', 0)
            battery_level = charge_state.get('battery_level', 0)
            
            print(f"Current Status: {current_charging_state}")
            print(f"Current Charge Rate: {current_charge_amps}A")
            print(f"Battery Level: {battery_level}%")
            
            # Decision logic based on available solar power
            if charge_amps is None:
                print("No solar data available - not controlling charging")
                return False
            
            if current_charging_state == "Charging":
                print("🔋 Vehicle is currently charging")
                
                if charge_amps < 5:
                    # Stop charging if insufficient solar power
                    print("☀️ Insufficient solar power - stopping charge")
                    stop_result = fleet_api.stop_charging(VEHICLE_ID)
                    if stop_result:
                        print("✅ Charging stopped")
                        emailNotif("TESPHASE", f"Grey car charging stopped - insufficient solar power ({charge_amps:.1f}A available)")
                        emailNotif2("TESPHASE", f"Grey car charging stopped - insufficient solar power ({charge_amps:.1f}A available)")
                    else:
                        print("❌ Failed to stop charging")
                        emailNotif("TESPHASE ERROR", "Failed to stop Grey car charging")
                        
                else:
                    # Adjust charging rate to match solar production
                    target_amps = min(int(charge_amps), 25)  # Cap at 25A max
                    
                    if abs(target_amps - current_charge_amps) > 2:  # Only adjust if significant difference
                        print(f"⚡ Adjusting charge rate to {target_amps}A")
                        amp_result = fleet_api.set_charging_amps(VEHICLE_ID, target_amps)
                        if amp_result:
                            print("✅ Charge rate adjusted")
                            emailNotif("TESPHASE", f"Grey car charge rate adjusted to {target_amps}A (solar: {charge_amps:.1f}A)")
                            emailNotif2("TESPHASE", f"Grey car charge rate adjusted to {target_amps}A (solar: {charge_amps:.1f}A)")
                        else:
                            print("❌ Failed to adjust charge rate")
                            emailNotif("TESPHASE ERROR", "Failed to adjust Grey car charging rate")
                    else:
                        print(f"✅ Charge rate already optimal ({current_charge_amps}A)")
                        # Send status email when charging optimally (every time for now)
                        emailNotif("TESPHASE STATUS", f"Grey car charging optimally at {current_charge_amps}A using solar power ({charge_amps:.1f}A available). Battery: {battery_level}%")
                        emailNotif2("TESPHASE STATUS", f"Grey car charging optimally at {current_charge_amps}A using solar power ({charge_amps:.1f}A available). Battery: {battery_level}%")
                        
            elif current_charging_state in ["Stopped", "Complete", "Disconnected"]:
                print(f"🔌 Vehicle charging is {current_charging_state.lower()}")
                
                if charge_amps > 5:
                    # Start charging if sufficient solar power
                    target_amps = min(int(charge_amps), 25)  # Cap at 25A max
                    
                    if current_charging_state == "Disconnected":
                        # Handle disconnected vehicle specifically
                        print("🔌 Grey car not plugged in - cannot start charging")
                        emailNotif("TESPHASE - PLUG IN CAR", f"Grey car (Model Y) is not plugged in. Please plug in to charge at {target_amps}A with available solar power ({charge_amps:.1f}A)")
                        emailNotif2("TESPHASE - PLUG IN CAR", f"Grey car (Model Y) is not plugged in. Please plug in to charge at {target_amps}A with available solar power ({charge_amps:.1f}A)")
                    else:
                        # Vehicle is stopped/complete but plugged in
                        print(f"☀️ Starting charge at {target_amps}A")
                        start_result = fleet_api.start_charging(VEHICLE_ID)
                        if start_result:
                            print("✅ Charging started")
                            # Set charging rate
                            time.sleep(2)  # Brief pause before setting amps
                            amp_result = fleet_api.set_charging_amps(VEHICLE_ID, target_amps)
                            if amp_result:
                                print(f"✅ Charge rate set to {target_amps}A")
                                emailNotif("TESPHASE", f"Grey car charging started at {target_amps}A (solar: {charge_amps:.1f}A)")
                                emailNotif2("TESPHASE", f"Grey car charging started at {target_amps}A (solar: {charge_amps:.1f}A)")
                            else:
                                print("❌ Failed to set charge rate")
                                emailNotif("TESPHASE ERROR", "Grey car started charging but failed to set rate")
                        else:
                            print("❌ Failed to start charging")
                            emailNotif("TESPHASE ERROR", "Failed to start Grey car charging")
                        
                else:
                    print(f"☀️ Insufficient solar power ({charge_amps:.1f}A) - not starting charge")
                    
            else:
                print(f"⚠️ Unknown charging state: {current_charging_state}")
                emailNotif("TESPHASE WARNING", f"Unknown Tesla charging state: {current_charging_state}")
                
            return True
            
        except Exception as e:
            print(f"❌ Tesla Fleet API error: {e}")
            emailNotif("TESPHASE ERROR", f"Tesla Fleet API error: {e}")
            return False
    
    # Main execution flow
    print("=== TESPHASE SMART CHARGING SYSTEM ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get solar data from Enphase
    charge_amps = enphase()
    
    # Control Tesla charging based on solar data
    if charge_amps is not None:
        tesla_fleet_control(charge_amps)
    else:
        print("No valid solar data - skipping Tesla control")
    
    print("=== CYCLE COMPLETE ===\n")


if __name__ == "__main__":
    while True: 
        main()
        time.sleep(900)  # 15 minute intervals