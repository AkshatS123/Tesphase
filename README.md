# Tesphase - Tesla & Enphase Smart Solar Charging System

## 🎉 **PRODUCTION READY** - Updated July 19, 2025

**Tesphase** is a smart charging system that automatically controls Tesla vehicle charging based on excess solar power from Enphase solar panels. The system maximizes use of free solar energy while avoiding peak electricity rates.

## Current Status: **FULLY OPERATIONAL** ✅

### **Core Functionality Working:**
- ✅ **Solar Data Collection** - Real-time Enphase production/consumption monitoring
- ✅ **Tesla Fleet API Integration** - Complete vehicle control via new Tesla Fleet API
- ✅ **Smart Charging Logic** - Automatically starts/stops/adjusts charging based on solar excess
- ✅ **Email Notifications** - Real-time alerts for all charging events and system status
- ✅ **Blackout Hour Protection** - Prevents high usage during 4PM-9PM peak hours
- ✅ **Token Management** - Auto-refresh for both Enphase and Tesla tokens

### **Last Testing Results (July 19, 2025):**
- **Solar Production**: 5,576W
- **Home Consumption**: 1,136W  
- **Excess Available**: 4,440W (18.5A for Tesla charging)
- **Vehicle Status**: Grey car (Model Y) - 53% battery, disconnected
- **System Response**: Smart notification to plug in car for 18A charging

## Tesla Fleet API Integration

### Domain Setup - **COMPLETED** ✅
- **Domain**: `https://akshats123.github.io/`
- **Public Key**: Hosted at `https://akshats123.github.io/.well-known/appspecific/com.tesla.3p.public-key.pem`
- **Tesla Registration**: Successfully registered in NA region
- **Virtual Key**: Added and validated

### Authentication - **WORKING** ✅
- **OAuth Flow**: Authorization code flow implemented and tested
- **Token Management**: Auto-refresh implemented with 8-hour token lifecycle
- **Vehicle Access**: Full access to both vehicles confirmed

## Enphase API Integration - **WORKING** ✅

- **Token Auto-Refresh**: Implemented and tested
- **Data Collection**: Production and consumption meters every 15 minutes

### Token Management:
- **Refresh Token**: Valid until 2026
- **Access Token**: Auto-refreshes before expiry
- **Last Refresh**: July 19, 2025 - successful

## File Structure

### **Core Files:**
- **`tesphase_working.py`** - Main production script with Tesla Fleet API integration
- **`tesla_fleet_api.py`** - Tesla Fleet API client class
- **`tokens.json`** - Contains all API tokens (Enphase + Tesla Fleet API)
- **`test_tesphase.py`** - Test script for debugging integration
- **`test_email.py`** - Email functionality test script

### **Configuration Files:**
- **`requirements.txt`** - Python dependencies (requests, urllib3, cryptography)
- **`CLAUDE.md`** - Complete project history and troubleshooting guide

## Email Configuration - **WORKING** ✅

### **Current Setup:**
- **Sender**: krakedlucifer91@gmail.com
- **Recipient**: s.akshat@gmail.com (svishal@gmail.com commented out)
- **Notifications**: All charging events, errors, and blackout warnings

### **Email Types:**
- **Charging Started/Stopped**: Real-time charging status changes
- **Rate Adjustments**: When solar power changes charging speed
- **Plug-In Reminders**: When car is disconnected but solar is available
- **Error Alerts**: API failures, token issues, data problems
- **Blackout Warnings**: High usage during 4PM-9PM peak hours

## Smart Charging Logic

### **Decision Matrix:**
1. **Sufficient Solar (>5A available)**:
   - If car disconnected → Email reminder to plug in
   - If car stopped/complete → Start charging at calculated rate
   - If car charging → Adjust rate to match solar production

2. **Insufficient Solar (<5A available)**:
   - If car charging → Stop charging
   - If car disconnected → No action (monitor only)

3. **Blackout Hours (4PM-9PM)**:
   - Monitor only, no charging changes
   - Alert if home consumption >2000W

### **Safety Features:**
- **Maximum Charge Rate**: 25A (hardware safety limit)
- **Minimum Solar**: 5A required to start/continue charging
- **Data Freshness**: Requires <30-minute-old solar data
- **Peak Hour Protection**: No charging during 4PM-9PM

## Production Deployment

### **Ready for Production:**
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Run Main Script**: `python3 tesphase_working.py`
3. **Monitoring**: Check emails for system status and charging events

### **Monitoring & Maintenance:**
- **Runs every 15 minutes** continuously
- **Auto-token refresh** prevents authentication failures
- **Email alerts** provide real-time system status
- **Detailed logging** for troubleshooting

## Next Steps for Future Development

### **Potential Enhancements:**
1. **Multi-Vehicle Support**: Extend to both Grey car and Red car
2. **Time-of-Use Optimization**: Advanced scheduling for different rate periods
3. **Weather Integration**: Solar forecasting for predictive charging
4. **Web Dashboard**: Real-time monitoring interface
5. **Database Logging**: Historical data storage and analysis

### **Current Limitations:**
- **Single Vehicle**: Currently configured for Grey car only
- **Basic Scheduling**: 15-minute intervals only
- **Email Only**: No web interface or mobile app

---

## **🚀 SYSTEM IS PRODUCTION READY - FULLY TESTED AND OPERATIONAL** 🚀


