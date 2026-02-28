#!/usr/bin/env python3
"""
Manual question seed for MD-102 and MS-102.
These are hand-crafted questions based on official Microsoft exam objectives.

Usage:
    python3 seed_manual.py
"""

import json
import hashlib
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(Path(__file__).parent.parent / ".env.local")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set"); sys.exit(1)


# ─── MD-102: Endpoint Administrator ──────────────────────────────────────────

MD102_QUESTIONS = [
    # ── Windows Autopilot ──
    {
        "module": "Deployment",
        "topic": "Windows Autopilot",
        "questionText": "You need to deploy Windows 11 to 500 new laptops with zero-touch provisioning. Users should be able to sign in with their Microsoft Entra ID credentials and have the device automatically enrolled in Intune. Which deployment method should you use?",
        "answers": [
            {"id": "a", "text": "Windows Autopilot user-driven mode", "isCorrect": True},
            {"id": "b", "text": "Microsoft Deployment Toolkit (MDT)", "isCorrect": False},
            {"id": "c", "text": "Windows Autopilot self-deploying mode", "isCorrect": False},
            {"id": "d", "text": "In-place upgrade", "isCorrect": False},
        ],
        "explanation": "Windows Autopilot user-driven mode enables zero-touch deployment where users sign in with Entra ID credentials and devices are automatically enrolled in Intune without IT needing to image the device.",
        "difficulty": 2,
    },
    {
        "module": "Deployment",
        "topic": "Windows Autopilot",
        "questionText": "A company deploys kiosk devices that should automatically enroll in Intune and configure themselves without any user interaction. Which Windows Autopilot profile type should you configure?",
        "answers": [
            {"id": "a", "text": "Self-deploying mode", "isCorrect": True},
            {"id": "b", "text": "User-driven mode", "isCorrect": False},
            {"id": "c", "text": "Pre-provisioned mode", "isCorrect": False},
            {"id": "d", "text": "Existing device mode", "isCorrect": False},
        ],
        "explanation": "Self-deploying mode is designed for kiosk or shared devices that need to configure themselves without any user interaction during OOBE.",
        "difficulty": 2,
    },
    {
        "module": "Deployment",
        "topic": "Windows Autopilot",
        "questionText": "You need to reduce enrollment time for new devices delivered to remote users. IT should pre-configure the device before the user receives it, but the user should still complete OOBE with their own credentials. Which Autopilot mode should you use?",
        "answers": [
            {"id": "a", "text": "Pre-provisioned (White Glove) mode", "isCorrect": True},
            {"id": "b", "text": "Self-deploying mode", "isCorrect": False},
            {"id": "c", "text": "User-driven mode", "isCorrect": False},
            {"id": "d", "text": "Existing device mode", "isCorrect": False},
        ],
        "explanation": "Pre-provisioned (White Glove) mode lets IT pre-provision the device then ship it to the user, who completes a shortened OOBE with their own credentials.",
        "difficulty": 3,
    },

    # ── Intune Enrollment ──
    {
        "module": "Device Management",
        "topic": "Intune Enrollment",
        "questionText": "Users in your organization have personal iOS devices they want to use for work email. You need to manage only work data on these devices without affecting personal data. Which Intune enrollment type should you use?",
        "answers": [
            {"id": "a", "text": "Device enrollment with App Protection Policies", "isCorrect": False},
            {"id": "b", "text": "BYOD enrollment with User Enrollment", "isCorrect": True},
            {"id": "c", "text": "Automated Device Enrollment (ADE)", "isCorrect": False},
            {"id": "d", "text": "Device Enrollment Manager (DEM)", "isCorrect": False},
        ],
        "explanation": "iOS User Enrollment (BYOD) creates a separation between work and personal data, allowing MDM management of only the work portion without full device control.",
        "difficulty": 2,
    },
    {
        "module": "Device Management",
        "topic": "Intune Enrollment",
        "questionText": "You need to bulk-enroll 200 Android devices into Intune. The devices are corporate-owned dedicated devices for warehouse workers. Which enrollment method is most appropriate?",
        "answers": [
            {"id": "a", "text": "Android Enterprise dedicated device enrollment", "isCorrect": True},
            {"id": "b", "text": "Android device administrator enrollment", "isCorrect": False},
            {"id": "c", "text": "Android Enterprise personally-owned work profile", "isCorrect": False},
            {"id": "d", "text": "BYOD enrollment", "isCorrect": False},
        ],
        "explanation": "Android Enterprise dedicated device enrollment is designed for corporate-owned, single-use devices like kiosks or shared warehouse devices.",
        "difficulty": 2,
    },

    # ── Compliance Policies ──
    {
        "module": "Device Compliance",
        "topic": "Compliance Policies",
        "questionText": "You create an Intune compliance policy requiring BitLocker encryption. A device is non-compliant because BitLocker is not enabled. What happens to the device by default if no actions for non-compliance are configured?",
        "answers": [
            {"id": "a", "text": "The device is marked non-compliant but no action is taken immediately", "isCorrect": True},
            {"id": "b", "text": "The device is immediately blocked from accessing company resources", "isCorrect": False},
            {"id": "c", "text": "The device is automatically wiped", "isCorrect": False},
            {"id": "d", "text": "The user receives an email notification immediately", "isCorrect": False},
        ],
        "explanation": "By default, devices marked as non-compliant are only marked as such in Intune. Blocking access or other actions require Conditional Access policies or explicit non-compliance actions.",
        "difficulty": 2,
    },
    {
        "module": "Device Compliance",
        "topic": "Compliance Policies",
        "questionText": "A compliance policy requires a minimum OS version of Windows 11 22H2. A device running Windows 11 21H2 attempts to access Exchange Online. What must be configured to block this device's access?",
        "answers": [
            {"id": "a", "text": "A Conditional Access policy that requires device compliance", "isCorrect": True},
            {"id": "b", "text": "An Intune device configuration profile", "isCorrect": False},
            {"id": "c", "text": "An App Protection Policy", "isCorrect": False},
            {"id": "d", "text": "A Windows Update ring policy", "isCorrect": False},
        ],
        "explanation": "Intune compliance policies alone only mark devices as compliant or not. To enforce access control, you must combine compliance policies with Azure AD/Entra ID Conditional Access.",
        "difficulty": 3,
    },

    # ── App Protection ──
    {
        "module": "App Management",
        "topic": "App Protection Policies",
        "questionText": "You need to prevent users from copying data from the Outlook mobile app to personal apps on their unmanaged iOS devices. Which Intune feature should you configure?",
        "answers": [
            {"id": "a", "text": "App Protection Policies (MAM without enrollment)", "isCorrect": True},
            {"id": "b", "text": "Device Configuration profile", "isCorrect": False},
            {"id": "c", "text": "Device Compliance policy", "isCorrect": False},
            {"id": "d", "text": "Conditional Access policy", "isCorrect": False},
        ],
        "explanation": "App Protection Policies (MAM-WE) protect app data on unmanaged devices without requiring device enrollment, making them ideal for BYOD scenarios.",
        "difficulty": 2,
    },
    {
        "module": "App Management",
        "topic": "App Protection Policies",
        "questionText": "An employee leaves the company. Their personal iPhone has both corporate Outlook data and personal apps. You need to remove only the corporate data. What action should you perform in Intune?",
        "answers": [
            {"id": "a", "text": "Selective wipe (retire)", "isCorrect": True},
            {"id": "b", "text": "Full wipe", "isCorrect": False},
            {"id": "c", "text": "Remote lock", "isCorrect": False},
            {"id": "d", "text": "Reset passcode", "isCorrect": False},
        ],
        "explanation": "Selective wipe (also called 'retire') removes only managed app data and policies from the device, leaving personal data intact.",
        "difficulty": 1,
    },

    # ── BitLocker ──
    {
        "module": "Security",
        "topic": "BitLocker",
        "questionText": "You need to enforce BitLocker encryption on all Windows 11 corporate devices enrolled in Intune. Where should you configure this requirement?",
        "answers": [
            {"id": "a", "text": "Endpoint security > Disk encryption profile in Intune", "isCorrect": True},
            {"id": "b", "text": "Device compliance policy in Intune", "isCorrect": False},
            {"id": "c", "text": "Windows Update rings in Intune", "isCorrect": False},
            {"id": "d", "text": "Conditional Access policy in Entra ID", "isCorrect": False},
        ],
        "explanation": "BitLocker encryption is configured and enforced via Intune Endpoint security > Disk encryption profiles, which push the actual encryption settings to devices.",
        "difficulty": 2,
    },
    {
        "module": "Security",
        "topic": "BitLocker",
        "questionText": "A user forgot their BitLocker recovery key. Where can an IT administrator find the BitLocker recovery key for an Intune-managed device?",
        "answers": [
            {"id": "a", "text": "In the Intune device blade under Monitor > Recovery keys", "isCorrect": True},
            {"id": "b", "text": "In Active Directory Users and Computers", "isCorrect": False},
            {"id": "c", "text": "In the Azure Key Vault", "isCorrect": False},
            {"id": "d", "text": "In the device's local TPM chip only", "isCorrect": False},
        ],
        "explanation": "For Intune-managed devices, BitLocker recovery keys are automatically escrowed to Intune and accessible from the device's Monitor > Recovery keys blade.",
        "difficulty": 1,
    },

    # ── Configuration Profiles ──
    {
        "module": "Device Configuration",
        "topic": "Configuration Profiles",
        "questionText": "You need to configure a custom Start menu layout for all Windows 11 devices in your organization via Intune. Which profile type should you create?",
        "answers": [
            {"id": "a", "text": "Device configuration profile > Templates > Device restrictions", "isCorrect": True},
            {"id": "b", "text": "Endpoint security profile", "isCorrect": False},
            {"id": "c", "text": "Compliance policy", "isCorrect": False},
            {"id": "d", "text": "Windows Autopilot profile", "isCorrect": False},
        ],
        "explanation": "Device restrictions configuration profiles in Intune include settings for customizing the Windows Start menu, taskbar, and other UI elements.",
        "difficulty": 2,
    },
    {
        "module": "Device Configuration",
        "topic": "Configuration Profiles",
        "questionText": "You need to configure a Wi-Fi profile that automatically connects devices to your corporate network when they are within range. Which Intune profile type should you use?",
        "answers": [
            {"id": "a", "text": "Device configuration profile > Wi-Fi", "isCorrect": True},
            {"id": "b", "text": "App configuration policy", "isCorrect": False},
            {"id": "c", "text": "Endpoint security > Firewall", "isCorrect": False},
            {"id": "d", "text": "Windows Autopilot deployment profile", "isCorrect": False},
        ],
        "explanation": "Wi-Fi device configuration profiles in Intune push wireless network settings including SSID, authentication method, and certificates to enrolled devices.",
        "difficulty": 1,
    },

    # ── Update Management ──
    {
        "module": "Update Management",
        "topic": "Windows Update Rings",
        "questionText": "You need to configure Windows Update for Business to defer feature updates by 30 days for all standard users, while IT staff get updates immediately. What should you create in Intune?",
        "answers": [
            {"id": "a", "text": "Two Windows Update rings assigned to different groups", "isCorrect": True},
            {"id": "b", "text": "A single compliance policy with deferral settings", "isCorrect": False},
            {"id": "c", "text": "Two Windows Autopilot profiles", "isCorrect": False},
            {"id": "d", "text": "A Windows LAPS policy", "isCorrect": False},
        ],
        "explanation": "Windows Update rings in Intune let you control deferral periods for different groups. Creating separate rings for IT and standard users gives each group different update timing.",
        "difficulty": 2,
    },
    {
        "module": "Update Management",
        "topic": "Windows Update Rings",
        "questionText": "A critical security patch is released. You need to ensure all managed Windows devices install it within 24 hours regardless of current deferral settings. What should you do in Intune?",
        "answers": [
            {"id": "a", "text": "Create an Expedite Windows quality update policy", "isCorrect": True},
            {"id": "b", "text": "Delete the existing Windows Update ring", "isCorrect": False},
            {"id": "c", "text": "Increase the compliance grace period", "isCorrect": False},
            {"id": "d", "text": "Trigger a remote sync for all devices", "isCorrect": False},
        ],
        "explanation": "Expedited quality updates in Intune override deferral settings and force urgent patches to install as quickly as possible, bypassing configured deferral periods.",
        "difficulty": 2,
    },

    # ── Entra ID Join ──
    {
        "module": "Identity",
        "topic": "Entra ID Join",
        "questionText": "A user's Windows 11 device is Azure AD Joined. The user is locked out and does not remember their PIN or password. What can an IT admin do remotely to help the user?",
        "answers": [
            {"id": "a", "text": "Use the Reset passcode action in Intune", "isCorrect": False},
            {"id": "b", "text": "Rotate the Windows LAPS local administrator password and use it to unlock", "isCorrect": True},
            {"id": "c", "text": "Perform a remote wipe", "isCorrect": False},
            {"id": "d", "text": "Re-enroll the device in Autopilot", "isCorrect": False},
        ],
        "explanation": "Windows LAPS (Local Administrator Password Solution) managed via Intune stores a local admin password in Entra ID that IT can retrieve to regain access to locked devices.",
        "difficulty": 3,
    },

    # ── Defender for Endpoint ──
    {
        "module": "Security",
        "topic": "Defender for Endpoint",
        "questionText": "You need to onboard Windows devices to Microsoft Defender for Endpoint using Intune. Which Intune feature should you use?",
        "answers": [
            {"id": "a", "text": "Endpoint security > Endpoint detection and response (EDR) policy", "isCorrect": True},
            {"id": "b", "text": "Device configuration > Templates > Antivirus", "isCorrect": False},
            {"id": "c", "text": "Windows Autopilot deployment profile", "isCorrect": False},
            {"id": "d", "text": "Compliance policy > Windows Health Attestation", "isCorrect": False},
        ],
        "explanation": "The EDR policy in Intune Endpoint security handles the onboarding configuration package that connects Windows devices to the Microsoft Defender for Endpoint service.",
        "difficulty": 2,
    },

    # ── App Deployment ──
    {
        "module": "App Management",
        "topic": "App Deployment",
        "questionText": "You need to deploy a line-of-business (LOB) Windows application (.intunewin) to managed devices. The app must be installed silently in the background. Which app type should you use in Intune?",
        "answers": [
            {"id": "a", "text": "Windows app (Win32)", "isCorrect": True},
            {"id": "b", "text": "Microsoft Store app", "isCorrect": False},
            {"id": "c", "text": "Web link", "isCorrect": False},
            {"id": "d", "text": "Built-in app", "isCorrect": False},
        ],
        "explanation": "Win32 apps (.intunewin format) support silent installation with custom install/uninstall commands and detection rules, making them ideal for LOB application deployment.",
        "difficulty": 1,
    },
    {
        "module": "App Management",
        "topic": "App Deployment",
        "questionText": "You assign a required app to a device group in Intune. The app fails to install on some devices. Where should you look first to diagnose the issue?",
        "answers": [
            {"id": "a", "text": "Intune > Apps > Monitor > App install status", "isCorrect": True},
            {"id": "b", "text": "Azure Monitor Logs", "isCorrect": False},
            {"id": "c", "text": "Microsoft Endpoint Configuration Manager", "isCorrect": False},
            {"id": "d", "text": "Windows Event Viewer on the affected device", "isCorrect": False},
        ],
        "explanation": "The App install status report in Intune shows installation status per device and user, including error codes for failed installations.",
        "difficulty": 1,
    },

    # ── Remote Actions ──
    {
        "module": "Device Management",
        "topic": "Remote Actions",
        "questionText": "A company laptop is reported stolen. You need to prevent any data on the device from being accessed while also preserving the ability to recover the device if found. What Intune action should you take?",
        "answers": [
            {"id": "a", "text": "Remote lock", "isCorrect": False},
            {"id": "b", "text": "Wipe", "isCorrect": False},
            {"id": "c", "text": "Retire", "isCorrect": False},
            {"id": "d", "text": "Wipe with 'Retain enrollment state' enabled", "isCorrect": True},
        ],
        "explanation": "Wiping with 'Retain enrollment state' resets the device to factory settings and removes corporate data, but keeps the Autopilot registration so the device re-enrolls automatically when recovered.",
        "difficulty": 3,
    },

    # ── Conditional Access ──
    {
        "module": "Identity",
        "topic": "Conditional Access",
        "questionText": "You need to ensure that only Intune-compliant devices can access SharePoint Online. Users on non-compliant devices should see a message explaining why access is blocked. What should you configure?",
        "answers": [
            {"id": "a", "text": "Conditional Access policy requiring device compliance for SharePoint", "isCorrect": True},
            {"id": "b", "text": "Intune App Protection Policy for SharePoint", "isCorrect": False},
            {"id": "c", "text": "SharePoint permission settings", "isCorrect": False},
            {"id": "d", "text": "Intune device compliance policy action", "isCorrect": False},
        ],
        "explanation": "Conditional Access policies in Entra ID enforce that only compliant devices (as reported by Intune) can access specific cloud apps like SharePoint Online.",
        "difficulty": 2,
    },

    # ── Intune Roles ──
    {
        "module": "Administration",
        "topic": "Intune Roles",
        "questionText": "A helpdesk technician needs to be able to perform remote actions (lock, wipe) on devices in Intune but should not be able to modify compliance policies or configuration profiles. Which built-in Intune role should you assign?",
        "answers": [
            {"id": "a", "text": "Help Desk Operator", "isCorrect": True},
            {"id": "b", "text": "Intune Service Administrator", "isCorrect": False},
            {"id": "c", "text": "Read Only Operator", "isCorrect": False},
            {"id": "d", "text": "Application Manager", "isCorrect": False},
        ],
        "explanation": "The Help Desk Operator role grants permissions to perform remote device actions and view device/user information without the ability to change policies.",
        "difficulty": 2,
    },

    # ── Co-management ──
    {
        "module": "Deployment",
        "topic": "Co-management",
        "questionText": "Your organization uses Configuration Manager (SCCM) to manage Windows devices. You want to gradually move workloads to Intune while keeping Configuration Manager. Which feature enables this?",
        "answers": [
            {"id": "a", "text": "Co-management", "isCorrect": True},
            {"id": "b", "text": "Windows Autopilot", "isCorrect": False},
            {"id": "c", "text": "Tenant attach", "isCorrect": False},
            {"id": "d", "text": "Cloud management gateway", "isCorrect": False},
        ],
        "explanation": "Co-management allows devices to be simultaneously managed by both Configuration Manager and Intune, with the ability to slide individual workloads to Intune over time.",
        "difficulty": 2,
    },
]


