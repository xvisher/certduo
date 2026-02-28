#!/usr/bin/env python3
"""
Seeds the database with sample questions for all four certifications.
Use this to get the app working immediately without running the web scraper.

Usage:
    python3 seed_sample.py
    python3 seed_sample.py --cert AZ-900
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(Path(__file__).parent.parent / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)


# ─── AZ-900: Azure Fundamentals ──────────────────────────────────────────────

AZ900_QUESTIONS = [
    # ── Cloud Concepts ──
    {
        "module": "Cloud Concepts",
        "topic": "Cloud Service Types",
        "questionText": "Which cloud service model gives you the most control over the underlying operating system and installed software?",
        "answers": [
            {"id": "a", "text": "Software as a Service (SaaS)", "isCorrect": False},
            {"id": "b", "text": "Platform as a Service (PaaS)", "isCorrect": False},
            {"id": "c", "text": "Infrastructure as a Service (IaaS)", "isCorrect": True},
            {"id": "d", "text": "Function as a Service (FaaS)", "isCorrect": False},
        ],
        "explanation": "IaaS provides virtualized computing infrastructure over the internet. You manage the OS, middleware, and applications, giving you the most control of the three main service models.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-overview", "title": "Cloud Service Types Overview"}],
        "difficulty": 1,
    },
    {
        "module": "Cloud Concepts",
        "topic": "Cloud Service Types",
        "questionText": "A company wants to deploy a web application without managing the underlying servers, OS patches, or runtime environment. Which cloud service model best fits this need?",
        "answers": [
            {"id": "a", "text": "IaaS", "isCorrect": False},
            {"id": "b", "text": "PaaS", "isCorrect": True},
            {"id": "c", "text": "SaaS", "isCorrect": False},
            {"id": "d", "text": "On-premises", "isCorrect": False},
        ],
        "explanation": "PaaS lets developers build and deploy applications without managing underlying infrastructure. The cloud provider handles the OS, runtime, and middleware.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-overview", "title": "Cloud Service Types Overview"}],
        "difficulty": 1,
    },
    {
        "module": "Cloud Concepts",
        "topic": "Cloud Deployment Models",
        "questionText": "An organization needs to keep sensitive patient data on-premises due to compliance requirements, but wants to use Azure for non-sensitive workloads. Which cloud deployment model should they use?",
        "answers": [
            {"id": "a", "text": "Public cloud", "isCorrect": False},
            {"id": "b", "text": "Private cloud", "isCorrect": False},
            {"id": "c", "text": "Hybrid cloud", "isCorrect": True},
            {"id": "d", "text": "Community cloud", "isCorrect": False},
        ],
        "explanation": "Hybrid cloud combines on-premises (or private cloud) infrastructure with public cloud resources, allowing organizations to keep sensitive data on-premises while leveraging cloud scalability for other workloads.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/architecture/framework/", "title": "Azure Architecture Framework"}],
        "difficulty": 1,
    },
    {
        "module": "Cloud Concepts",
        "topic": "Benefits of Cloud",
        "questionText": "Which benefit of cloud computing allows you to increase or decrease resources based on demand without paying for unused capacity?",
        "answers": [
            {"id": "a", "text": "High availability", "isCorrect": False},
            {"id": "b", "text": "Elasticity", "isCorrect": True},
            {"id": "c", "text": "Fault tolerance", "isCorrect": False},
            {"id": "d", "text": "Disaster recovery", "isCorrect": False},
        ],
        "explanation": "Elasticity is the ability to automatically scale resources up or down based on demand. This means you only pay for what you use and can handle traffic spikes without manual intervention.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/scale-partition", "title": "Performance Efficiency - Scale"}],
        "difficulty": 1,
    },
    {
        "module": "Cloud Concepts",
        "topic": "Benefits of Cloud",
        "questionText": "What does high availability mean in the context of cloud computing?",
        "answers": [
            {"id": "a", "text": "The ability to recover from a catastrophic regional failure", "isCorrect": False},
            {"id": "b", "text": "The ability to scale resources up or down automatically", "isCorrect": False},
            {"id": "c", "text": "The ability to keep services running with minimal downtime", "isCorrect": True},
            {"id": "d", "text": "The ability to distribute load across multiple servers", "isCorrect": False},
        ],
        "explanation": "High availability refers to a system's ability to remain operational and accessible for a high percentage of time, minimizing downtime through redundancy and failover mechanisms.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/reliability/overview", "title": "Azure Reliability"}],
        "difficulty": 1,
    },
    {
        "module": "Cloud Concepts",
        "topic": "Cloud Expenditure Models",
        "questionText": "Which expenditure model do cloud services primarily use?",
        "answers": [
            {"id": "a", "text": "Capital Expenditure (CapEx)", "isCorrect": False},
            {"id": "b", "text": "Operational Expenditure (OpEx)", "isCorrect": True},
            {"id": "c", "text": "Both CapEx and OpEx equally", "isCorrect": False},
            {"id": "d", "text": "Neither CapEx nor OpEx", "isCorrect": False},
        ],
        "explanation": "Cloud services shift spending from CapEx (large upfront investments in hardware) to OpEx (ongoing operating costs), allowing organizations to pay for only what they consume.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview", "title": "Azure Cost Management"}],
        "difficulty": 1,
    },
    # ── Azure Architecture ──
    {
        "module": "Azure Architecture and Services",
        "topic": "Regions and Availability Zones",
        "questionText": "What is an Azure Availability Zone?",
        "answers": [
            {"id": "a", "text": "A separate Azure region located in a different country", "isCorrect": False},
            {"id": "b", "text": "A physically separate datacenter within an Azure region with independent power, cooling, and networking", "isCorrect": True},
            {"id": "c", "text": "A logical grouping of Azure resources for billing purposes", "isCorrect": False},
            {"id": "d", "text": "A DNS zone for routing traffic between regions", "isCorrect": False},
        ],
        "explanation": "Availability Zones are physically separate datacenters within a single Azure region. Each zone has independent power, cooling, and networking, providing protection against datacenter-level failures.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/availability-zones/overview", "title": "Azure Availability Zones"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Regions and Availability Zones",
        "questionText": "You need to protect an application from a complete Azure datacenter failure. What should you deploy?",
        "answers": [
            {"id": "a", "text": "Multiple instances in the same datacenter", "isCorrect": False},
            {"id": "b", "text": "Instances across multiple Availability Zones in the same region", "isCorrect": True},
            {"id": "c", "text": "A single large virtual machine with more CPU and RAM", "isCorrect": False},
            {"id": "d", "text": "A load balancer in a single datacenter", "isCorrect": False},
        ],
        "explanation": "Deploying across multiple Availability Zones ensures your application survives a complete datacenter failure since each AZ is a separate physical facility.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/availability-zones/overview", "title": "Azure Availability Zones"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Resource Organization",
        "questionText": "What is an Azure Resource Group?",
        "answers": [
            {"id": "a", "text": "A billing container that groups subscriptions together", "isCorrect": False},
            {"id": "b", "text": "A logical container that holds related Azure resources for a solution", "isCorrect": True},
            {"id": "c", "text": "A set of Azure policies applied to a subscription", "isCorrect": False},
            {"id": "d", "text": "A network boundary that isolates virtual machines", "isCorrect": False},
        ],
        "explanation": "A Resource Group is a container that holds related Azure resources. Resources in a group share the same lifecycle and can be managed, deployed, and deleted together.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal", "title": "Azure Resource Groups"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Resource Organization",
        "questionText": "Which Azure resource management hierarchy, from broadest to most specific, is correct?",
        "answers": [
            {"id": "a", "text": "Subscription → Management Group → Resource Group → Resource", "isCorrect": False},
            {"id": "b", "text": "Resource → Resource Group → Subscription → Management Group", "isCorrect": False},
            {"id": "c", "text": "Management Group → Subscription → Resource Group → Resource", "isCorrect": True},
            {"id": "d", "text": "Management Group → Resource Group → Subscription → Resource", "isCorrect": False},
        ],
        "explanation": "The Azure hierarchy from broadest to most specific is: Management Groups (group subscriptions), Subscriptions (group resource groups), Resource Groups (group resources), and Resources (individual services).",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/governance/management-groups/overview", "title": "Azure Management Groups"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Compute Services",
        "questionText": "Which Azure service lets you run containerized applications without managing virtual machines or container orchestration infrastructure?",
        "answers": [
            {"id": "a", "text": "Azure Virtual Machines", "isCorrect": False},
            {"id": "b", "text": "Azure Kubernetes Service (AKS)", "isCorrect": False},
            {"id": "c", "text": "Azure Container Instances (ACI)", "isCorrect": True},
            {"id": "d", "text": "Azure App Service", "isCorrect": False},
        ],
        "explanation": "Azure Container Instances (ACI) lets you run containers directly without managing VMs or a container orchestration platform. It's the fastest and simplest way to run containers in Azure.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/container-instances/container-instances-overview", "title": "Azure Container Instances"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Compute Services",
        "questionText": "What is Azure Functions primarily used for?",
        "answers": [
            {"id": "a", "text": "Hosting full web applications with persistent state", "isCorrect": False},
            {"id": "b", "text": "Running small pieces of code (functions) in response to events without managing servers", "isCorrect": True},
            {"id": "c", "text": "Managing virtual machine scale sets", "isCorrect": False},
            {"id": "d", "text": "Storing large amounts of unstructured data", "isCorrect": False},
        ],
        "explanation": "Azure Functions is a serverless compute service that lets you run event-triggered code without managing infrastructure. You only pay for the execution time of your functions.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview", "title": "Azure Functions"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Storage Services",
        "questionText": "Which Azure Storage type is best suited for storing unstructured data like images, videos, and documents?",
        "answers": [
            {"id": "a", "text": "Azure Table Storage", "isCorrect": False},
            {"id": "b", "text": "Azure Queue Storage", "isCorrect": False},
            {"id": "c", "text": "Azure Blob Storage", "isCorrect": True},
            {"id": "d", "text": "Azure File Storage", "isCorrect": False},
        ],
        "explanation": "Azure Blob Storage is optimized for storing massive amounts of unstructured data, such as text, images, videos, and backups. 'Blob' stands for Binary Large Object.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction", "title": "Azure Blob Storage"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Database Services",
        "questionText": "Which Azure database service is a fully managed relational database compatible with SQL Server?",
        "answers": [
            {"id": "a", "text": "Azure Cosmos DB", "isCorrect": False},
            {"id": "b", "text": "Azure SQL Database", "isCorrect": True},
            {"id": "c", "text": "Azure Table Storage", "isCorrect": False},
            {"id": "d", "text": "Azure Cache for Redis", "isCorrect": False},
        ],
        "explanation": "Azure SQL Database is a fully managed relational database service built on SQL Server engine. Microsoft handles patching, backups, and availability automatically.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview", "title": "Azure SQL Database"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Database Services",
        "questionText": "Azure Cosmos DB is best described as which type of database?",
        "answers": [
            {"id": "a", "text": "A relational database optimized for OLAP workloads", "isCorrect": False},
            {"id": "b", "text": "A globally distributed, multi-model NoSQL database", "isCorrect": True},
            {"id": "c", "text": "A graph database exclusively for social network analysis", "isCorrect": False},
            {"id": "d", "text": "A time-series database for IoT telemetry", "isCorrect": False},
        ],
        "explanation": "Azure Cosmos DB is a globally distributed, multi-model NoSQL database that supports document, key-value, graph, and column-family data models with single-digit millisecond latency.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/cosmos-db/introduction", "title": "Azure Cosmos DB"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Architecture and Services",
        "topic": "Networking Services",
        "questionText": "Which Azure service provides a private, isolated network environment in the cloud?",
        "answers": [
            {"id": "a", "text": "Azure ExpressRoute", "isCorrect": False},
            {"id": "b", "text": "Azure Virtual Network (VNet)", "isCorrect": True},
            {"id": "c", "text": "Azure DNS", "isCorrect": False},
            {"id": "d", "text": "Azure Content Delivery Network", "isCorrect": False},
        ],
        "explanation": "Azure Virtual Network (VNet) is the fundamental building block for private networks in Azure. It enables Azure resources to securely communicate with each other, the internet, and on-premises networks.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview", "title": "Azure Virtual Network"}],
        "difficulty": 1,
    },
    # ── Azure Management and Governance ──
    {
        "module": "Azure Management and Governance",
        "topic": "Identity and Access",
        "questionText": "What is Microsoft Entra ID (formerly Azure Active Directory) primarily used for?",
        "answers": [
            {"id": "a", "text": "Managing physical servers in Azure datacenters", "isCorrect": False},
            {"id": "b", "text": "Identity and access management for cloud-based resources", "isCorrect": True},
            {"id": "c", "text": "Storing relational data for enterprise applications", "isCorrect": False},
            {"id": "d", "text": "Monitoring network traffic and detecting threats", "isCorrect": False},
        ],
        "explanation": "Microsoft Entra ID (formerly Azure AD) is Microsoft's cloud-based identity and access management service. It helps employees sign in and access resources in external and internal resources.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/active-directory-whatis", "title": "Microsoft Entra ID"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Identity and Access",
        "questionText": "What does Role-Based Access Control (RBAC) in Azure allow you to do?",
        "answers": [
            {"id": "a", "text": "Encrypt data at rest in Azure storage accounts", "isCorrect": False},
            {"id": "b", "text": "Assign granular permissions to users, groups, and applications for Azure resources", "isCorrect": True},
            {"id": "c", "text": "Monitor and log all activity across an Azure subscription", "isCorrect": False},
            {"id": "d", "text": "Create network rules to filter inbound and outbound traffic", "isCorrect": False},
        ],
        "explanation": "Azure RBAC lets you manage who has access to Azure resources, what they can do with those resources, and what areas they have access to — using built-in or custom roles.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/role-based-access-control/overview", "title": "Azure RBAC"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Cost Management",
        "questionText": "Which Azure tool helps you estimate the cost of Azure products and services before you deploy them?",
        "answers": [
            {"id": "a", "text": "Azure Cost Management + Billing", "isCorrect": False},
            {"id": "b", "text": "Azure Pricing Calculator", "isCorrect": True},
            {"id": "c", "text": "Azure Advisor", "isCorrect": False},
            {"id": "d", "text": "Total Cost of Ownership (TCO) Calculator", "isCorrect": False},
        ],
        "explanation": "The Azure Pricing Calculator allows you to configure Azure services and see an estimated monthly cost before you deploy, helping with budgeting and planning.",
        "documentationLinks": [{"url": "https://azure.microsoft.com/en-us/pricing/calculator/", "title": "Azure Pricing Calculator"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Cost Management",
        "questionText": "Which tool helps organizations estimate the savings from migrating on-premises workloads to Azure by comparing on-premises costs with Azure costs?",
        "answers": [
            {"id": "a", "text": "Azure Pricing Calculator", "isCorrect": False},
            {"id": "b", "text": "Azure Cost Management", "isCorrect": False},
            {"id": "c", "text": "Total Cost of Ownership (TCO) Calculator", "isCorrect": True},
            {"id": "d", "text": "Azure Advisor", "isCorrect": False},
        ],
        "explanation": "The TCO Calculator estimates the cost savings of moving workloads to Azure by comparing your current on-premises infrastructure costs (hardware, software, operations) against Azure pricing.",
        "documentationLinks": [{"url": "https://azure.microsoft.com/en-us/pricing/tco/calculator/", "title": "TCO Calculator"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Governance Tools",
        "questionText": "What is Azure Policy primarily used for?",
        "answers": [
            {"id": "a", "text": "Monitoring performance metrics of Azure resources", "isCorrect": False},
            {"id": "b", "text": "Enforcing organizational standards and compliance requirements across Azure resources", "isCorrect": True},
            {"id": "c", "text": "Managing user identities and access permissions", "isCorrect": False},
            {"id": "d", "text": "Automating the deployment of Azure resources", "isCorrect": False},
        ],
        "explanation": "Azure Policy helps enforce organizational standards and assess compliance at scale. It evaluates Azure resources for non-compliance with assigned policies, such as requiring specific tags or restricting resource types.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/governance/policy/overview", "title": "Azure Policy"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Monitoring Tools",
        "questionText": "Which Azure service collects, analyzes, and acts on telemetry data from your Azure and on-premises environments?",
        "answers": [
            {"id": "a", "text": "Azure Advisor", "isCorrect": False},
            {"id": "b", "text": "Azure Service Health", "isCorrect": False},
            {"id": "c", "text": "Azure Monitor", "isCorrect": True},
            {"id": "d", "text": "Microsoft Defender for Cloud", "isCorrect": False},
        ],
        "explanation": "Azure Monitor collects metrics and logs from your Azure resources, helps you understand how your applications are performing, and identifies issues affecting them.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/azure-monitor/overview", "title": "Azure Monitor"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Security Tools",
        "questionText": "What is Microsoft Defender for Cloud?",
        "answers": [
            {"id": "a", "text": "An antivirus solution for Azure virtual machines only", "isCorrect": False},
            {"id": "b", "text": "A cloud security posture management and threat protection service", "isCorrect": True},
            {"id": "c", "text": "A firewall service for filtering network traffic", "isCorrect": False},
            {"id": "d", "text": "A DDoS protection service for Azure resources", "isCorrect": False},
        ],
        "explanation": "Microsoft Defender for Cloud is a security posture management and threat protection tool. It strengthens the security posture of your cloud resources and protects workloads in Azure, hybrid, and multicloud environments.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction", "title": "Microsoft Defender for Cloud"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Deployment Tools",
        "questionText": "What is Azure Resource Manager (ARM)?",
        "answers": [
            {"id": "a", "text": "A monitoring tool for tracking Azure resource usage and costs", "isCorrect": False},
            {"id": "b", "text": "The deployment and management service for Azure that handles all resource operations", "isCorrect": True},
            {"id": "c", "text": "A virtual machine orchestration tool similar to Kubernetes", "isCorrect": False},
            {"id": "d", "text": "A database management service for relational workloads", "isCorrect": False},
        ],
        "explanation": "Azure Resource Manager (ARM) is the deployment and management service for Azure. It processes all API requests for creating, updating, and deleting Azure resources, and handles authentication through Entra ID.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview", "title": "Azure Resource Manager"}],
        "difficulty": 2,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Service Level Agreements",
        "questionText": "What does an Azure Service Level Agreement (SLA) define?",
        "answers": [
            {"id": "a", "text": "The pricing tiers available for a given Azure service", "isCorrect": False},
            {"id": "b", "text": "Microsoft's commitments for uptime and connectivity for Azure services", "isCorrect": True},
            {"id": "c", "text": "The data residency requirements for Azure services", "isCorrect": False},
            {"id": "d", "text": "The support response times for Azure technical issues", "isCorrect": False},
        ],
        "explanation": "An SLA describes Microsoft's commitments for uptime and connectivity. If a service falls below its SLA, Microsoft may provide service credits as compensation.",
        "documentationLinks": [{"url": "https://azure.microsoft.com/en-us/support/legal/sla/", "title": "Azure SLAs"}],
        "difficulty": 1,
    },
    {
        "module": "Azure Management and Governance",
        "topic": "Service Level Agreements",
        "questionText": "Deploying an application across two Availability Zones in the same region will result in which composite SLA compared to a single-zone deployment?",
        "answers": [
            {"id": "a", "text": "Lower, because there are more components that can fail", "isCorrect": False},
            {"id": "b", "text": "Higher, because redundancy reduces the probability of total failure", "isCorrect": True},
            {"id": "c", "text": "The same, because SLA is determined by the region not the zone", "isCorrect": False},
            {"id": "d", "text": "Zero, because Microsoft does not provide SLAs for multi-zone deployments", "isCorrect": False},
        ],
        "explanation": "Deploying across multiple Availability Zones increases the composite SLA because it reduces the probability of both zones failing simultaneously. Azure guarantees 99.99% uptime for VMs deployed across AZs vs 99.9% for single VMs.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/reliability/overview", "title": "Azure Reliability"}],
        "difficulty": 3,
    },
]


# ─── AZ-104: Azure Administrator (sample subset) ─────────────────────────────

AZ104_QUESTIONS = [
    {
        "module": "Manage Azure Identities and Governance",
        "topic": "Microsoft Entra ID",
        "questionText": "You need to allow users from a partner company to access resources in your Azure subscription without creating new accounts. Which Entra ID feature should you use?",
        "answers": [
            {"id": "a", "text": "Entra ID B2C", "isCorrect": False},
            {"id": "b", "text": "Entra ID B2B (External Identities)", "isCorrect": True},
            {"id": "c", "text": "Entra ID Domain Services", "isCorrect": False},
            {"id": "d", "text": "Conditional Access", "isCorrect": False},
        ],
        "explanation": "Entra ID B2B (Business-to-Business) allows you to invite external users from partner organizations to collaborate using their own credentials, without needing to manage separate accounts.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/active-directory/external-identities/what-is-b2b", "title": "Entra ID B2B"}],
        "difficulty": 2,
    },
    {
        "module": "Manage Azure Identities and Governance",
        "topic": "Role-Based Access Control",
        "questionText": "What is the least-privileged built-in RBAC role that allows a user to read all resources in a subscription but not make any changes?",
        "answers": [
            {"id": "a", "text": "Contributor", "isCorrect": False},
            {"id": "b", "text": "Owner", "isCorrect": False},
            {"id": "c", "text": "Reader", "isCorrect": True},
            {"id": "d", "text": "User Access Administrator", "isCorrect": False},
        ],
        "explanation": "The Reader role grants read-only access to all resources without the ability to make changes. It follows the principle of least privilege for view-only scenarios.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles", "title": "Azure Built-in Roles"}],
        "difficulty": 1,
    },
    {
        "module": "Implement and Manage Storage",
        "topic": "Azure Storage Accounts",
        "questionText": "You need to store large amounts of data that is rarely accessed but must be retained for 7 years for compliance. Which storage tier is most cost-effective?",
        "answers": [
            {"id": "a", "text": "Hot tier", "isCorrect": False},
            {"id": "b", "text": "Cool tier", "isCorrect": False},
            {"id": "c", "text": "Archive tier", "isCorrect": True},
            {"id": "d", "text": "Premium tier", "isCorrect": False},
        ],
        "explanation": "The Archive tier has the lowest storage cost but highest retrieval cost, making it ideal for data that is rarely accessed. It is suitable for compliance, backup, and long-term retention scenarios.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview", "title": "Azure Blob Storage Access Tiers"}],
        "difficulty": 2,
    },
    {
        "module": "Deploy and Manage Azure Compute Resources",
        "topic": "Virtual Machines",
        "questionText": "What Azure VM feature allows you to save costs by committing to a 1 or 3 year usage plan?",
        "answers": [
            {"id": "a", "text": "Spot Instances", "isCorrect": False},
            {"id": "b", "text": "Reserved Instances", "isCorrect": True},
            {"id": "c", "text": "Azure Hybrid Benefit", "isCorrect": False},
            {"id": "d", "text": "Dev/Test pricing", "isCorrect": False},
        ],
        "explanation": "Azure Reserved VM Instances provide a significant discount (up to 72%) compared to pay-as-you-go pricing by committing to a 1 or 3 year term for predictable workloads.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/save-compute-costs-reservations", "title": "Azure Reservations"}],
        "difficulty": 2,
    },
    {
        "module": "Monitor and Maintain Azure Resources",
        "topic": "Azure Monitor",
        "questionText": "Which Azure Monitor feature allows you to query and analyze log data using KQL (Kusto Query Language)?",
        "answers": [
            {"id": "a", "text": "Azure Metrics", "isCorrect": False},
            {"id": "b", "text": "Azure Log Analytics", "isCorrect": True},
            {"id": "c", "text": "Azure Alerts", "isCorrect": False},
            {"id": "d", "text": "Azure Workbooks", "isCorrect": False},
        ],
        "explanation": "Azure Log Analytics is a tool within Azure Monitor that lets you write and run KQL queries against collected log data from across your Azure environment.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview", "title": "Azure Log Analytics"}],
        "difficulty": 2,
    },
]


# ─── MD-102: Endpoint Administrator (sample subset) ──────────────────────────

MD102_QUESTIONS = [
    {
        "module": "Deploy Windows Client",
        "topic": "Autopilot",
        "questionText": "What is Windows Autopilot primarily used for?",
        "answers": [
            {"id": "a", "text": "Patching Windows devices with security updates", "isCorrect": False},
            {"id": "b", "text": "Automating the setup and pre-configuration of new Windows devices", "isCorrect": True},
            {"id": "c", "text": "Encrypting Windows device storage with BitLocker", "isCorrect": False},
            {"id": "d", "text": "Remotely wiping lost or stolen devices", "isCorrect": False},
        ],
        "explanation": "Windows Autopilot is a collection of technologies used to set up and pre-configure new Windows devices, enabling a zero-touch deployment experience where users can set up devices directly out of the box.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/autopilot/overview", "title": "Windows Autopilot Overview"}],
        "difficulty": 1,
    },
    {
        "module": "Manage Identity and Compliance",
        "topic": "Intune Enrollment",
        "questionText": "Which Microsoft Intune enrollment method is best for corporate-owned devices that employees will use exclusively for work?",
        "answers": [
            {"id": "a", "text": "BYOD (Bring Your Own Device) enrollment", "isCorrect": False},
            {"id": "b", "text": "Autopilot with Entra ID Join", "isCorrect": True},
            {"id": "c", "text": "Mobile Application Management (MAM) without enrollment", "isCorrect": False},
            {"id": "d", "text": "Group Policy enrollment", "isCorrect": False},
        ],
        "explanation": "Autopilot with Entra ID Join is ideal for corporate-owned devices, providing a zero-touch deployment experience with full Intune management capabilities.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/intune/fundamentals/windows-enrollment-overview", "title": "Windows Enrollment in Intune"}],
        "difficulty": 2,
    },
    {
        "module": "Manage, Maintain, and Protect Devices",
        "topic": "Compliance Policies",
        "questionText": "In Microsoft Intune, what happens when a device fails to meet a compliance policy?",
        "answers": [
            {"id": "a", "text": "The device is immediately wiped", "isCorrect": False},
            {"id": "b", "text": "The device is marked as non-compliant and can be blocked from accessing corporate resources via Conditional Access", "isCorrect": True},
            {"id": "c", "text": "The user's account is permanently disabled in Entra ID", "isCorrect": False},
            {"id": "d", "text": "The device enrollment is automatically revoked", "isCorrect": False},
        ],
        "explanation": "When a device fails compliance, Intune marks it as non-compliant. When combined with Entra ID Conditional Access policies, non-compliant devices can be blocked from accessing corporate resources like email and SharePoint.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/intune/protect/device-compliance-get-started", "title": "Intune Device Compliance"}],
        "difficulty": 2,
    },
    {
        "module": "Manage Apps and Data",
        "topic": "App Protection Policies",
        "questionText": "A user has both corporate and personal apps on their personal phone. You want to prevent corporate data from being copied to personal apps. Which Intune feature achieves this?",
        "answers": [
            {"id": "a", "text": "Device Configuration Profiles", "isCorrect": False},
            {"id": "b", "text": "App Protection Policies (APP/MAM)", "isCorrect": True},
            {"id": "c", "text": "Compliance Policies", "isCorrect": False},
            {"id": "d", "text": "Windows Information Protection", "isCorrect": False},
        ],
        "explanation": "App Protection Policies (part of MAM - Mobile Application Management) allow you to protect corporate data within apps without requiring full device enrollment, enforcing restrictions like blocking copy/paste between managed and unmanaged apps.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/intune/apps/app-protection-policy", "title": "Intune App Protection Policies"}],
        "difficulty": 2,
    },
    {
        "module": "Manage, Maintain, and Protect Devices",
        "topic": "BitLocker",
        "questionText": "Which Intune policy type is used to configure and enforce BitLocker drive encryption on Windows devices?",
        "answers": [
            {"id": "a", "text": "Compliance policy", "isCorrect": False},
            {"id": "b", "text": "Endpoint security - Disk encryption policy", "isCorrect": True},
            {"id": "c", "text": "App configuration policy", "isCorrect": False},
            {"id": "d", "text": "Device enrollment restriction", "isCorrect": False},
        ],
        "explanation": "BitLocker encryption is configured through Intune's Endpoint Security > Disk Encryption policies. This allows you to enforce encryption settings and store BitLocker recovery keys in Entra ID.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/intune/protect/encrypt-devices", "title": "Encrypt devices with Intune"}],
        "difficulty": 2,
    },
]


# ─── MS-102: Microsoft 365 Administrator (sample subset) ─────────────────────

MS102_QUESTIONS = [
    {
        "module": "Manage Your Microsoft 365 Tenant",
        "topic": "Tenant Configuration",
        "questionText": "Which Microsoft 365 admin center allows you to view a unified view of service health, message center, and reports across all Microsoft 365 services?",
        "answers": [
            {"id": "a", "text": "SharePoint admin center", "isCorrect": False},
            {"id": "b", "text": "Microsoft 365 admin center", "isCorrect": True},
            {"id": "c", "text": "Exchange admin center", "isCorrect": False},
            {"id": "d", "text": "Teams admin center", "isCorrect": False},
        ],
        "explanation": "The Microsoft 365 admin center (admin.microsoft.com) is the central hub for managing your tenant, including service health, message center updates, and reports across all Microsoft 365 services.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/microsoft-365/admin/admin-overview/admin-center-overview", "title": "Microsoft 365 Admin Center"}],
        "difficulty": 1,
    },
    {
        "module": "Implement and Manage Identity and Access",
        "topic": "Conditional Access",
        "questionText": "What is the purpose of Conditional Access in Microsoft Entra ID?",
        "answers": [
            {"id": "a", "text": "To automatically assign licenses to new users", "isCorrect": False},
            {"id": "b", "text": "To enforce access controls based on signals like user location, device compliance, and risk level", "isCorrect": True},
            {"id": "c", "text": "To replicate on-premises Active Directory to the cloud", "isCorrect": False},
            {"id": "d", "text": "To manage mobile device enrollment in Intune", "isCorrect": False},
        ],
        "explanation": "Conditional Access is the Zero Trust policy engine that evaluates signals (user identity, location, device state, risk) to grant or block access and potentially require MFA or compliant devices.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/azure/active-directory/conditional-access/overview", "title": "Conditional Access"}],
        "difficulty": 2,
    },
    {
        "module": "Manage Security and Compliance",
        "topic": "Microsoft Purview",
        "questionText": "Which Microsoft Purview feature allows you to classify and protect sensitive information across Microsoft 365 services?",
        "answers": [
            {"id": "a", "text": "Data Loss Prevention (DLP)", "isCorrect": False},
            {"id": "b", "text": "Sensitivity Labels", "isCorrect": True},
            {"id": "c", "text": "eDiscovery", "isCorrect": False},
            {"id": "d", "text": "Compliance Manager", "isCorrect": False},
        ],
        "explanation": "Sensitivity Labels in Microsoft Purview allow you to classify and protect content in Microsoft 365 by applying labels that can encrypt content, add watermarks, and restrict access.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/microsoft-365/compliance/sensitivity-labels", "title": "Sensitivity Labels"}],
        "difficulty": 2,
    },
    {
        "module": "Manage Security and Compliance",
        "topic": "Data Loss Prevention",
        "questionText": "You need to prevent users from accidentally sharing documents containing credit card numbers via email. Which Microsoft 365 feature should you configure?",
        "answers": [
            {"id": "a", "text": "Sensitivity Labels", "isCorrect": False},
            {"id": "b", "text": "Data Loss Prevention (DLP) policies", "isCorrect": True},
            {"id": "c", "text": "Retention policies", "isCorrect": False},
            {"id": "d", "text": "Communication compliance", "isCorrect": False},
        ],
        "explanation": "DLP policies detect sensitive information types (like credit card numbers) in content and can automatically block sharing, send alerts, or require user justification when policy violations occur.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/microsoft-365/compliance/dlp-learn-about-dlp", "title": "Data Loss Prevention"}],
        "difficulty": 1,
    },
    {
        "module": "Manage Microsoft Teams and SharePoint",
        "topic": "Teams Administration",
        "questionText": "In Microsoft Teams, which policy type controls which features individual users can access, such as private channel creation and third-party app usage?",
        "answers": [
            {"id": "a", "text": "Meeting policies", "isCorrect": False},
            {"id": "b", "text": "Teams policies", "isCorrect": False},
            {"id": "c", "text": "App permission policies", "isCorrect": False},
            {"id": "d", "text": "Messaging policies", "isCorrect": True},
        ],
        "explanation": "Actually, Teams admin policies are split into several types. Meeting policies control meeting features, messaging policies control chat features, Teams policies control team creation, and app policies control app access. This question focuses on messaging features.",
        "documentationLinks": [{"url": "https://learn.microsoft.com/en-us/microsoftteams/teams-policies", "title": "Teams Policies"}],
        "difficulty": 3,
    },
]


CERT_DATA = {
    "AZ-900": {
        "name": "Azure Fundamentals",
        "description": "Master the foundational cloud concepts and Azure services needed to pass the AZ-900 exam.",
        "questions": AZ900_QUESTIONS,
    },
    "AZ-104": {
        "name": "Azure Administrator",
        "description": "Learn to implement, manage, and monitor Azure environments for the AZ-104 exam.",
        "questions": AZ104_QUESTIONS,
    },
    "MD-102": {
        "name": "Endpoint Administrator",
        "description": "Deploy, manage, and secure endpoints using Intune and Windows Autopilot for the MD-102 exam.",
        "questions": MD102_QUESTIONS,
    },
    "MS-102": {
        "name": "Microsoft 365 Administrator",
        "description": "Manage Microsoft 365 tenants, identity, security, and compliance for the MS-102 exam.",
        "questions": MS102_QUESTIONS,
    },
}


def seed_cert(cert_code: str, data: dict, conn):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print(f"\n{'='*50}")
    print(f"Seeding {cert_code} ({len(data['questions'])} questions)...")

    # Upsert certification
    cursor.execute("""
        INSERT INTO "Certification" (id, code, name, description, "totalModules", "createdAt", "updatedAt")
        VALUES (gen_random_uuid()::text, %s, %s, %s, 0, NOW(), NOW())
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name, description = EXCLUDED.description, "updatedAt" = NOW()
        RETURNING id
    """, (cert_code, data["name"], data["description"]))
    cert_id = cursor.fetchone()["id"]

    modules_map = {}
    topics_map = {}

    for q in data["questions"]:
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
                cursor.execute('SELECT id FROM "Module" WHERE "certificationId" = %s AND title = %s', (cert_id, module_title))
                row = cursor.fetchone()
            if row:
                modules_map[module_title] = row["id"]

        module_id = modules_map.get(module_title)
        if not module_id:
            continue

        # Upsert topic
        topic_key = (module_title, topic_title)
        if topic_key not in topics_map:
            ms_url = q.get("documentationLinks", [{}])[0].get("url", "https://learn.microsoft.com")
            cursor.execute("""
                INSERT INTO "Topic" (id, "moduleId", title, "msLearnUrl", "orderIndex", "createdAt")
                VALUES (gen_random_uuid()::text, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING RETURNING id
            """, (module_id, topic_title, ms_url, len(topics_map)))
            row = cursor.fetchone()
            if not row:
                cursor.execute('SELECT id FROM "Topic" WHERE "moduleId" = %s AND title = %s', (module_id, topic_title))
                row = cursor.fetchone()
            if row:
                topics_map[topic_key] = row["id"]

        topic_id = topics_map.get(topic_key)

        # Insert question (skip if duplicate text)
        cursor.execute("""
            INSERT INTO "Question" (
                id, "certificationId", "moduleId", "topicId",
                "questionText", "questionType", answers, explanation,
                source, "sourceIcon", "documentationLinks",
                difficulty, "isActive", "createdAt", "updatedAt"
            )
            VALUES (gen_random_uuid()::text, %s, %s, %s, %s, 'SINGLE_CHOICE', %s, %s, 'MICROSOFT', 'microsoft', %s, %s, true, NOW(), NOW())
            ON CONFLICT DO NOTHING
        """, (
            cert_id, module_id, topic_id,
            q["questionText"],
            json.dumps(q["answers"]),
            q.get("explanation", ""),
            json.dumps(q.get("documentationLinks", [])),
            q.get("difficulty", 2),
        ))

    # Update module count
    cursor.execute("""
        UPDATE "Certification" SET "totalModules" = (
            SELECT COUNT(*) FROM "Module" WHERE "certificationId" = %s
        ) WHERE id = %s
    """, (cert_id, cert_id))

    conn.commit()
    cursor.close()

    print(f"  ✓ {cert_code}: {len(data['questions'])} questions, {len(modules_map)} modules, {len(topics_map)} topics")


def main():
    parser = argparse.ArgumentParser(description="Seed sample questions into CertDuo database")
    parser.add_argument("--cert", help="Only seed one cert (e.g., AZ-900)")
    args = parser.parse_args()

    conn = psycopg2.connect(DATABASE_URL)
    try:
        certs = {args.cert.upper(): CERT_DATA[args.cert.upper()]} if args.cert else CERT_DATA
        for code, data in certs.items():
            if code not in CERT_DATA:
                print(f"Unknown cert: {code}")
                continue
            seed_cert(code, data, conn)
    finally:
        conn.close()

    print("\n✓ Done! Run the app with: npm run dev")


if __name__ == "__main__":
    main()
