ZenTail

ZenTail is an automated, end-to-end Enterprise Resource Planning (ERP) solution for veterinary clinics. Built with a "self-configuring" architecture, the system eliminates manual setup by orchestrating database schemas and security layers automatically upon execution.

🚀 Quick Start Guide
Step 1: Prerequisites

    Python 3.10+ installed.

    MongoDB Atlas account (Cloud NoSQL database).

    Terminal Access (CMD, PowerShell, or Bash).

Step 2: Automated Installation
Bash

pip install -r requirements.txt

Step 3: Run the Engine
Bash

python app.py

⚡ What Happens Automatically

    Database Synchronization: The script instantly connects to MongoDB Atlas and creates the necessary collections for products, breeds, and appointments if they do not exist.

    Server Initialization: A high-performance Flask server starts with built-in secure session handling and Bcrypt encryption for comprehensive data protection.

    Administrative Setup: The system boots the Admin Dashboard, pre-configured to monitor live site traffic, visitor analytics, and medical logs.

    Service Readiness: REST APIs for clinic geolocation and appointment booking are activated immediately, allowing for instant user interaction.

💎 Unique Features
🐕 Client-Side Services (User Journey)

    Appointment Engine: Navigate to the booking page to test the automated scheduling logic, featuring real-time no-overlap validation to prevent double-bookings.

    Clinic Geolocation: Access the vet locator to find the nearest medical assistance based on live map coordinates.

    Pet Health Profiles: Users can instantly retrieve specific patient data and medical history from the cloud database via the Jinja2 rendering engine.

📊 Administrative Services (ERP Console)

    Live Traffic Monitor: Access /admin to see a real-time counter of unique visitors, active sessions, and page interaction metrics.

    Emergency Dispatch: Submit an "Emergency" request to trigger the visual alert system—a blinking urgent notification that appears on the admin console via CSS keyframes and JS polling.

    Dynamic Content Management: Upload pet breed info or medical catalogs; the server processes files to static/uploads and updates the global gallery instantly without a restart.