# ─── MS-102: Microsoft 365 Administrator ─────────────────────────────────────

MS102_QUESTIONS = [
    # ── Tenant Configuration ──
    {
        "module": "Tenant Management",
        "topic": "Tenant Configuration",
        "questionText": "You are setting up a new Microsoft 365 tenant. You need to verify your custom domain (contoso.com) so users can sign in with contoso.com email addresses. What must you add to your public DNS zone?",
        "answers": [
            {"id": "a", "text": "An MX record pointing to Microsoft 365", "isCorrect": False},
            {"id": "b", "text": "A TXT record with the verification code provided by Microsoft 365", "isCorrect": True},
            {"id": "c", "text": "An A record pointing to the Microsoft 365 portal", "isCorrect": False},
            {"id": "d", "text": "A CNAME record for autodiscover", "isCorrect": False},
        ],
        "explanation": "Microsoft 365 domain verification requires adding a TXT record (or sometimes an MX record) to your public DNS zone to prove ownership of the domain.",
        "difficulty": 1,
    },
    {
        "module": "Tenant Management",
        "topic": "Tenant Configuration",
        "questionText": "Your organization needs to prevent users from creating Microsoft 365 Groups. Which admin center should you use to configure this restriction?",
        "answers": [
            {"id": "a", "text": "Microsoft Entra admin center > Groups settings", "isCorrect": True},
            {"id": "b", "text": "Microsoft 365 admin center > Settings", "isCorrect": False},
            {"id": "c", "text": "Exchange admin center > Groups", "isCorrect": False},
            {"id": "d", "text": "SharePoint admin center", "isCorrect": False},
        ],
        "explanation": "The policy to restrict Microsoft 365 Group creation to specific users is configured in the Microsoft Entra admin center under Groups > General settings.",
        "difficulty": 2,
    },

    # ── Identity and Access ──
    {
        "module": "Identity Management",
        "topic": "Microsoft Entra ID",
        "questionText": "You need to require MFA for all users accessing Microsoft 365 from outside the corporate network, but not from inside. What is the most efficient approach?",
        "answers": [
            {"id": "a", "text": "Enable Security Defaults in Entra ID", "isCorrect": False},
            {"id": "b", "text": "Create a Conditional Access policy with a Named Location as an exclusion condition", "isCorrect": True},
            {"id": "c", "text": "Configure per-user MFA for all users", "isCorrect": False},
            {"id": "d", "text": "Configure ADFS claims rules", "isCorrect": False},
        ],
        "explanation": "Conditional Access policies with Named Locations allow you to require MFA only when users are outside trusted IP ranges (corporate network), providing the most granular control.",
        "difficulty": 2,
    },
    {
        "module": "Identity Management",
        "topic": "Microsoft Entra ID",
        "questionText": "A user account is at risk of compromise based on Microsoft Entra ID Identity Protection signals. You need to automatically force a password reset for risky users. What should you configure?",
        "answers": [
            {"id": "a", "text": "User risk policy in Microsoft Entra ID Protection", "isCorrect": True},
            {"id": "b", "text": "Sign-in risk policy in Microsoft Entra ID Protection", "isCorrect": False},
            {"id": "c", "text": "A Conditional Access policy requiring MFA", "isCorrect": False},
            {"id": "d", "text": "Smart Lockout settings", "isCorrect": False},
        ],
        "explanation": "The User risk policy in Entra ID Protection can automatically block access or require a secure password change when a user's risk level reaches the configured threshold.",
        "difficulty": 2,
    },
    {
        "module": "Identity Management",
        "topic": "Microsoft Entra ID",
        "questionText": "You need to allow external business partners (from partner.com) to access a specific SharePoint site using their own credentials. Which feature should you use?",
        "answers": [
            {"id": "a", "text": "Microsoft Entra B2B collaboration", "isCorrect": True},
            {"id": "b", "text": "Microsoft Entra B2C", "isCorrect": False},
            {"id": "c", "text": "Active Directory Federation Services (ADFS)", "isCorrect": False},
            {"id": "d", "text": "Microsoft Entra External Identities for customers", "isCorrect": False},
        ],
        "explanation": "Microsoft Entra B2B collaboration lets you invite external partners to access your resources using their own organizational credentials, without managing their accounts.",
        "difficulty": 1,
    },

    # ── Exchange Online ──
    {
        "module": "Messaging",
        "topic": "Exchange Online",
        "questionText": "You need to prevent users in your organization from sending email to an external domain (competitor.com). Which Exchange Online feature should you configure?",
        "answers": [
            {"id": "a", "text": "Mail flow rule (transport rule) blocking messages to competitor.com", "isCorrect": True},
            {"id": "b", "text": "Anti-spam outbound policy", "isCorrect": False},
            {"id": "c", "text": "Safe Links policy in Defender for Office 365", "isCorrect": False},
            {"id": "d", "text": "DLP policy in Microsoft Purview", "isCorrect": False},
        ],
        "explanation": "Mail flow (transport) rules in Exchange Online can block, redirect, or modify messages based on conditions such as recipient domain.",
        "difficulty": 2,
    },
    {
        "module": "Messaging",
        "topic": "Exchange Online",
        "questionText": "A user who left the organization had a shared mailbox with important email. You need to retain access to the mailbox content for 90 days after the user license is removed. What should you do?",
        "answers": [
            {"id": "a", "text": "Convert the user mailbox to a shared mailbox before removing the license", "isCorrect": True},
            {"id": "b", "text": "Apply an eDiscovery hold to the mailbox", "isCorrect": False},
            {"id": "c", "text": "Enable litigation hold on the mailbox", "isCorrect": False},
            {"id": "d", "text": "Export the mailbox to a PST file", "isCorrect": False},
        ],
        "explanation": "Converting a user mailbox to a shared mailbox allows it to persist without a license (up to 50GB), preserving the content and giving delegated users continued access.",
        "difficulty": 2,
    },

    # ── Teams ──
    {
        "module": "Collaboration",
        "topic": "Microsoft Teams",
        "questionText": "You need to prevent users from adding external participants to Microsoft Teams meetings. Where should you configure this restriction?",
        "answers": [
            {"id": "a", "text": "Teams admin center > Meetings > Meeting policies", "isCorrect": True},
            {"id": "b", "text": "Microsoft 365 admin center > Settings > Org settings", "isCorrect": False},
            {"id": "c", "text": "Microsoft Entra admin center > External identities", "isCorrect": False},
            {"id": "d", "text": "Teams admin center > Users > Guest access", "isCorrect": False},
        ],
        "explanation": "Teams meeting policies control per-user or per-group settings for meetings, including whether external participants can be added.",
        "difficulty": 2,
    },
    {
        "module": "Collaboration",
        "topic": "Microsoft Teams",
        "questionText": "You need to configure Teams so that only IT-approved apps can be installed by users. What should you configure in the Teams admin center?",
        "answers": [
            {"id": "a", "text": "App permission policies", "isCorrect": True},
            {"id": "b", "text": "App setup policies", "isCorrect": False},
            {"id": "c", "text": "Meeting policies", "isCorrect": False},
            {"id": "d", "text": "Messaging policies", "isCorrect": False},
        ],
        "explanation": "App permission policies in the Teams admin center control which apps users can install and use, allowing you to block all third-party apps or allow only specific ones.",
        "difficulty": 2,
    },

    # ── SharePoint Online ──
    {
        "module": "Collaboration",
        "topic": "SharePoint Online",
        "questionText": "You need to prevent users from sharing SharePoint files with people outside your organization. Which SharePoint admin setting should you configure?",
        "answers": [
            {"id": "a", "text": "Set the external sharing level to 'Only people in your organization'", "isCorrect": True},
            {"id": "b", "text": "Configure a Conditional Access policy for SharePoint", "isCorrect": False},
            {"id": "c", "text": "Apply a DLP policy to SharePoint", "isCorrect": False},
            {"id": "d", "text": "Enable SharePoint Information Barriers", "isCorrect": False},
        ],
        "explanation": "The external sharing level in SharePoint admin center controls whether and how files can be shared with external users, from completely restricted to anyone with a link.",
        "difficulty": 1,
    },

    # ── Defender for Office 365 ──
    {
        "module": "Security",
        "topic": "Defender for Office 365",
        "questionText": "Users report receiving phishing emails that appear to be from your CEO. You need to protect against email sender impersonation. Which Microsoft Defender for Office 365 feature should you configure?",
        "answers": [
            {"id": "a", "text": "Anti-phishing policy with impersonation protection", "isCorrect": True},
            {"id": "b", "text": "Safe Attachments policy", "isCorrect": False},
            {"id": "c", "text": "Safe Links policy", "isCorrect": False},
            {"id": "d", "text": "Anti-spam policy", "isCorrect": False},
        ],
        "explanation": "Anti-phishing policies in Defender for Office 365 include impersonation protection that identifies and flags emails that appear to be from specific people or domains you protect.",
        "difficulty": 2,
    },
    {
        "module": "Security",
        "topic": "Defender for Office 365",
        "questionText": "You need to protect users from malicious links in emails that are clicked hours after delivery. Which Defender for Office 365 feature provides this protection?",
        "answers": [
            {"id": "a", "text": "Safe Links with time-of-click protection", "isCorrect": True},
            {"id": "b", "text": "Safe Attachments with dynamic delivery", "isCorrect": False},
            {"id": "c", "text": "Zero-hour auto purge (ZAP)", "isCorrect": False},
            {"id": "d", "text": "Threat Explorer", "isCorrect": False},
        ],
        "explanation": "Safe Links rewrites URLs and checks them at time-of-click, so even links that were safe on delivery can be blocked if they later become malicious.",
        "difficulty": 2,
    },

    # ── Purview / Compliance ──
    {
        "module": "Compliance",
        "topic": "Microsoft Purview",
        "questionText": "You need to automatically classify and label documents containing credit card numbers in SharePoint Online. Which Microsoft Purview feature should you use?",
        "answers": [
            {"id": "a", "text": "Sensitive information types with auto-labeling policies", "isCorrect": True},
            {"id": "b", "text": "Retention labels", "isCorrect": False},
            {"id": "c", "text": "eDiscovery", "isCorrect": False},
            {"id": "d", "text": "Communication compliance", "isCorrect": False},
        ],
        "explanation": "Auto-labeling policies in Microsoft Purview use sensitive information types (like credit card patterns) to automatically apply sensitivity labels to content in SharePoint and Exchange.",
        "difficulty": 2,
    },
    {
        "module": "Compliance",
        "topic": "Microsoft Purview",
        "questionText": "Your organization must retain all email for 7 years to meet regulatory requirements. Which feature should you configure in Microsoft Purview?",
        "answers": [
            {"id": "a", "text": "Retention policy applied to Exchange Online", "isCorrect": True},
            {"id": "b", "text": "eDiscovery hold", "isCorrect": False},
            {"id": "c", "text": "Litigation hold on all mailboxes", "isCorrect": False},
            {"id": "d", "text": "Sensitivity labels with encryption", "isCorrect": False},
        ],
        "explanation": "Retention policies in Microsoft Purview allow you to define how long content must be kept across Microsoft 365 services including Exchange, ensuring regulatory compliance.",
        "difficulty": 1,
    },
    {
        "module": "Compliance",
        "topic": "Data Loss Prevention",
        "questionText": "You need to prevent users from emailing documents containing Social Security Numbers outside the organization. Which Microsoft Purview feature should you configure?",
        "answers": [
            {"id": "a", "text": "Data Loss Prevention (DLP) policy", "isCorrect": True},
            {"id": "b", "text": "Communication compliance policy", "isCorrect": False},
            {"id": "c", "text": "Insider risk management policy", "isCorrect": False},
            {"id": "d", "text": "Retention policy", "isCorrect": False},
        ],
        "explanation": "DLP policies detect sensitive information types (like SSNs) in content and apply protective actions such as blocking external sharing or sending policy tips to users.",
        "difficulty": 1,
    },

    # ── Licensing ──
    {
        "module": "Tenant Management",
        "topic": "Licensing",
        "questionText": "You need to automatically assign Microsoft 365 E3 licenses to all members of the 'Sales' group in Entra ID. Which licensing feature should you use?",
        "answers": [
            {"id": "a", "text": "Group-based licensing in Microsoft Entra ID", "isCorrect": True},
            {"id": "b", "text": "Subscription management in Microsoft 365 admin center", "isCorrect": False},
            {"id": "c", "text": "PowerShell with Set-MsolUserLicense", "isCorrect": False},
            {"id": "d", "text": "Microsoft Cost Management", "isCorrect": False},
        ],
        "explanation": "Group-based licensing in Microsoft Entra ID automatically assigns or removes licenses when users join or leave a group, eliminating manual license management.",
        "difficulty": 1,
    },

    # ── Hybrid ──
    {
        "module": "Identity Management",
        "topic": "Hybrid Identity",
        "questionText": "Your organization has an on-premises Active Directory. You need to synchronize user accounts to Microsoft Entra ID while keeping passwords managed on-premises. Which tool and feature should you use?",
        "answers": [
            {"id": "a", "text": "Microsoft Entra Connect with Password Hash Sync", "isCorrect": True},
            {"id": "b", "text": "Microsoft Entra Connect with Pass-through Authentication", "isCorrect": False},
            {"id": "c", "text": "ADFS with federation", "isCorrect": False},
            {"id": "d", "text": "Microsoft Entra Cloud Sync with directory sync only", "isCorrect": False},
        ],
        "explanation": "Microsoft Entra Connect with Password Hash Sync synchronizes a hash of user password hashes to Entra ID, enabling cloud authentication while keeping the source of truth on-premises.",
        "difficulty": 2,
    },
    {
        "module": "Identity Management",
        "topic": "Hybrid Identity",
        "questionText": "You need to synchronize on-premises AD to Entra ID with minimal infrastructure. Your on-premises AD has multiple domains in different forests. Which solution is best suited?",
        "answers": [
            {"id": "a", "text": "Microsoft Entra Cloud Sync", "isCorrect": True},
            {"id": "b", "text": "Microsoft Entra Connect (full version)", "isCorrect": False},
            {"id": "c", "text": "ADFS", "isCorrect": False},
            {"id": "d", "text": "Microsoft Entra Connect Health only", "isCorrect": False},
        ],
        "explanation": "Microsoft Entra Cloud Sync uses a lightweight provisioning agent and is designed for multi-forest scenarios with minimal on-premises infrastructure requirements.",
        "difficulty": 3,
    },

    # ── Reports and Monitoring ──
    {
        "module": "Monitoring",
        "topic": "Reports and Monitoring",
        "questionText": "You need to view a report showing which Microsoft 365 services users are actively using and how much storage they are consuming. Where should you look?",
        "answers": [
            {"id": "a", "text": "Microsoft 365 admin center > Reports > Usage", "isCorrect": True},
            {"id": "b", "text": "Microsoft Entra admin center > Monitoring", "isCorrect": False},
            {"id": "c", "text": "Microsoft Purview > Audit", "isCorrect": False},
            {"id": "d", "text": "Microsoft 365 Defender portal > Reports", "isCorrect": False},
        ],
        "explanation": "The Usage reports in the Microsoft 365 admin center provide activity and adoption data for all Microsoft 365 services including storage consumption.",
        "difficulty": 1,
    },
    {
        "module": "Monitoring",
        "topic": "Reports and Monitoring",
        "questionText": "You need to investigate a suspicious sign-in from an unfamiliar location for a specific user. Which Microsoft Entra report should you check?",
        "answers": [
            {"id": "a", "text": "Sign-in logs in Microsoft Entra admin center", "isCorrect": True},
            {"id": "b", "text": "Audit logs in Microsoft Entra admin center", "isCorrect": False},
            {"id": "c", "text": "Usage & insights report", "isCorrect": False},
            {"id": "d", "text": "Microsoft 365 admin center > Active Users report", "isCorrect": False},
        ],
        "explanation": "The Entra ID Sign-in logs provide details about each sign-in event including location, device, application, and risk level, making them ideal for investigating suspicious activity.",
        "difficulty": 1,
    },

    # ── Service Health ──
    {
        "module": "Tenant Management",
        "topic": "Service Health",
        "questionText": "Users report that they cannot access Exchange Online. You need to quickly determine if there is a Microsoft service outage. Where should you check first?",
        "answers": [
            {"id": "a", "text": "Microsoft 365 admin center > Health > Service health", "isCorrect": True},
            {"id": "b", "text": "Microsoft Entra admin center > Diagnose and solve problems", "isCorrect": False},
            {"id": "c", "text": "Microsoft 365 Defender portal > Incidents", "isCorrect": False},
            {"id": "d", "text": "Azure status page at status.azure.com", "isCorrect": False},
        ],
        "explanation": "The Service health dashboard in the Microsoft 365 admin center shows real-time status of all Microsoft 365 services and is the first place to check during an outage.",
        "difficulty": 1,
    },

    # ── SSPR ──
    {
        "module": "Identity Management",
        "topic": "Self-Service Password Reset",
        "questionText": "You need to allow users to reset their own passwords without contacting the helpdesk, including writing the new password back to on-premises Active Directory. What must be configured?",
        "answers": [
            {"id": "a", "text": "Self-service password reset (SSPR) with password writeback enabled in Entra Connect", "isCorrect": True},
            {"id": "b", "text": "SSPR only — writeback happens automatically", "isCorrect": False},
            {"id": "c", "text": "ADFS with password sync", "isCorrect": False},
            {"id": "d", "text": "Privileged Identity Management (PIM)", "isCorrect": False},
        ],
        "explanation": "SSPR requires the Password Writeback feature to be enabled in Microsoft Entra Connect to propagate password changes back to on-premises Active Directory.",
        "difficulty": 2,
    },
]


def seed_questions(cert_code: str, questions: list, conn):
    """Seed a list of questions for a cert."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get certification ID
    cursor.execute('SELECT id FROM "Certification" WHERE code = %s', (cert_code,))
    cert_row = cursor.fetchone()
    if not cert_row:
        print(f"  ⚠️  Certification {cert_code} not found in DB — run seed_sample.py first")
        cursor.close()
        return 0

    cert_id = cert_row["id"]
    inserted = 0

    modules_map = {}
    topics_map = {}

    for q in questions:
        module_title = q["module"]
        topic_title = q["topic"]

        # Upsert module
        if module_title not in modules_map:
            cursor.execute("""
                INSERT INTO "Module" (id, "certificationId", title, "orderIndex", "createdAt")
                VALUES (gen_random_uuid()::text, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING RETURNING id
            """, (cert_id, module_title, len(modules_map)))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    'SELECT id FROM "Module" WHERE "certificationId" = %s AND title = %s',
                    (cert_id, module_title)
                )
                row = cursor.fetchone()
            if row:
                modules_map[module_title] = row["id"]

        module_id = modules_map.get(module_title)
        if not module_id:
            continue

        # Upsert topic
        topic_key = (module_title, topic_title)
        if topic_key not in topics_map:
            cursor.execute("""
                INSERT INTO "Topic" (id, "moduleId", title, "msLearnUrl", "orderIndex", "createdAt")
                VALUES (gen_random_uuid()::text, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING RETURNING id
            """, (module_id, topic_title, "https://learn.microsoft.com", len(topics_map)))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    'SELECT id FROM "Topic" WHERE "moduleId" = %s AND title = %s',
                    (module_id, topic_title)
                )
                row = cursor.fetchone()
            if row:
                topics_map[topic_key] = row["id"]

        topic_id = topics_map.get(topic_key)

        q_hash = hashlib.sha256(q["questionText"].lower().strip().encode()).hexdigest()[:16]

        cursor.execute("""
            INSERT INTO "Question" (
                id, "certificationId", "moduleId", "topicId",
                "questionText", "questionType", answers, explanation,
                source, "sourceUrl", "documentationLinks",
                difficulty, "isActive", "createdAt", "updatedAt"
            )
            VALUES (
                gen_random_uuid()::text, %s, %s, %s,
                %s, 'SINGLE_CHOICE', %s, %s,
                'MICROSOFT', 'https://learn.microsoft.com', '[]',
                %s, true, NOW(), NOW()
            )
            ON CONFLICT DO NOTHING
        """, (
            cert_id, module_id, topic_id,
            q["questionText"],
            json.dumps(q["answers"]),
            q.get("explanation", ""),
            q.get("difficulty", 2),
        ))

        if cursor.rowcount > 0:
            inserted += 1

    conn.commit()
    cursor.close()
    return inserted


def main():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        print("\nSeeding MD-102 manual questions...")
        n = seed_questions("MD-102", MD102_QUESTIONS, conn)
        print(f"  ✓ Inserted {n} new questions for MD-102 ({len(MD102_QUESTIONS)} total written)")

        print("\nSeeding MS-102 manual questions...")
        n = seed_questions("MS-102", MS102_QUESTIONS, conn)
        print(f"  ✓ Inserted {n} new questions for MS-102 ({len(MS102_QUESTIONS)} total written)")
    finally:
        conn.close()

    print("\n✓ Manual seeding complete!")


if __name__ == "__main__":
    main()
