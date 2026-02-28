#!/usr/bin/env python3
"""
Seeds learning content (markdown body + reading time) into the Topic table.
Run after seed_sample.py has populated the certifications/modules/topics.

Usage:
    python3 seed_content.py
    python3 seed_content.py --cert AZ-900
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv(Path(__file__).parent.parent / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT LIBRARY  (exact topic_title from DB → {body, readingTime, msLearnUrl})
# ─────────────────────────────────────────────────────────────────────────────

CONTENT = {

    # ══════════════════════════════════════════════════════════════════════════
    # AZ-900 — Cloud Concepts
    # ══════════════════════════════════════════════════════════════════════════

    "Cloud Service Types": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-cloud-service-types/",
        "body": """## Cloud Service Types: IaaS, PaaS, and SaaS

Azure services fall into three main categories that describe how much management responsibility you retain versus what the cloud provider handles.

## Infrastructure as a Service (IaaS)

IaaS is the most flexible category. The cloud provider manages the physical infrastructure (servers, storage, networking), but **you manage everything above that** — operating system, middleware, runtime, and applications.

**You manage:** OS, middleware, runtime, data, applications
**Provider manages:** Virtualization, servers, storage, networking

### Common IaaS Use Cases
- Lift-and-shift migrations of existing on-premises applications
- Test and development environments
- Storage, backup, and disaster recovery
- High-performance computing workloads

### IaaS Examples in Azure
- Azure Virtual Machines
- Azure Virtual Network
- Azure Disk Storage

### When to Choose IaaS
Choose IaaS when you need maximum control, are migrating legacy applications, or have specific OS-level requirements you cannot change.

---

## Platform as a Service (PaaS)

PaaS sits in the middle. The cloud provider manages the infrastructure **plus** the operating system, middleware, and runtime. You focus on your application and data only.

**You manage:** Applications, data
**Provider manages:** OS, middleware, runtime, virtualization, servers, storage, networking

### Common PaaS Use Cases
- Web application development and hosting
- Database management without OS-level access
- Machine learning and analytics platforms
- API development and management

### PaaS Examples in Azure
- Azure App Service (web apps)
- Azure SQL Database
- Azure Functions
- Azure Kubernetes Service (managed control plane)

### When to Choose PaaS
Choose PaaS when you want to focus on application development without managing underlying infrastructure. Ideal for development teams.

---

## Software as a Service (SaaS)

SaaS is the most complete cloud service model. You use a fully managed application over the internet. The provider manages everything — you only manage your data and user access configuration.

**You manage:** Data, user accounts, access configuration
**Provider manages:** Everything else

### Common SaaS Examples
- Microsoft 365 (Word, Excel, Teams, Outlook)
- Dynamics 365
- Salesforce, Dropbox, Gmail

### When to Choose SaaS
Choose SaaS for productivity tools, collaboration software, and situations where you need software quickly without any infrastructure customization.

---

## Comparison Summary

| Feature | IaaS | PaaS | SaaS |
|---------|------|------|------|
| Control | Highest | Medium | Lowest |
| Flexibility | Highest | Medium | Lowest |
| Management burden | Highest | Medium | Lowest |
| Time to deploy | Slow | Fast | Instant |
| Best for | Lift-and-shift | App development | End users |

## Key Takeaways

- **IaaS** = rent the infrastructure, manage everything else yourself
- **PaaS** = rent the platform, focus only on your code and data
- **SaaS** = use ready-made software, manage only data and users
- Moving from IaaS → PaaS → SaaS reduces management burden but also reduces control
- Most real-world Azure deployments use a mix of all three models""",
    },

    "Benefits of Cloud": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-benefits-use-cloud-services/",
        "body": """## Benefits of Using Cloud Services

Microsoft Azure and other cloud platforms offer a core set of benefits that apply across virtually every workload.

## High Availability

High availability means your application remains accessible even when components fail. Azure offers **Service Level Agreements (SLAs)** that guarantee uptime percentages:

- Most Azure services offer 99.9% or higher uptime
- Critical services like Microsoft Entra ID offer 99.99%
- 99.99% uptime = less than ~52 minutes of downtime per year

Azure achieves high availability through redundancy — running workloads across multiple servers, racks, and datacenters.

## Scalability

Scalability is the ability to adjust resources to meet demand.

- **Vertical scaling (scale up):** Add more CPU or RAM to an existing resource
- **Horizontal scaling (scale out):** Add more instances of a resource

Cloud scalability is elastic — scale out during peak demand (e.g., Black Friday) and scale back in afterward, paying only for what you use.

## Reliability

Reliability is the ability of a system to recover from failures and continue functioning:

- Resources can be deployed across multiple **regions**
- **Availability Zones** protect from datacenter-level failures
- **Geo-redundant storage** automatically replicates data to a secondary region

## Predictability

- **Performance predictability:** Autoscaling, load balancing, and high availability ensure consistent user experience
- **Cost predictability:** Track and forecast spending using Azure Cost Management and the Azure Pricing Calculator

## Security

Azure provides tools and features at every layer:

- Built-in DDoS protection, firewalls, and network security groups
- Microsoft Defender for Cloud monitors your security posture
- Compliance certifications (ISO, SOC, HIPAA, GDPR) maintained by Microsoft
- You retain control over your data's location and access

## Governance and Manageability

- **Azure Policy** enforces rules across your environment
- **Azure Blueprints** deploy compliant environments automatically
- **Azure portal, CLI, PowerShell, REST APIs** all provide management flexibility

## Key Takeaways

- High availability, scalability, reliability, predictability, security, governance, and manageability are the core cloud benefits
- SLAs formalize the availability guarantees providers make to customers
- The shift from CapEx to OpEx is a fundamental financial benefit of cloud computing""",
    },

    "Cloud Deployment Models": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/",
        "body": """## Cloud Deployment Models

A cloud deployment model defines where your data lives and how your infrastructure is managed. There are three main models.

## Public Cloud

A public cloud is built, controlled, and maintained by a third-party provider (like Microsoft Azure). Resources are owned by the provider and shared across multiple organizations (with data isolation).

**Characteristics:**
- No capital expenditure to scale up
- Applications can be quickly provisioned and deprovisioned
- Customers pay only for what they use

**Best for:** Organizations that want to minimize IT management overhead, have variable workloads, or need rapid global scaling.

## Private Cloud

A private cloud is a computing environment dedicated exclusively to one organization. It can be hosted on-premises or by a third party, but infrastructure is not shared.

**Characteristics:**
- Organization purchases and maintains hardware
- Greater control over data, security, and compliance
- Must purchase hardware for any anticipated growth (even if unused)

**Best for:** Organizations with strict regulatory requirements (government, healthcare, finance) or those needing complete control.

## Hybrid Cloud

A hybrid cloud combines public and private clouds, allowing data and applications to move between them.

**Characteristics:**
- Most flexibility of the three models
- Can use public cloud to handle demand spikes ("cloud bursting")
- Requires more complex management and governance

**Best for:** Organizations that must keep some data on-premises (compliance) but want cloud agility for other workloads.

## Comparing Deployment Models

| | Public | Private | Hybrid |
|--|--------|---------|--------|
| Capital cost | None | High | Medium |
| Control | Low | High | Medium |
| Scalability | Unlimited | Limited | Flexible |
| Compliance | Varies | Highest | Flexible |

## Key Takeaways

- **Public cloud:** Third-party owned, shared infrastructure, pay-as-you-go
- **Private cloud:** Dedicated infrastructure, maximum control, higher cost
- **Hybrid cloud:** Mix of both, maximum flexibility, more complex to manage
- Most enterprises use hybrid or multi-cloud approaches""",
    },

    "Cloud Expenditure Models": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/",
        "body": """## Cloud Expenditure Models: CapEx vs. OpEx

One of the most important financial concepts in cloud computing is the shift from **Capital Expenditure (CapEx)** to **Operational Expenditure (OpEx)**.

## Capital Expenditure (CapEx)

CapEx refers to spending money on physical infrastructure **upfront** — before you use it.

**On-premises CapEx examples:**
- Purchasing servers, storage arrays, and networking equipment
- Building or renting datacenter space
- Installing cooling, power, and cabling infrastructure

**Characteristics:**
- High upfront investment
- Costs are deducted over time through depreciation
- You own the assets
- Hard to predict exact needs (over-provisioning or under-provisioning)

## Operational Expenditure (OpEx)

OpEx refers to spending money on services **as you use them** — pay-as-you-go.

**Cloud OpEx examples:**
- Paying monthly for Azure virtual machines
- Paying per GB for Azure Blob Storage
- Paying per query for Azure SQL Database

**Characteristics:**
- No large upfront cost
- Predictable monthly billing
- Scale up or down based on actual usage
- Deducted in the same year the expense occurs

## Why Cloud Shifts Costs to OpEx

When you use Azure, you're essentially renting computing resources from Microsoft. This means:

1. You stop buying hardware (no CapEx)
2. You pay monthly for what you consume (OpEx)
3. Microsoft handles depreciation, maintenance, and replacement

## Consumption-Based Model

Azure uses a **consumption-based model**, meaning you only pay for what you use. Benefits:

- **No upfront costs:** Start using resources immediately
- **No wasted resources:** Stop paying when you stop using
- **Elastic costs:** Costs scale naturally with your business
- **Better cost prediction:** Use Azure Cost Management to forecast and budget

## Key Takeaways

- **CapEx:** Upfront investment in owned hardware (on-premises model)
- **OpEx:** Pay-as-you-go for consumed services (cloud model)
- Cloud computing primarily uses OpEx — no large upfront hardware purchases
- The consumption-based model means you pay only for what you use
- This model enables better cost control, forecasting, and elimination of wasted capacity""",
    },

    # ── AZ-900 — Azure Architecture ──────────────────────────────────────────

    "Regions and Availability Zones": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/",
        "body": """## Azure Regions and Availability Zones

Understanding Azure's physical infrastructure is foundational for any Azure professional.

## Azure Regions

A **region** is a geographic area containing at least one (usually multiple) datacenters that are networked together. Examples: East US, West Europe, Southeast Asia.

**Key facts:**
- Azure has 60+ regions across the globe
- Most services require you to select a region when creating a resource
- Regions have different service availability and pricing
- Choose a region close to your users to reduce latency

## Region Pairs

Every Azure region is **paired** with another region in the same geography, at least 300 miles apart.

Benefits of region pairs:
- In a large-scale Azure outage, at least one region in every pair is prioritized for recovery
- Planned Azure updates are rolled to one paired region at a time (minimizing downtime)
- Data stays within the same geography for tax and compliance purposes

*Example pairs: East US ↔ West US, North Europe ↔ West Europe*

## Availability Zones

**Availability Zones** are physically separate datacenters **within a single Azure region**. Each zone has independent power, cooling, and networking.

- A region with Availability Zones has at least **3 separate zones**
- Deploying across zones protects you from a single datacenter failure
- **Zone-redundant services:** Automatically replicate across zones (e.g., Azure SQL, Storage with ZRS)
- **Zonal services:** You pin a resource to a specific zone (e.g., a VM)

## Azure Geographies

A **geography** is a market containing two or more regions that preserve data residency and compliance boundaries. Examples: United States, Europe, Asia Pacific.

Geographies ensure data sovereignty — your data stays within the geographic boundary you select.

## Management Hierarchy

```
Azure Account
  └── Management Group (optional governance layer)
        └── Subscriptions (billing + access control)
              └── Resource Groups (lifecycle containers)
                    └── Resources (VMs, databases, etc.)
```

### Resource Groups

- Every resource must belong to exactly **one** resource group
- Resources in a group share a lifecycle — deploy together, delete together
- Apply tags, access control, and policies at the resource group level

### Subscriptions

- A **subscription** is a billing and access control boundary
- A single account can have multiple subscriptions (Dev/Test/Production pattern)
- Each subscription receives its own invoice

### Management Groups

- Containers for managing policies and access **across multiple subscriptions**
- Up to 6 levels of nesting
- Policies applied at a management group cascade down to all subscriptions

## Key Takeaways

- Regions are geographic areas; choose based on user proximity, compliance, and service availability
- Availability Zones protect from datacenter failures within a region (at least 3 per region)
- Region Pairs protect from region-wide failures and are used for disaster recovery
- All resources must belong to a resource group, inside a subscription
- Management groups govern multiple subscriptions with inherited policies and RBAC""",
    },

    "Resource Organization": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/",
        "body": """## Azure Resource Organization

Azure provides a hierarchical structure to organize, manage, and govern your cloud resources effectively.

## The Four-Level Hierarchy

**Management Groups → Subscriptions → Resource Groups → Resources**

Each level provides management scope for the levels below it.

## Resources

A **resource** is any manageable item in Azure:
- Virtual machines, storage accounts, databases
- Virtual networks, App Service plans, key vaults
- Every resource has a resource type, name, region, and subscription

## Resource Groups

A **resource group** is a logical container for related Azure resources.

**Rules:**
- Every resource must belong to exactly **one** resource group
- Resource groups cannot be nested
- Resources in different regions can be in the same resource group

**Best practices:**
- Group resources that share the same lifecycle (deploy and delete together)
- Group resources for the same project or environment
- Apply RBAC permissions at the resource group level for access control

## Subscriptions

A **subscription** provides authenticated, authorized access to Azure services and is the primary billing boundary.

**Common subscription patterns:**
- **By environment:** Separate subscriptions for Dev, Test, and Production
- **By department:** Each business unit has its own subscription and invoice
- **By compliance:** Isolate workloads with different regulatory requirements

## Management Groups

**Management Groups** allow you to manage governance at scale across multiple subscriptions:

- Apply policies and RBAC at the management group level — they cascade down
- Up to **6 levels** of nested management groups
- A **Root Management Group** is automatically created for your tenant

**Example hierarchy:**
```
Root Management Group
  ├─ Corp IT Management Group
  │    ├─ Production Subscription
  │    └─ Dev/Test Subscription
  └─ Business Units Management Group
       └─ Marketing Subscription
```

## Azure Resource Tags

**Tags** are name-value pairs attached to resources for organization:
- `Environment: Production`
- `Department: Finance`
- `Project: Phoenix`
- `CostCenter: CC-1234`

Tags enable:
- Filter and search resources across subscriptions
- Cost allocation reports by project/department
- Automation triggers based on tag values
- Policy enforcement (e.g., "require CostCenter tag on all VMs")

## Key Takeaways

- **Resources** are the actual Azure services you deploy
- **Resource Groups** group resources that share a lifecycle
- **Subscriptions** are billing and access control boundaries
- **Management Groups** govern policies across multiple subscriptions
- Tags provide metadata for cost tracking, filtering, and automation""",
    },

    "Compute Services": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/",
        "body": """## Azure Compute Services

Azure compute provides on-demand resources — CPU, memory, and storage — for running applications. The main options are Virtual Machines, Containers, App Service, and Functions.

## Azure Virtual Machines (VMs)

Azure VMs are IaaS — you get virtualized hardware and manage everything from the OS up.

**Key facts:**
- Supports Windows and Linux
- Priced by the second — stop and deallocate the VM to stop paying for compute
- Choose the VM size based on your workload (CPU, RAM, storage IOPS)

### VM Availability Options

| Option | Protection | SLA |
|--------|-----------|-----|
| No redundancy | None | No SLA |
| Availability Set | Hardware/rack failure in datacenter | 99.95% |
| Availability Zone | Full datacenter failure | 99.99% |
| VM Scale Sets | Auto-scaling across zones | Up to 99.99% |

### VM States and Billing

- **Running:** VM is active — billed for compute
- **Stopped (OS shutdown):** Resources still reserved — **still billed for compute**
- **Deallocated:** Hardware released — **no compute charge** (storage still billed)

> Always **deallocate** VMs when not in use to stop compute billing!

## Azure App Service

App Service is a **PaaS** platform for hosting web apps, REST APIs, and mobile backends.

- Supports .NET, Python, Node.js, Java, PHP, Ruby
- Built-in CI/CD from GitHub, Azure DevOps
- Auto-scaling and load balancing included
- No server management required

## Azure Container Instances (ACI)

Run Docker containers in Azure **without managing VMs or clusters**.

- Fastest way to run a container in Azure
- Billed by the second
- Good for: isolated tasks, simple workloads, CI/CD pipelines

## Azure Kubernetes Service (AKS)

Managed Kubernetes for orchestrating containerized applications at scale.

- Azure manages the Kubernetes control plane
- You manage worker nodes (or use virtual nodes for serverless)
- Best for complex microservices architectures

## Azure Functions

**Serverless** compute — write code, run in response to events, pay only when code executes.

- Event triggers: HTTP, Timer, Queue message, Blob upload, etc.
- **Consumption plan:** Scales to zero, pay per execution
- **Premium plan:** Pre-warmed instances, no cold starts
- Supports: C#, JavaScript, Python, Java, PowerShell

## Choosing the Right Service

| Scenario | Best Service |
|----------|-------------|
| Full OS control, lift-and-shift | Virtual Machines |
| Host a web app or API | App Service |
| Run containers quickly | Container Instances |
| Production container orchestration | AKS |
| Event-driven short tasks | Azure Functions |

## Key Takeaways

- **VMs:** IaaS, maximum control, most management burden — always deallocate to stop billing
- **App Service:** PaaS, focus on code, managed platform
- **ACI:** Quick container execution without cluster management
- **AKS:** Production-grade container orchestration
- **Functions:** Serverless, event-driven, consumption pricing""",
    },

    "Networking Services": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/",
        "body": """## Azure Networking Services

Azure networking connects your resources to each other, to the internet, and to your on-premises infrastructure.

## Azure Virtual Network (VNet)

A **Virtual Network** is the foundational networking building block. It's a logically isolated network in Azure that you control.

**Key capabilities:**
- Resources within a VNet can communicate with each other by default
- Outbound internet connectivity is enabled by default
- Inbound internet access requires a public IP or load balancer
- Divide VNets into **subnets** for organization and security

### VNet Peering
Connects two VNets so resources in each can communicate as if they were in the same network. Traffic stays on Microsoft's private backbone (not the public internet).

## Azure VPN Gateway

Connects your Azure VNet to your on-premises network over an **encrypted tunnel** via the public internet.

- **Site-to-Site VPN:** Connects your entire on-premises network to Azure (persistent)
- **Point-to-Site VPN:** Connects individual remote devices to Azure
- Maximum bandwidth: typically up to 10 Gbps

## Azure ExpressRoute

Creates **private, dedicated connections** between your on-premises infrastructure and Azure datacenters — completely bypassing the public internet.

**Advantages over VPN:**
- More reliable (dedicated circuit)
- Lower, consistent latency
- Higher bandwidth (up to 100 Gbps)
- Traffic never crosses the public internet

**Use when:** Regulatory requirements mandate private connectivity, or you need consistent performance for mission-critical workloads.

## Network Security Groups (NSGs)

NSGs are virtual firewalls — they contain inbound and outbound traffic rules.

- Each rule specifies: source, destination, protocol, port range, and priority
- Lower priority number = higher precedence (processed first)
- Can be applied to subnets or individual network interfaces (NICs)

## Azure Load Balancer

Distributes incoming network traffic across multiple backend VMs.

- **Layer 4 (TCP/UDP)** load balancing
- Supports public (internet-facing) and internal load balancers
- Required for the 99.99% SLA with Availability Zones

## Azure Application Gateway

Layer 7 (HTTP/HTTPS) load balancer with additional capabilities:

- **URL-based routing:** Send /api traffic to one backend, /images to another
- **SSL termination:** Decrypt HTTPS at the gateway
- **Web Application Firewall (WAF):** Protects against OWASP threats (SQL injection, XSS)

## Key Takeaways

- **VNet:** Isolated private network in Azure — foundation of all Azure networking
- **VPN Gateway:** Encrypted connection to on-premises over the internet
- **ExpressRoute:** Private dedicated connection to on-premises (no public internet)
- **NSG:** Allow/deny rules for network traffic (applied to subnet or NIC)
- **Load Balancer:** Layer 4 traffic distribution across VMs
- **Application Gateway:** Layer 7 with WAF — web application protection and routing""",
    },

    "Storage Services": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/",
        "body": """## Azure Storage Services

Azure Storage is Microsoft's cloud storage solution for modern data storage scenarios — massively scalable, durable, and highly available.

## Azure Storage Account

A **storage account** is the top-level resource. It provides a unique namespace accessible over HTTP/HTTPS. All storage resources (blobs, files, queues, tables) live inside a storage account.

## Azure Blob Storage

Object storage for **unstructured data** — images, videos, backups, log files, static website content.

### Access Tiers

| Tier | Use Case | Storage Cost | Access Cost |
|------|----------|-------------|-------------|
| **Hot** | Frequently accessed | Higher | Lower |
| **Cool** | Infrequently accessed (≥30 days) | Lower | Higher |
| **Archive** | Rarely accessed (≥180 days) | Lowest | Highest (+ hours to rehydrate) |

Move data between tiers manually or via lifecycle management policies.

## Azure Files

Fully managed **file shares** in the cloud accessible via **SMB** and NFS protocols — same as Windows file shares.

**Use cases:**
- Replace on-premises file servers
- Share configuration files across VMs
- Lift-and-shift applications that use file system APIs

Azure Files can be mounted simultaneously from cloud AND on-premises deployments.

## Azure Queue Storage

Stores large numbers of **messages** for asynchronous communication between application components.

- Each message: up to 64 KB
- A single queue: millions of messages
- Classic use: web front-end posts tasks, background workers process them

## Azure Disk Storage

Block-level storage volumes (virtual hard disks) for Azure VMs.

| Type | Use Case |
|------|----------|
| **Ultra Disk** | Sub-millisecond latency, highest IOPS — SAP HANA, top-tier DBs |
| **Premium SSD** | Production workloads, consistent performance |
| **Standard SSD** | Most workloads (recommended default) |
| **Standard HDD** | Lowest cost, backups, dev/test |

## Redundancy Options

| Option | Copies | Protects Against |
|--------|--------|-----------------|
| **LRS** (Locally Redundant) | 3 in same datacenter | Hardware failure |
| **ZRS** (Zone Redundant) | 3 across Availability Zones | Datacenter failure |
| **GRS** (Geo Redundant) | 6 (3 primary + 3 secondary region) | Regional outage |
| **GZRS** (Geo-Zone Redundant) | 6 across zones + paired region | Zone + regional outage |

## Data Migration and Transfer

| Tool | Use Case |
|------|----------|
| **AzCopy** | Command-line bulk copy of blobs and files |
| **Azure Storage Explorer** | GUI for managing storage resources |
| **Azure File Sync** | Sync on-premises Windows Server with Azure Files |
| **Azure Data Box** | Physical offline device for up to 100 TB transfers |

## Key Takeaways

- **Blob Storage:** Unstructured data with Hot/Cool/Archive tiers for cost optimization
- **Azure Files:** Cloud SMB file shares — drop-in replacement for on-premises file servers
- **Queue Storage:** Asynchronous messaging between application components
- **Disk Storage:** Block storage for VMs — choose tier based on performance needs
- Redundancy options range from LRS (local only) to GZRS (zone + geo redundant)""",
    },

    "Database Services": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/",
        "body": """## Azure Database Services

Azure offers a comprehensive portfolio of fully managed database services for both relational and non-relational workloads.

## Azure SQL Database

Azure SQL Database is a fully managed **relational database** based on Microsoft SQL Server.

**Key features:**
- Built-in high availability (99.99% SLA)
- Automatic backups, patching, and updates
- Intelligent performance tuning and threat detection
- Supports T-SQL queries — familiar for SQL Server developers
- **Serverless tier:** Compute scales automatically, pauses when idle

**Use when:** You need a relational database with SQL Server compatibility, want minimal administration, or are building new cloud-native applications.

## Azure SQL Managed Instance

A fully managed SQL Server instance that provides near-100% compatibility with on-premises SQL Server (including SQL Server Agent, cross-database queries, linked servers).

**Use when:** Migrating on-premises SQL Server workloads that use features not supported by Azure SQL Database (like SQL Server Agent jobs).

## Azure Database for PostgreSQL / MySQL / MariaDB

Fully managed community database services:
- **Azure Database for PostgreSQL:** For open-source PostgreSQL workloads
- **Azure Database for MySQL:** Popular for web applications (WordPress, Drupal)
- **Azure Database for MariaDB:** MySQL-compatible fork

All include: automatic backups, patching, high availability, and scaling.

## Azure Cosmos DB

**Cosmos DB** is a globally distributed, multi-model NoSQL database designed for mission-critical applications.

**Key features:**
- **Global distribution:** Replicate data to any Azure region with a click
- **Multi-model:** Supports document (JSON), key-value, column-family, and graph APIs
- **Single-digit millisecond** read and write latency at any scale
- **Multiple consistency levels:** From eventual to strong consistency
- **Serverless and provisioned** throughput options

**Use when:** You need global distribution, extremely low latency, or flexible schema (document/JSON data).

## Azure Cache for Redis

A fully managed in-memory data store based on Redis. Used to:
- Cache frequently accessed database query results
- Store session state in web applications
- Implement pub/sub messaging patterns
- Reduce database load and improve response times

## Choosing the Right Database

| Scenario | Best Service |
|----------|-------------|
| Relational data, SQL queries | Azure SQL Database |
| SQL Server lift-and-shift | Azure SQL Managed Instance |
| Open-source relational | Azure Database for PostgreSQL/MySQL |
| Global, low-latency NoSQL | Azure Cosmos DB |
| Caching and session state | Azure Cache for Redis |

## Key Takeaways

- **Azure SQL Database:** Fully managed SQL Server — great for new apps and SQL Server migrations
- **SQL Managed Instance:** Near-100% SQL Server compatibility for complex migrations
- **Cosmos DB:** Global, multi-model NoSQL — when you need sub-10ms latency anywhere in the world
- **Azure Cache for Redis:** In-memory caching to reduce database load
- All Azure database services include automatic backups, patching, and high availability""",
    },

    # ── AZ-900 — Identity & Security ─────────────────────────────────────────

    "Microsoft Entra ID": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-identity-access-security/",
        "body": """## Microsoft Entra ID (Azure Active Directory)

**Microsoft Entra ID** is Microsoft's cloud-based identity and access management service. It's the backbone of authentication across Microsoft 365, Azure, and thousands of SaaS applications.

## What Entra ID Does

- **Authentication:** Verifies user identity (passwords, MFA, FIDO2 keys)
- **Authorization:** Controls what authenticated users can access (RBAC)
- **Single Sign-On (SSO):** One login grants access to multiple applications
- **Application management:** Register and control access to apps
- **Device management:** Register and manage devices for policy enforcement

## Entra ID vs. On-Premises Active Directory

| Feature | Active Directory (on-prem) | Microsoft Entra ID (cloud) |
|---------|---------------------------|---------------------------|
| Protocol | Kerberos, NTLM, LDAP | OAuth 2.0, OIDC, SAML |
| Auth target | On-premises apps | Internet/cloud apps |
| MFA built-in | Add-on required | Built-in |
| Flat structure | No (uses OUs) | Yes (flat tenant) |
| Internet-accessible | No (by default) | Yes |

## Authentication Methods

**Multi-Factor Authentication (MFA)** requires two or more:
- **Something you know:** Password, PIN
- **Something you have:** Authenticator app, SMS code, hardware token
- **Something you are:** Fingerprint, facial recognition

MFA dramatically reduces account compromise risk — passwords alone are insufficient.

## Passwordless Authentication

Microsoft supports three passwordless options:
1. **Windows Hello for Business** — biometric/PIN tied to a registered device
2. **Microsoft Authenticator app** — approve sign-ins via phone notification
3. **FIDO2 security keys** — hardware keys (YubiKey, etc.)

## Conditional Access

Entra ID Conditional Access applies access policies based on real-time signals:

**Signals:** User/group identity, device compliance state, location (IP), application being accessed, sign-in risk score

**Actions:** Allow, require MFA, block access, require compliant device

*Example: "If a user signs in from outside our network on an unmanaged device → require MFA"*

## Role-Based Access Control (Azure RBAC)

RBAC controls **what users can do** with Azure resources. Roles are assigned at a scope.

**Common built-in roles:**
- **Owner:** Full access + ability to assign permissions
- **Contributor:** Create/manage resources, cannot assign permissions
- **Reader:** View-only, no changes
- **User Access Administrator:** Manage user access only

**Scope hierarchy:** Management Group → Subscription → Resource Group → Resource
(Roles cascade down from parent scope)

## Zero Trust Principles

1. **Verify explicitly:** Authenticate and authorize based on all available data points
2. **Use least privilege:** Grant minimum necessary access, use Just-In-Time access
3. **Assume breach:** Minimize blast radius, segment access, encrypt everything

## Key Takeaways

- Microsoft Entra ID is the cloud identity platform — not the same as on-premises AD
- MFA requires two factors: something you know + something you have/are
- Conditional Access = smart access policies based on signals (user, device, location, risk)
- Azure RBAC = permissions to Azure resources (Owner > Contributor > Reader)
- Zero Trust model: verify everything, trust nothing by default""",
    },

    "Conditional Access": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-identity-access-security/",
        "body": """## Conditional Access in Microsoft Entra ID

**Conditional Access** is Microsoft Entra ID's policy engine for controlling access to cloud applications based on real-time signals.

## How Conditional Access Works

Conditional Access acts as the **gatekeeper** between user identity verification and resource access. It evaluates signals and enforces controls.

**The flow:**
1. User attempts to access an application
2. Entra ID gathers signals (who, what device, from where, what app, what risk)
3. Conditional Access policies are evaluated
4. Access is granted, requires MFA, requires compliant device, or is blocked

## Signals Used in Policies

- **User or group membership:** Apply different policies to executives vs. general staff
- **IP location:** Corporate network vs. unknown country
- **Device:** Is the device Entra-joined? Is it compliant with Intune policies?
- **Application:** Accessing Salesforce vs. Azure Portal may trigger different requirements
- **Real-time risk:** Microsoft evaluates sign-in risk (impossible travel, leaked credentials)

## Policy Controls

**Grant controls (what's required to access):**
- Require MFA
- Require Entra-joined device
- Require Intune-compliant device
- Require approved client application
- Require terms of use acceptance
- **Block access** (most restrictive)

**Session controls (restrict what can be done after access):**
- Sign-in frequency (how often to re-authenticate)
- Persistent browser session settings
- Application restrictions (view-only in SharePoint)

## Common Policy Examples

1. **"Require MFA for all admin roles"** — All Global Admin, Exchange Admin, etc. must use MFA on every sign-in

2. **"Block legacy authentication"** — Block sign-ins using older protocols (IMAP, POP3, Basic Auth) that can't use MFA

3. **"Require compliant device for Office 365"** — Only Intune-managed, policy-compliant devices can access Microsoft 365

4. **"Block access from high-risk countries"** — Block sign-ins from locations your organization never operates in

## Prerequisites

- Requires **Microsoft Entra ID P1** or P2 license (included in Microsoft 365 Business Premium, E3, E5)
- Cannot be used simultaneously with **Security Defaults** (which must be disabled first)

## Key Takeaways

- Conditional Access evaluates signals (identity, device, location, app, risk) to enforce access policies
- It can require MFA, require compliant devices, or block access entirely
- Conditional Access requires Entra ID P1+ licensing
- It replaces Security Defaults for organizations needing granular control
- Always create a **break-glass account** (excluded from Conditional Access) to avoid lockout""",
    },

    "Identity and Access": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-identity-access-security/",
        "body": """## Azure Identity and Access Management

Identity is the primary security perimeter in cloud computing. Verifying who someone is and controlling what they can do is more important than ever.

## The Shared Responsibility of Identity

In cloud environments, **you are always responsible for identity and access management** — regardless of whether you use IaaS, PaaS, or SaaS. The cloud provider secures the infrastructure; you secure who can access your resources.

## Microsoft Entra ID Tenants

A **tenant** is a dedicated Entra ID instance representing your organization. When you sign up for Microsoft 365 or Azure, a tenant is automatically created.

- Unique domain: `yourcompany.onmicrosoft.com` (you can add custom domains)
- All your users, groups, applications, and policies live in the tenant
- Completely isolated from other organizations' tenants

## Users and Groups

- **Users:** Represent individual people or service identities
- **Groups:** Collections of users — assign permissions to groups rather than individuals
- **Service Principals:** Non-human identities for applications, VMs, and automation
- **Managed Identities:** Azure-managed service principals — no credentials to manage

### Managed Identities

Azure resources (VMs, App Service, Functions) can have a **managed identity** — an automatically managed Entra ID identity. The application can authenticate to other Azure services (like Key Vault) without storing credentials anywhere.

- **System-assigned:** Tied to a specific resource, deleted with the resource
- **User-assigned:** Standalone identity that can be shared across multiple resources

## Role-Based Access Control (RBAC)

Azure RBAC controls permissions to Azure resources using three elements:

1. **Security principal:** Who — user, group, service principal, or managed identity
2. **Role definition:** What — set of allowed actions (e.g., "read storage" or "manage VMs")
3. **Scope:** Where — management group, subscription, resource group, or resource

Roles are **inherited** — assigning a role at the subscription scope applies to all resource groups and resources within it.

## Principle of Least Privilege

Always grant the **minimum permissions** necessary:
- Use Reader instead of Contributor where write access isn't needed
- Use built-in roles before creating custom roles
- Assign roles to groups rather than individual users
- Review and remove unused role assignments regularly

## Key Takeaways

- You are always responsible for identity management in cloud environments
- Managed Identities let Azure resources authenticate without stored credentials
- RBAC = security principal + role definition + scope
- Always apply least privilege — grant only the permissions needed
- Entra ID groups simplify permissions management at scale""",
    },

    "Role-Based Access Control": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-identity-access-security/",
        "body": """## Azure Role-Based Access Control (RBAC)

Azure RBAC is the authorization system that controls who can do what with which Azure resources.

## How RBAC Works

RBAC uses three components:

1. **Security principal:** The *who* — a user, group, service principal, or managed identity
2. **Role definition:** The *what* — a collection of permissions (actions and notActions)
3. **Scope:** The *where* — management group, subscription, resource group, or resource

A **role assignment** combines these three: *"This user can do these actions on this resource."*

## Common Built-In Roles

| Role | Description |
|------|-------------|
| **Owner** | Full access to all resources + assign permissions to others |
| **Contributor** | Create/manage all resources; cannot assign permissions |
| **Reader** | View all resources; cannot make changes |
| **User Access Administrator** | Manage user access to Azure resources |

Azure has 100+ additional built-in roles for specific services (e.g., Virtual Machine Contributor, Storage Blob Data Reader).

## Scope Hierarchy and Inheritance

Roles assigned at a **higher scope are inherited** by all lower scopes:

```
Management Group  ← assign here, inherits to everything below
  └── Subscription
        └── Resource Group
              └── Resource
```

If you assign the Reader role at the subscription level, the user can read everything in every resource group and resource within that subscription.

## Allow Model

Azure RBAC uses an **allow model** — permissions are additive. You start with no permissions and add them via role assignments. Multiple roles can be assigned to the same user; effective permissions = union of all role assignments.

**Exception:** Deny assignments (from Azure Blueprints or custom deny policies) can override allows.

## Custom Roles

If built-in roles don't fit your needs, create **custom roles** with exactly the permissions required:
- Define `Actions` (allowed operations) and `NotActions` (excluded operations)
- Assign to any scope
- Custom roles require Entra ID P1 or higher

## RBAC vs. Entra ID Roles

| | Azure RBAC | Entra ID Roles |
|--|-----------|----------------|
| Controls | Azure resources (VMs, storage, etc.) | Entra ID objects (users, groups, apps) |
| Examples | Owner, Contributor, Reader | Global Admin, User Admin, Exchange Admin |
| Scope | Resource-level | Tenant-level |

These are separate systems — an Entra ID Global Admin does NOT automatically have Azure resource permissions.

## Key Takeaways

- RBAC = security principal + role definition + scope
- Roles are inherited from parent scopes (subscription → resource groups → resources)
- **Owner** = full access; **Contributor** = manage resources; **Reader** = view only
- Azure RBAC controls Azure resources; Entra ID roles control directory objects
- Always use least privilege — assign only the role needed, at the narrowest scope""",
    },

    "Security Tools": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-azure-identity-access-security/",
        "body": """## Azure Security Tools

Azure provides a comprehensive, layered security toolset to protect your cloud environment.

## Defense in Depth

**Defense in Depth** uses multiple security layers so that if one is breached, the next stops the attack.

**Layers (outside → inside):**
1. Physical security (Microsoft's responsibility)
2. Identity and access (MFA, RBAC, Conditional Access)
3. Perimeter (DDoS protection, firewalls)
4. Network (NSGs, VNet isolation)
5. Compute (OS hardening, endpoint protection)
6. Application (secure code, no hardcoded credentials)
7. Data (encryption at rest and in transit)

## Microsoft Defender for Cloud

A **cloud security posture management (CSPM)** and **cloud workload protection** platform.

**Key capabilities:**
- **Secure Score:** Percentage score tracking your overall security posture
- **Security recommendations:** Identifies misconfigurations with remediation steps
- **Threat alerts:** Detects active threats (brute force attacks, crypto mining, lateral movement)
- **Regulatory compliance:** Maps resources to compliance frameworks (PCI DSS, ISO 27001, NIST)
- **Multicloud:** Protects Azure, AWS, and Google Cloud resources

## Microsoft Sentinel

A cloud-native **SIEM** (Security Information and Event Management) + **SOAR** (Security Orchestration, Automation and Response) platform.

- Collects security data at cloud scale from all your sources
- Detects threats using built-in analytics and machine learning
- Investigates incidents with AI-assisted tools
- Automates responses (block user, isolate VM, send alert)

*Defender for Cloud = secure your posture and protect workloads*
*Microsoft Sentinel = detect, investigate, and respond to incidents organization-wide*

## Azure DDoS Protection

Protects Azure resources from Distributed Denial of Service attacks:

- **Basic (free):** Always-on monitoring, automatic mitigation for Azure infrastructure
- **Standard (paid):** Per-resource tuning, attack analytics, cost protection guarantee, 24/7 DDoS rapid response team

## Azure Key Vault

Centralized secrets management:
- **Secrets:** API keys, passwords, connection strings
- **Encryption keys:** Customer-managed keys for Azure services
- **Certificates:** SSL/TLS certificate lifecycle management

Never hardcode credentials — store them in Key Vault and access via managed identities.

## Azure Firewall

Fully managed, stateful **network firewall as a service**:
- Centrally create and enforce network policies across VNets
- Built-in high availability and cloud scalability
- Threat intelligence-based filtering (block known malicious IPs)

## Azure Bastion

Browser-based **RDP/SSH access** to VMs without public IP addresses:
- Connect via Azure portal over TLS — no VPN required
- VMs have no public IP exposure — reduced attack surface
- Available from any browser, any device

## Key Takeaways

- **Defense in Depth:** Layered security (physical → identity → perimeter → network → compute → app → data)
- **Defender for Cloud:** Posture + workload protection, Secure Score, multicloud
- **Microsoft Sentinel:** SIEM + SOAR — collect, detect, investigate, respond
- **DDoS Protection:** Basic (free) vs Standard (advanced per-resource protection)
- **Key Vault:** Centralize secrets, keys, certificates — never hardcode credentials
- **Azure Bastion:** Secure VM access without public IPs""",
    },

    # ── AZ-900 — Governance & Management ────────────────────────────────────

    "Cost Management": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-cost-management-azure/",
        "body": """## Azure Cost Management and Billing

Understanding and controlling cloud costs is a critical skill. Azure provides powerful tools for planning, monitoring, and optimizing spending.

## Factors That Affect Azure Costs

1. **Resource type:** Different resources have different pricing models (per second, per GB, per operation)
2. **Region:** Prices vary by region due to local infrastructure and energy costs
3. **Consumption model:** Pay-as-you-go vs. Reserved Instances (1-3 year commitment, up to 72% savings) vs. Spot VMs (up to 90% off, interruptible)
4. **Network traffic:** Inbound data is usually free; outbound (egress) is charged
5. **Subscription type:** Enterprise Agreement customers receive volume discounts

## Azure Pricing Calculator

Estimate costs **before** deploying:
- Available at: azure.microsoft.com/en-us/pricing/calculator/
- Configure services, choose regions and tiers, see monthly cost estimates
- Export estimates to share with stakeholders

## Azure TCO Calculator

Compare **on-premises vs. Azure** costs:
- Input current infrastructure (servers, storage, networking, labor)
- Get 5-year projected savings from migrating to Azure
- Accounts for hardware, software licenses, datacenter space, power, and IT labor costs

## Azure Cost Management Tool

Built-in service for monitoring and optimizing spending:

- **Cost analysis:** Visualize spending by subscription, resource group, service, or tag
- **Budgets:** Set thresholds and receive alerts (or trigger automation) when approaching limits
- **Advisor recommendations:** Identifies underutilized resources (e.g., VMs at <5% CPU average)
- **Cost exports:** Send data to storage for custom reporting and BI tools

## Cost Optimization Strategies

| Strategy | Savings |
|----------|---------|
| **Reserved Instances** | Up to 72% vs. pay-as-you-go |
| **Azure Hybrid Benefit** | Up to 40% — use existing Windows/SQL Server licenses |
| **Spot VMs** | Up to 90% — for fault-tolerant, interruptible workloads |
| **Auto-shutdown** | Eliminate overnight compute costs for dev/test VMs |
| **Right-sizing** | Don't over-provision — use the smallest VM that meets needs |
| **Delete unused resources** | Unused VMs, disks, and public IPs still incur charges |

## Resource Tags for Cost Allocation

Tags (name-value pairs) allow cost tracking by:
- Department, team, or cost center
- Project or application
- Environment (Production, Development, Testing)

Use Azure Policy to enforce tagging requirements on all new resources.

## Key Takeaways

- Use the **Pricing Calculator** to estimate costs before deployment
- Use the **TCO Calculator** to build business cases for cloud migration
- **Azure Cost Management** monitors and optimizes ongoing spending
- Reserved Instances + Azure Hybrid Benefit = biggest savings for stable workloads
- Tags are essential for cost allocation across departments and projects""",
    },

    "Service Level Agreements": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-cost-management-azure/",
        "body": """## Azure Service Level Agreements (SLAs)

A **Service Level Agreement (SLA)** is a formal agreement between Microsoft and customers defining the expected level of service — primarily around uptime.

## What Azure SLAs Include

- **Uptime guarantee:** Minimum availability percentage
- **Service credits:** What you receive if Microsoft fails to meet the SLA (bill credits, not cash)
- **Exclusions:** Scheduled maintenance, customer-caused outages, force majeure events

## Reading the Numbers

| SLA % | Max downtime/month | Max downtime/year |
|-------|-------------------|-------------------|
| 99% | ~7.3 hours | ~3.65 days |
| 99.9% | ~43.8 minutes | ~8.76 hours |
| 99.95% | ~21.9 minutes | ~4.38 hours |
| 99.99% | ~4.4 minutes | ~52.6 minutes |

Most Azure services offer **99.9% or higher**. Microsoft Entra ID offers 99.99%.

## Composite SLAs

Your application's overall SLA is the **product** of all dependent services' SLAs.

**Example:**
```
Web App SLA:      99.95%
SQL Database SLA: 99.99%
Composite SLA:    99.95% × 99.99% = 99.94%
```

The composite SLA is always **lower** than any individual component's SLA.

## Improving Your Composite SLA

Use **redundancy** to exceed individual SLAs. Example — two VMs in different Availability Zones, either can serve traffic:
- Combined failure probability = 0.01% × 0.01% = 0.0001%
- Effective availability: 99.9999% (better than either VM alone at 99.9%)

## Free Tier = No SLA

Azure's **Free tier services have NO SLA**. For production workloads, always use paid tiers with SLA guarantees.

## Service Credits

When Microsoft fails to meet an SLA:
- You must file a claim within 2 months of the incident
- Credits range from 10% to 100% of the monthly service fee for the affected period
- Credits cannot exceed 100% — no cash refunds

## Key Takeaways

- SLAs define minimum uptime guarantees with credits as remediation
- 99.9% ≈ 44 minutes/month downtime; 99.99% ≈ 4 minutes/month
- Composite SLA = multiply all individual SLAs (always lower than each component)
- Free tier has **no SLA** — never use for production
- Redundancy (Availability Zones, region pairs) significantly improves your effective SLA""",
    },

    "Monitoring Tools": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-monitoring-tools-azure/",
        "body": """## Azure Monitoring Tools

Operating Azure reliably requires visibility into your environment and tools to act on that information.

## Azure Monitor

The central platform for collecting, analyzing, and acting on telemetry from Azure and on-premises environments.

**Data types collected:**
- **Metrics:** Numerical values at intervals (CPU %, memory, request rate)
- **Logs:** Structured event data (errors, audit trails) — queryable via KQL
- **Traces:** Distributed tracing across microservices

**Key features:**
- **Metrics Explorer:** Real-time charts of resource metrics
- **Log Analytics:** Query logs using Kusto Query Language (KQL)
- **Alerts:** Trigger notifications or automation when conditions are met
- **Dashboards:** Custom views combining multiple data sources
- **Workbooks:** Interactive reports for operations teams

## Azure Alerts

Create alerts for:
- **Metric alerts:** CPU > 80% for 5 minutes → send email
- **Log alerts:** More than 100 errors in 15 minutes → create incident
- **Activity log alerts:** Someone deleted a resource group → notify admins
- **Smart detection:** Application Insights auto-detects anomalies

## Application Insights

Application Performance Management (APM) for live web applications:

- Track: request rate, response time, failure rate, dependency calls
- Detect: performance anomalies, slow pages, exceptions
- Identify: which code path causes slowdowns
- Supports: .NET, Node.js, Python, Java, Go + codeless auto-instrumentation

## Azure Service Health

Personalized alerts about Azure platform issues affecting YOUR resources:

| Component | Scope |
|-----------|-------|
| **Azure Status** | Broad view of all Azure services globally |
| **Service Health** | Issues affecting the services and regions YOU use |
| **Resource Health** | Status of your specific individual resources |

## Azure Advisor

Your free, personalized cloud consultant. Analyzes configuration and usage, recommends improvements in 5 categories:

1. **Reliability:** Improve availability (e.g., "Add a second VM to availability set")
2. **Security:** Fix vulnerabilities (e.g., "Enable MFA for accounts with owner access")
3. **Performance:** Speed up apps (e.g., "Consider Premium SSD instead of Standard HDD")
4. **Cost:** Reduce spending (e.g., "This VM has <5% CPU — consider B-series or downsize")
5. **Operational Excellence:** Improve processes and deployments

## Management Tools Comparison

| Tool | Best For |
|------|---------|
| **Azure Portal** | GUI exploration, one-off tasks, visualization |
| **Azure CLI** | Bash scripts, cross-platform automation |
| **Azure PowerShell** | PowerShell scripts, Windows admin workflows |
| **Azure Cloud Shell** | Browser-based shell — no installation needed |
| **Azure Arc** | Manage on-premises + other cloud resources from Azure |

## Key Takeaways

- **Azure Monitor:** Central hub for metrics, logs, and alerts across your environment
- **Application Insights:** APM for web apps — performance, errors, and usage analytics
- **Service Health:** Personalized alerts about Azure outages affecting YOUR resources
- **Azure Advisor:** Free recommendations across reliability, security, performance, cost, ops
- **Azure Arc:** Extend Azure governance and monitoring to non-Azure resources""",
    },

    "Azure Monitor": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-monitoring-tools-azure/",
        "body": """## Azure Monitor

Azure Monitor is the unified monitoring platform for Azure, on-premises, and multicloud environments.

## What Azure Monitor Collects

Azure Monitor aggregates data from virtually every layer of your Azure environment:

- **Azure resources:** Automatically collects metrics and activity logs from all Azure resources
- **Guest OS:** Collect performance counters, event logs, and custom logs from VMs via the Azure Monitor Agent
- **Applications:** Application Insights collects request, dependency, exception, and performance data
- **Custom sources:** Any REST API endpoint can send data to Azure Monitor Logs

## Metrics vs. Logs

| | Metrics | Logs |
|--|---------|------|
| Data type | Numerical values | Structured/text records |
| Storage | Azure Monitor Metrics | Log Analytics Workspace |
| Retention | 93 days (default) | 30 days–2 years (configurable) |
| Query | Metrics Explorer (charts) | Log Analytics (KQL) |
| Best for | Real-time alerting, dashboards | Root cause analysis, trends |

## Log Analytics and KQL

**Log Analytics** is the query interface for Azure Monitor Logs, using **Kusto Query Language (KQL)**.

Example KQL query — find VMs with high CPU:
```
Perf
| where ObjectName == "Processor" and CounterName == "% Processor Time"
| where CounterValue > 80
| summarize avg(CounterValue) by Computer, bin(TimeGenerated, 1h)
| order by avg_CounterValue desc
```

## Azure Monitor Alerts

Configure alerts that fire when conditions are met:

**Alert components:**
- **Condition:** When CPU > 90% for 5 minutes on VM1
- **Action Group:** What to do — send email, SMS, call webhook, create ITSM ticket, run Logic App
- **Alert rule:** Combines condition + action group

**Alert states:** Fired → Acknowledged → Resolved

## Dashboards and Workbooks

- **Azure Dashboards:** Pin metrics charts, log query results, and resource health to shared dashboards in the Azure portal
- **Azure Monitor Workbooks:** Interactive reports combining text, queries, metrics, and parameters — great for operations runbooks

## Integration with Other Services

Azure Monitor feeds into:
- **Microsoft Sentinel:** Sends security logs for SIEM analysis
- **Defender for Cloud:** Ingests resource telemetry for security recommendations
- **Azure Automation:** Trigger runbooks in response to alerts
- **Power BI:** Export data for business-level reporting

## Key Takeaways

- Azure Monitor = central data platform: metrics + logs + traces
- Metrics are for real-time charts and quick alerting; Logs are for deep analysis
- Log Analytics uses KQL — a powerful, readable query language
- Alert rules = condition + action group (who to notify and how)
- Dashboards and Workbooks visualize monitoring data for teams""",
    },

    "Governance Tools": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-azure/",
        "body": """## Azure Governance Tools

At scale, organizations need automated guardrails to ensure resources are deployed correctly and consistently. Azure provides a comprehensive governance toolkit.

## Azure Policy

**Azure Policy** enforces organizational standards and assesses compliance across your Azure environment.

### How It Works
1. Define a **policy definition** — a JSON rule describing allowed or required configurations
2. **Assign** the policy to a scope (management group, subscription, resource group)
3. Azure evaluates new and existing resources against the policy
4. Non-compliant resources are flagged; enforcement can prevent deployment

### Policy Effects

| Effect | Behavior |
|--------|----------|
| **Deny** | Block creation of non-compliant resources |
| **Audit** | Allow creation but log as non-compliant |
| **Append** | Add required fields to the resource |
| **DeployIfNotExists** | Auto-deploy a related resource if it's missing |
| **Modify** | Add or update properties on existing resources |

### Policy Initiatives (Policy Sets)
Bundle multiple policies into one assignment. Example: "Enable Azure Security Center" initiative includes policies to enable various security features together.

### Built-in Policies
Azure includes hundreds of built-in policies covering security, performance, and compliance. You can also write custom policies in JSON.

## Azure Blueprints

**Azure Blueprints** package together:
- Role assignments
- Policy assignments
- ARM templates
- Resource group definitions

Into a single, versioned, repeatable deployment unit.

Assign one blueprint to deploy a fully compliant environment in minutes. Useful for standing up new subscriptions that must comply with organizational standards.

*Blueprint = Infrastructure + Policy + RBAC in one deployable artifact*

## Resource Locks

**Resource Locks** prevent accidental deletion or modification:

| Lock Type | Effect |
|-----------|--------|
| **CanNotDelete** | Read and modify allowed; deletion blocked |
| **ReadOnly** | Only read allowed — no modifications or deletion |

Locks apply regardless of RBAC permissions. A subscription Owner **cannot** delete a resource with a Delete lock without first removing the lock.

Apply locks to: subscriptions, resource groups, or individual resources. Locks **inherit** downward.

## Microsoft Purview

A unified **data governance** service for managing data across on-premises, multicloud, and SaaS sources.

**Capabilities:**
- **Data Map:** Automated discovery and classification of sensitive data (PII, financial, health)
- **Data Catalog:** Search and browse your entire data estate
- **Data Insights:** Reports on data usage and compliance posture
- **Information Protection:** Apply sensitivity labels from Microsoft Purview to files across Microsoft 365

## Azure Compliance Manager / Trust Center

- **Service Trust Portal:** Access Azure audit reports, compliance guides, and certificates (ISO 27001, SOC 2, PCI DSS)
- **Microsoft Compliance Manager:** Assess and improve your compliance posture against regulatory frameworks

## Key Takeaways

- **Azure Policy:** Enforce rules, prevent non-compliant resources (Deny effect) or audit them
- **Policy Initiatives:** Bundle multiple policies into one assignment
- **Azure Blueprints:** Reproducible, compliant environment templates
- **Resource Locks:** CanNotDelete or ReadOnly — prevent accidental deletion/modification
- **Microsoft Purview:** Data governance and sensitive data discovery across your estate""",
    },

    "Deployment Tools": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-azure/",
        "body": """## Azure Deployment and Management Tools

Azure provides multiple tools for deploying and managing resources — from a graphical portal to code-based automation.

## Azure Portal

Web-based graphical interface at **portal.azure.com**.

- Point-and-click interface for creating and managing resources
- Built-in dashboards and monitoring
- Best for: exploring services, one-off tasks, learning Azure
- Not ideal for: repeatable deployments, automation

## Azure Cloud Shell

Browser-based command-line shell, accessible from the Azure portal or **shell.azure.com**.

- Supports both **Bash** (Azure CLI) and **PowerShell**
- No local installation required
- Persistent file storage in Azure Files (your scripts are saved)
- Always up-to-date with latest Azure CLI and PowerShell modules

## Azure CLI

Cross-platform command-line tool for managing Azure resources.

```bash
# List all VMs in a resource group
az vm list --resource-group MyRG --output table

# Create a storage account
az storage account create --name mystorageacct --resource-group MyRG --sku Standard_LRS
```

- Runs on Windows, macOS, Linux
- Great for shell scripts and automation pipelines
- All commands start with `az`

## Azure PowerShell

PowerShell module for managing Azure resources.

```powershell
# Get all VMs in a resource group
Get-AzVM -ResourceGroupName "MyRG"

# Start a VM
Start-AzVM -Name "MyVM" -ResourceGroupName "MyRG"
```

- Best for Windows administrators familiar with PowerShell
- Integrates with existing PowerShell scripts and automation

## Infrastructure as Code (IaC)

Define and deploy infrastructure using code for repeatability and version control.

### ARM Templates (JSON)
Native Azure IaC format. Declarative JSON that describes the desired state of Azure resources.
- Complete, idempotent deployments
- Supports all Azure resources and features

### Bicep
Microsoft's simplified language for deploying Azure resources — compiles to ARM JSON.
```bicep
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: 'mystorageacct'
  location: 'eastus'
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}
```
- More readable than raw ARM JSON
- Full feature parity with ARM

### Terraform
Third-party, open-source IaC tool that works across Azure, AWS, and Google Cloud.
- Large community and provider ecosystem
- Great for multi-cloud organizations

## Azure Arc

**Azure Arc** extends Azure management capabilities to resources **outside** Azure:
- On-premises servers and VMs
- VMs in other cloud providers (AWS, GCP)
- Kubernetes clusters anywhere

With Arc, you can apply Azure Policy, use Defender for Cloud, and monitor with Azure Monitor — all from a single Azure control plane.

## Key Takeaways

- **Azure Portal:** GUI — best for exploration and one-off tasks
- **Cloud Shell:** Browser-based Bash or PowerShell — no installation needed
- **Azure CLI / PowerShell:** Script-based automation for repeatable tasks
- **ARM / Bicep / Terraform:** IaC — define infrastructure as code for version control and repeatability
- **Azure Arc:** Manage on-premises and multicloud resources from Azure""",
    },

    "Microsoft Purview": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-azure/",
        "body": """## Microsoft Purview

**Microsoft Purview** is a unified data governance, risk, and compliance solution that helps organizations manage and govern their data wherever it lives — on-premises, in Azure, or in other clouds.

## The Two Main Pillars

### 1. Microsoft Purview (Unified Data Governance)
For managing your **data estate** — discovering, classifying, and governing data assets.

### 2. Microsoft Purview Compliance (formerly Microsoft 365 Compliance)
For managing your organization's **compliance posture** — protecting sensitive information and meeting regulatory requirements.

## Data Governance Capabilities

### Data Map
- Automated **scanning and classification** of data sources
- Supports: Azure SQL, Azure Data Lake, on-premises SQL Server, S3, Teradata, SAP, and more
- Detects sensitive data types: PII, financial data, health information, credentials

### Data Catalog
- **Searchable inventory** of all data assets in your organization
- Business users can find and understand data without knowing where it physically lives
- Supports business glossary terms, data steward assignments, and lineage visualization

### Data Insights
- Reports on where sensitive data exists
- Which data assets are most accessed
- Compliance posture across your data estate

### Data Lineage
- Visualize how data flows from source to destination
- Understand which reports use which tables; trace data transformation pipelines

## Compliance Capabilities

### Compliance Manager
- Assess your compliance posture against 300+ regulatory frameworks (GDPR, ISO 27001, HIPAA, NIST)
- Provides an overall **compliance score**
- Suggests improvement actions with step-by-step guidance

### Information Protection
- **Sensitivity labels:** Classify and protect documents and emails (Confidential, Public, etc.)
- **Data Loss Prevention (DLP):** Prevent sensitive data from being shared externally
- **Insider Risk Management:** Detect potentially risky user activity

### eDiscovery and Audit
- Search and hold content across Microsoft 365 for legal investigations
- Audit log provides a record of all user and admin activities

## When to Use Purview

| Scenario | Purview Solution |
|----------|-----------------|
| Find where customer PII is stored | Data Map + Catalog |
| Prove GDPR compliance to auditors | Compliance Manager |
| Prevent employees emailing SSNs externally | DLP policies |
| Investigate a data breach | eDiscovery + Audit |

## Key Takeaways

- Microsoft Purview = data governance + compliance in one platform
- **Data Map:** Automatically discovers and classifies data across your entire estate
- **Compliance Manager:** Score your compliance posture and get remediation guidance
- **DLP policies:** Prevent sensitive data from leaving your organization
- Purview covers both Azure data governance AND Microsoft 365 compliance""",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # AZ-104 — Admin Topics
    # ══════════════════════════════════════════════════════════════════════════

    "Virtual Machines": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/configure-virtual-machines/",
        "body": """## Azure Virtual Machine Administration

Azure VMs are the cornerstone of IaaS workloads. As an Azure Administrator, you need to understand VM configuration, sizing, availability, and management in depth.

## VM Creation Considerations

Key decisions when creating a VM:
- **Region and Availability option:** Availability Set, Availability Zone, or Scale Set
- **Image:** OS + optional pre-installed software (Windows Server, Ubuntu, SQL Server images)
- **Size:** CPU cores + RAM + temp disk capacity + max data disk IOPS
- **Disks:** OS disk (required), data disks (optional), temporary disk (ephemeral — not persisted)
- **Networking:** VNet, subnet, public IP (optional), Network Security Group
- **Management:** Boot diagnostics, auto-shutdown, Azure Monitor Agent

## VM Size Families

| Family | Optimized For |
|--------|--------------|
| **B-series (Burstable)** | Variable, low average CPU — dev/test |
| **D-series (General purpose)** | Balanced CPU/memory — web servers, databases |
| **E-series (Memory optimized)** | High RAM — in-memory databases, analytics |
| **F-series (Compute optimized)** | High CPU cores — batch jobs, gaming servers |
| **N-series (GPU)** | Graphics rendering, ML training |
| **L-series (Storage optimized)** | High disk throughput — NoSQL, Cassandra |

## VM Disk Types

| Disk | Description |
|------|-------------|
| **OS Disk** | Persistent, created from image, required on every VM |
| **Temporary Disk** | Ephemeral SSD — **lost on stop/deallocate** — page file only |
| **Data Disks** | Additional managed disks, persistent, for app data |

> Never store critical application data on the temporary disk — it's wiped on deallocation!

## Availability Options Compared

| Option | SLA | Protection |
|--------|-----|-----------|
| No redundancy | No SLA | None |
| **Availability Set** | 99.95% | Hardware/rack failure in datacenter |
| **Availability Zone** | 99.99% | Full datacenter failure |
| **Scale Sets across zones** | 99.99% | Datacenter failure + auto-scaling |

## VM States and Billing

| State | Billed for Compute? |
|-------|-------------------|
| Running | ✅ Yes |
| Stopped (OS shutdown) | ✅ Yes — hardware still reserved |
| **Deallocated** | ❌ No compute — only storage billed |

**Key insight:** Using the OS `shutdown` command leaves the VM in Stopped (not deallocated) state — you're still billed for compute. Use the Azure portal, CLI, or automation to deallocate properly.

## Extensions and Configuration Management

**VM Extensions** run scripts or install software post-deployment:
- **Custom Script Extension:** Run any shell/PowerShell script on the VM
- **DSC (Desired State Configuration):** Enforce configuration state (e.g., ensure IIS is installed and running)
- **Azure Monitor Agent:** Enable metrics, logs, and health monitoring
- **Azure AD SSH Login:** Use Entra ID credentials to SSH into Linux VMs

## Azure Bastion for Secure Access

Instead of exposing VMs with public IP addresses and open RDP/SSH ports:
- Deploy Azure Bastion in your VNet
- Connect via browser-based RDP/SSH through the Azure portal
- VMs have no public IP — drastically reduced attack surface

## Key Takeaways

- Choose VM size based on workload requirements (compute, memory, storage, GPU)
- Availability Sets protect against rack failures (99.95%); Zones protect against datacenter failure (99.99%)
- Always **deallocate** VMs (not just OS shutdown) to stop compute billing
- Temporary disks are ephemeral — lost on deallocation
- Use Azure Bastion for secure RDP/SSH without public IP addresses
- Extensions automate post-deployment configuration and monitoring setup""",
    },

    "Azure Storage Accounts": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/configure-storage-accounts/",
        "body": """## Azure Storage Account Administration

Storage accounts are foundational Azure resources. As an administrator, you need to know how to create, configure, secure, and manage them effectively.

## Storage Account Types

| Type | Supports | Use Case |
|------|----------|----------|
| **Standard general-purpose v2** | Blobs, Files, Queues, Tables | Recommended for most scenarios |
| **Premium block blobs** | Block blobs only | High-transaction, low-latency blob workloads |
| **Premium file shares** | Azure Files only | High-performance file shares (IOPS intensive) |
| **Premium page blobs** | Page blobs only | VM disks requiring high IOPS |

## Storage Account Configuration

When creating a storage account, configure:

1. **Performance:** Standard (HDD-backed) or Premium (SSD-backed)
2. **Replication:** LRS, ZRS, GRS, or GZRS
3. **Access tier (Blob):** Hot or Cool (Archive set at blob level)
4. **Secure transfer required:** Enforce HTTPS (strongly recommended)
5. **Public access:** Allow or block anonymous access to blob containers
6. **Minimum TLS version:** Set to TLS 1.2 minimum (security best practice)

## Redundancy Options

| Redundancy | Copies | Geo-Redundant? | Zone-Redundant? |
|-----------|--------|---------------|----------------|
| **LRS** | 3 in one datacenter | No | No |
| **ZRS** | 3 across AZs in one region | No | Yes |
| **GRS** | 3+3 (primary + secondary region) | Yes | No |
| **GZRS** | 3 AZs primary + 3 secondary region | Yes | Yes |

**With RA-GRS or RA-GZRS:** Read access to secondary region is available even if primary is down (read-only during failover).

## Blob Storage — Lifecycle Management

Automatically transition blobs between access tiers or delete them:

```json
{
  "rules": [{
    "name": "archive-old-logs",
    "type": "Lifecycle",
    "definition": {
      "filters": { "blobTypes": ["blockBlob"], "prefixMatch": ["logs/"] },
      "actions": {
        "baseBlob": {
          "tierToCool": { "daysAfterModificationGreaterThan": 30 },
          "tierToArchive": { "daysAfterModificationGreaterThan": 90 },
          "delete": { "daysAfterModificationGreaterThan": 365 }
        }
      }
    }
  }]
}
```

## Securing Storage Accounts

### Access Keys
- Every storage account has two 512-bit access keys
- Access keys grant full access to the account — treat like root passwords
- Rotate regularly; store in Azure Key Vault

### Shared Access Signatures (SAS)
A SAS token grants **limited, time-bound access** to specific resources:
- **Service SAS:** Access to a specific blob container, file share, queue, or table
- **Account SAS:** Access to multiple services
- **User delegation SAS:** Uses Entra ID credentials (most secure)

Configure: start time, expiry time, allowed permissions (read/write/delete/list), allowed IP ranges

### Azure AD (Entra ID) Authentication
The **most secure** method — use RBAC roles instead of keys:
- `Storage Blob Data Reader` — read blobs
- `Storage Blob Data Contributor` — read, write, delete blobs
- `Storage File Data SMB Share Contributor` — access Azure Files via SMB

### Firewall and Virtual Network Rules
Restrict storage account access to:
- Specific Azure VNets and subnets (using Service Endpoints or Private Endpoints)
- Specific IP address ranges
- Trusted Azure services (e.g., Azure Backup, Azure Monitor)

## Azure File Sync

**Azure File Sync** transforms on-premises Windows Server file servers into a cache of Azure Files:
- Sync files between on-premises server and Azure file share
- **Cloud tiering:** Frequently accessed files stay local; cold files are tiered to Azure (recalled on access)
- Multi-site sync — multiple servers can sync to the same Azure file share

## Key Takeaways

- Use **Standard GPv2** for most scenarios; Premium options for high-IOPS workloads
- Enable **secure transfer (HTTPS)** and set minimum TLS 1.2 on all accounts
- Use **Entra ID RBAC** over access keys for blob/file access where possible
- **SAS tokens** grant time-limited, scoped access — always set expiry and minimum permissions
- **Lifecycle management** automates cost optimization by tiering/deleting old data
- **Private Endpoints** provide the highest network security for storage access""",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MD-102 — Endpoint Administration
    # ══════════════════════════════════════════════════════════════════════════

    "Intune Enrollment": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/enroll-devices-microsoft-intune/",
        "body": """## Microsoft Intune Device Enrollment

Microsoft Intune is the cloud-based endpoint management service for managing devices and apps. Before Intune can manage a device, it must be **enrolled**.

## Enrollment Prerequisites

1. **Intune license:** Required for each managed user (included in Microsoft 365 Business Premium, EMS E3/E5)
2. **MDM Authority:** Must be set to Intune in the Intune admin center
3. **Automatic enrollment (Windows):** Configure in Entra ID → Mobility → Microsoft Intune
4. **DNS records:** Some enrollment methods require EnterpriseEnrollment CNAME record

## Windows Enrollment Methods

### Windows Autopilot
Zero-touch deployment for corporate Windows devices:
- IT pre-registers device hardware IDs with Autopilot profile
- Device ships directly to user — no IT imaging required
- On first boot, device auto-configures: joins Entra ID, enrolls in Intune, installs required apps
- Supports: User-Driven, Self-Deploying, and Pre-Provisioned modes
- **Enrollment Status Page (ESP):** Prevents access until required apps/policies are applied

### Entra ID Join + Automatic Enrollment
For corporate-owned devices set up fresh:
- User joins the device to Entra ID during Windows Out-of-Box Experience (OOBE)
- Automatic MDM enrollment is triggered by the Entra ID join
- Results in: Entra ID joined + Intune managed

### Entra Hybrid Join + Group Policy Enrollment
For devices already joined to on-premises Active Directory:
- Device is joined to both on-premises AD AND Entra ID (hybrid join)
- Group Policy triggers automatic MDM enrollment

### Manual Enrollment (BYOD)
- Settings → Accounts → Access work or school → Connect
- User signs in with organizational account
- Creates a workplace join (not full Entra ID join)
- Best for personal devices where the user wants access to work resources

## iOS/iPadOS Enrollment

### Apple Business Manager (ABM) + Automated Device Enrollment (ADE)
- For corporate-owned iPhones and iPads
- Device enrolls automatically without user interaction
- **Supervised mode:** Unlocks additional management capabilities (disable App Store, always-on VPN, etc.)
- Assign devices to Intune directly from ABM

### Company Portal App (BYOD)
- User installs Company Portal from App Store
- User signs in with organizational credentials
- Enrolls in Intune with a **user-enrolled** or **device enrollment** profile
- Creates management profile on the device

## Android Enrollment

### Android Enterprise (Fully Managed)
- Corporate-owned device, entirely managed by Intune
- Enrollment: QR code during setup, NFC bump, or token
- All apps controlled by IT; no separation between work and personal

### Android Enterprise (Work Profile) — BYOD
- Creates a separate, encrypted work profile on the personal device
- Work apps and data live in the work profile — IT can only manage the work profile
- Personal data remains completely private from IT

### Android Enterprise (Dedicated Device)
- Kiosk-mode devices (point of sale, digital signage, shared tablets)
- Single or multi-app kiosk mode

## macOS Enrollment

### ABM + ADE (Corporate)
- Automatic enrollment when Mac is first set up
- Intune management profile installed silently

### Company Portal (User-initiated)
- User downloads Company Portal
- Installs management profile manually
- Supports app deployment and compliance policies

## Enrollment Restrictions

Control which devices can enroll:
- **Device type restrictions:** Allow only corporate devices, block personal (iOS/Android)
- **Device limit restrictions:** Maximum devices per user (default: 15)
- **Platform restrictions:** Block specific OS versions or manufacturers

## Key Takeaways

- **Windows Autopilot:** Zero-touch corporate device deployment — the modern standard
- **ADE (iOS/Mac):** Silent, supervised enrollment for corporate Apple devices
- **Work Profile (Android):** BYOD — creates isolated work container, personal data stays private
- Enrollment requires: Intune license + MDM authority set + auto-enrollment configured
- Enrollment restrictions control which device types and how many devices per user can enroll""",
    },

    "Compliance Policies": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/protect-devices-with-microsoft-intune/",
        "body": """## Intune Compliance Policies

Compliance policies define the rules and settings a device must meet to be considered **compliant** by Intune. Non-compliant devices can be blocked from accessing corporate resources via Conditional Access.

## What Compliance Policies Define

A compliance policy specifies requirements such as:

### Device Health
- Device must not be jailbroken or rooted
- Must pass Microsoft Defender for Endpoint threat assessment
- Must have Windows Defender enabled

### Device Properties
- Minimum OS version: e.g., Windows 11 22H2 or later
- Maximum OS version: block devices running future preview builds
- Device type restrictions (personal vs. corporate)

### System Security (Windows)
- Require **BitLocker** disk encryption
- Require **Secure Boot** to be enabled
- Require **Code Integrity** (only signed drivers load)
- Firewall must be enabled
- Antivirus must be enabled and up to date

### Password Requirements
- Require a password to unlock the device
- Minimum password length (e.g., 8 characters)
- Password complexity (upper, lower, numbers, special characters)
- Maximum minutes of inactivity before screen lock
- Password expiry and history

## Compliance Evaluation

When a device checks in with Intune:
1. Compliance policy is evaluated against current device state
2. Device is marked **Compliant**, **Not Compliant**, or **Not Evaluated**
3. Compliance state is reported to Entra ID
4. Conditional Access policies in Entra ID use the compliance state as a signal

## Non-Compliance Actions

You configure what happens when a device becomes non-compliant:

| Action | Timing | Description |
|--------|--------|-------------|
| Mark as non-compliant | Immediately | Device is flagged in Intune |
| Send email to user | After X days | Notify user to remediate |
| Retire device | After X days | Remove corporate data |
| Block access (via CA) | Immediately | Conditional Access blocks access |

## Grace Period

Set a **grace period** (e.g., 3 days) before non-compliance blocks access. This gives users time to remediate issues (install updates, enable BitLocker) before losing access.

## Compliance Policy Scoping

Compliance policies are assigned to:
- **User groups:** Policy applies to devices the user enrolls
- **Device groups:** Policy applies to specific devices

Use **filters** to target specific device platforms (Windows 10, iOS 16+, Android 13+).

## Conditional Access Integration

The power of compliance policies comes from Conditional Access integration:

1. Intune evaluates device compliance and reports to Entra ID
2. Conditional Access policy: **"Require compliant device for access to Exchange Online"**
3. Non-compliant device → user cannot access email until device is remediated

## Key Takeaways

- Compliance policies define the minimum security requirements for managed devices
- Non-compliant devices can be blocked from accessing corporate resources via Conditional Access
- Configure **non-compliance actions** with grace periods to notify users before blocking
- Common requirements: BitLocker, Secure Boot, min OS version, firewall enabled, no jailbreak
- Compliance state flows from Intune to Entra ID and is used by Conditional Access policies""",
    },

    "Autopilot": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/deploy-configure-windows-autopilot/",
        "body": """## Windows Autopilot

Windows Autopilot is a collection of technologies for deploying new Windows devices with a zero-touch, cloud-native experience — no imaging, no IT hands-on-keyboard required.

## Traditional vs. Autopilot Deployment

| Traditional | Autopilot |
|-------------|-----------|
| IT captures and deploys custom OS image | Uses Windows OEM image as-is |
| Physical imaging lab required | No imaging infrastructure |
| Device must pass through IT department | Ships direct from vendor to user |
| Days to weeks per device | 30-60 minutes per device |
| Complex, brittle process | Simple, repeatable |

## How Autopilot Works

1. **Device registration:** OEM or IT registers device hardware hash with Autopilot (via Microsoft Partner Center, Intune, or CSV import)
2. **Profile assignment:** Intune assigns an Autopilot deployment profile to the registered device
3. **First boot:** User powers on device and connects to Wi-Fi/Ethernet
4. **OOBE customization:** Autopilot skips standard Windows setup screens (license, privacy settings, local account creation)
5. **Entra ID join:** Device joins Entra ID using user's organizational credentials
6. **Intune enrollment:** Automatic MDM enrollment occurs
7. **ESP:** Enrollment Status Page tracks app/policy deployment progress
8. **Ready to use:** User gets a configured, managed desktop

## Autopilot Deployment Modes

### User-Driven Mode
Most common. User enters their Entra ID credentials during setup. Device gets joined to Entra ID and enrolled in Intune. User sees their profile and apps after ESP completes.

### Self-Deploying Mode
For shared/kiosk devices with no user affinity. Device enrolls completely without user interaction — ideal for digital signage, shared workstations, conference room devices.

### Pre-Provisioned (White Glove)
IT or the OEM pre-provisions the device before it reaches the user:
- IT runs the device through the "Technician Phase" — installs all device-targeted apps and policies
- Reseals the device and ships to user
- User completes the "User Phase" — much faster since device-targeted apps are already installed

### Autopilot Reset
Resets an existing enrolled Windows device back to a business-ready state:
- Removes all user data, apps, and settings
- Re-enrolls in Intune with existing Autopilot profile
- Useful for device redeployment or remediation

## Enrollment Status Page (ESP)

The ESP tracks and displays deployment progress during Autopilot:

**Three phases:**
1. **Device preparation:** Entra ID join, MDM enrollment
2. **Device setup:** Device-targeted apps and policies
3. **Account setup:** User-targeted apps and policies

Configure: which apps must be installed before user can proceed, timeout settings, error handling behavior.

**Block user access until apps are installed:** Prevents users from accessing desktop before required security tools (antivirus, VPN) are ready.

## Autopilot Requirements

- Windows 10 1809+ or Windows 11
- Device must have internet access on first boot
- Device hardware hash registered in Intune before first boot
- Entra ID P1 license (included in M365 Business Premium and above)
- Automatic MDM enrollment configured in Entra ID

## Key Takeaways

- Autopilot enables zero-touch deployment — ship devices directly to users from the vendor
- OEM or IT registers device hardware hashes before the device reaches the user
- **User-Driven:** Standard mode for user-assigned corporate devices
- **Self-Deploying:** Kiosk/shared devices with no user account
- **Pre-Provisioned:** IT pre-stages device apps before shipping to user (fastest user experience)
- The **Enrollment Status Page** blocks user access until required apps are installed""",
    },

    "App Protection Policies": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/protect-apps-data-with-app-protection-policies/",
        "body": """## Intune App Protection Policies (APP)

**App Protection Policies (APP)** — also called Mobile Application Management (MAM) — protect corporate data within managed apps, even on **unmanaged (personal) devices** where you cannot install a device management profile.

## APP vs. MDM: Key Difference

| | MDM (Device Enrollment) | MAM (App Protection Policies) |
|--|------------------------|-------------------------------|
| Manages | Entire device | Individual apps only |
| Requires enrollment | Yes | No (MAM without enrollment) |
| Ideal for | Corporate-owned devices | BYOD personal devices |
| Can wipe | Entire device | Only corporate data in managed apps |
| Employee privacy | Lower | Higher |

APP is the **BYOD-friendly** approach — IT protects corporate data without touching personal apps, photos, or contacts.

## What App Protection Policies Control

### Data Protection Settings

**Data transfer restrictions:**
- Prevent "Save As" to personal storage (OneDrive Personal, Google Drive, iCloud)
- Prevent cut/copy/paste between managed and unmanaged apps
- Restrict which apps corporate data can be shared TO
- Prevent screenshots in managed apps (Android)

**Access requirements:**
- Require PIN or biometric to open managed app
- Require corporate credentials after inactivity period
- Block app access on jailbroken/rooted devices

**Conditional launch settings:**
- Minimum OS version — block or wipe if device is too old
- Minimum app version — require up-to-date app
- Offline grace period — wipe corporate data after X days offline

### Selective Wipe
When an employee leaves or loses their device:
- **Selective wipe (APP):** Removes only corporate data and accounts from managed apps
- **Full wipe (MDM):** Wipes the entire device (only possible with enrollment)

Selective wipe via MAM leaves personal photos, apps, and contacts completely untouched.

## Supported Apps

Apps must be **Intune-enlightened** to support APP:
- **Microsoft apps:** Teams, Outlook, Word, Excel, PowerPoint, Edge, OneDrive — all support APP natively
- **Third-party apps:** Many enterprise apps (Salesforce, Box, Adobe Acrobat) support Intune SDK
- **Line-of-business apps:** Wrap existing apps using the Intune App Wrapping Tool

## MAM Without Enrollment (MAM-WE)

The most powerful BYOD scenario:
- No MDM enrollment required on the device
- User installs Company Portal (or just the managed app)
- User signs in with work account within the app
- APP is applied to the managed app — corporate data is protected
- Device itself is NOT managed by IT

Perfect for: contractors, employees using personal iPhones, students with their own iPads.

## Deployment

1. Create an App Protection Policy in Intune admin center
2. Configure data protection and access requirement settings
3. Assign to user groups (not device groups — MAM is user-centric)
4. Users receive the policy when they sign into a managed app with their work account

## Key Takeaways

- **App Protection Policies** protect corporate data within apps, even on unmanaged personal devices
- They control data transfer (copy/paste, save-as), access (PIN, biometrics), and conditional launch
- **Selective wipe** removes only corporate data — personal data is never touched
- **MAM without enrollment** is ideal for BYOD — no device management profile required
- Microsoft 365 apps (Outlook, Teams, Word) natively support APP with no additional configuration
- APP is assigned to **user groups**, not device groups""",
    },

    "BitLocker": {
        "readingTime": 5,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/protect-devices-with-microsoft-intune/",
        "body": """## BitLocker Drive Encryption

**BitLocker** is Windows' built-in full-disk encryption technology. When managed via Intune, it ensures corporate devices store data in encrypted form — protecting data if a device is lost or stolen.

## How BitLocker Works

BitLocker encrypts the entire drive using **AES encryption** (128-bit or 256-bit). Without the encryption key, data on the disk is unreadable — even if the drive is removed and connected to another PC.

**Key protectors** unlock the drive during boot:
- **TPM (Trusted Platform Module):** Hardware chip that stores the encryption key — most common for transparent encryption
- **TPM + PIN:** Requires user PIN at boot in addition to TPM
- **Recovery Key:** 48-digit numeric key as backup

## Intune BitLocker Configuration

Configure BitLocker via **Endpoint Security → Disk Encryption** in the Intune admin center.

**Key settings:**
- **Require BitLocker:** Enforce encryption on all Windows devices
- **Encryption method:** AES-CBC 128-bit (default) or AES-XTS 256-bit (recommended for new deployments)
- **Startup authentication:** TPM only vs. TPM + PIN vs. TPM + startup key
- **Recovery key backup:** Automatically escrow recovery keys to Entra ID — IT can retrieve them if needed

## BitLocker Recovery Keys in Entra ID

When Intune configures BitLocker, recovery keys are automatically **escrowed** (stored) in Entra ID:
- Admins can retrieve keys from Entra ID portal or Intune for device recovery
- Users can self-service recover their key from MyAccount.microsoft.com

This is critical — without a recovery key, a user locked out of their encrypted drive **cannot recover their data**.

## Silent Enablement

Intune can enable BitLocker **silently** (without user interaction) on devices that have:
- TPM 2.0
- Are Entra ID joined or Hybrid joined
- Running Windows 10 1803+ or Windows 11

No user prompts, no user action required — encryption happens in the background.

## Compliance Policy Integration

BitLocker is commonly required in **Intune Compliance Policies**:
```
Require BitLocker: Yes
Require Secure Boot: Yes
```
Non-compliant (unencrypted) devices are blocked from accessing corporate resources via Conditional Access.

## Key Takeaways

- BitLocker encrypts the entire Windows drive — data is unreadable without the key
- Intune can silently enable BitLocker on TPM 2.0 devices without user action
- Recovery keys are automatically escrowed to Entra ID — admins can retrieve them
- BitLocker is commonly enforced via compliance policies (block unencrypted devices)
- Use AES-XTS 256-bit encryption for maximum security on new deployments""",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MS-102 — Microsoft 365 Administrator
    # ══════════════════════════════════════════════════════════════════════════

    "Tenant Configuration": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/examine-microsoft-365-tenant/",
        "body": """## Microsoft 365 Tenant Configuration

A Microsoft 365 **tenant** is a dedicated instance of Entra ID (Azure Active Directory) and Microsoft 365 services for your organization.

## Initial Tenant Setup

### 1. Organization Profile
In the Microsoft 365 admin center (admin.microsoft.com):
- Set organization name, address, technical contact, and default language
- Configure release preferences:
  - **Targeted Release:** Preview new features early (small pilot group)
  - **Standard Release:** General availability rollout (all users)

### 2. Add and Verify Custom Domains

Your tenant starts with `yourcompany.onmicrosoft.com`. Add your own domain (e.g., `contoso.com`):

1. In admin center → Settings → Domains → Add Domain
2. Enter your domain name
3. Verify ownership by adding a **TXT record** to your domain's DNS:
   - `MS=ms12345678` (provided by Microsoft)
4. Add **MX records** to route email to Microsoft 365:
   - `contoso.com. MX 0 contoso-com.mail.protection.outlook.com`
5. Add **Autodiscover CNAME** for automatic Outlook configuration:
   - `autodiscover.contoso.com → autodiscover.outlook.com`

DNS propagation can take 24-72 hours. Test verification in the admin center.

### 3. Security Defaults vs. Conditional Access

New tenants have **Security Defaults** enabled — a preconfigured baseline:
- Require MFA registration for all users
- Block legacy authentication
- Require MFA for admins on every sign-in
- MFA required when Entra ID detects risk

**When to disable Security Defaults:**
Only disable when implementing Conditional Access policies (which offer more granular control). You cannot use both simultaneously.

## Admin Roles in Microsoft 365

Apply least privilege — assign the minimum role needed:

| Role | Scope |
|------|-------|
| **Global Administrator** | Full control over entire tenant — use sparingly |
| **Exchange Administrator** | Mailboxes, mail flow, transport rules |
| **Teams Administrator** | Teams settings, meetings, voice calling |
| **User Administrator** | Create/manage users, reset passwords |
| **SharePoint Administrator** | SharePoint sites, OneDrive settings |
| **Security Administrator** | Security policies, Defender, Compliance |
| **Billing Administrator** | Manage subscriptions and purchases |

**Best practice:** Create at least two Global Admin accounts (one for daily use, one break-glass emergency account). Both should be protected with MFA and strong passwords.

## Microsoft 365 Admin Centers

| Admin Center | URL | Primary Function |
|---|---|---|
| Microsoft 365 | admin.microsoft.com | Users, licenses, domains |
| Exchange | admin.exchange.microsoft.com | Email, mailboxes |
| Teams | admin.teams.microsoft.com | Teams, meetings, calling |
| SharePoint | {tenant}-admin.sharepoint.com | SharePoint, OneDrive |
| Intune | intune.microsoft.com | Device management |
| Security | security.microsoft.com | Threats, compliance |
| Compliance | compliance.microsoft.com | DLP, eDiscovery, audit |
| Entra ID | entra.microsoft.com | Identity, access |

## License Management

### Assigning Licenses
- **Per-user assignment:** Manually assign in admin center
- **Group-based licensing:** Automatically assign licenses to Entra ID group members (requires Entra ID P1)

### License Types (Microsoft 365 Business)
| Plan | Target | Key Features |
|------|--------|-------------|
| **Business Basic** | Small business | Web apps, Teams, Exchange |
| **Business Standard** | SMB with desktop apps | Everything + desktop Office |
| **Business Premium** | SMB with security needs | Everything + Intune + Defender |

## Hybrid Identity with Entra Connect

For organizations with on-premises Active Directory:
- **Microsoft Entra Connect:** Syncs users/groups from on-prem AD to Entra ID
- **Password Hash Sync (recommended):** Syncs password hashes, enables cloud authentication
- **Pass-Through Authentication:** Authentication happens on-premises
- Enables **single sign-on** — same credentials for on-prem and cloud

## Key Takeaways

- Custom domain verification requires adding a TXT record to your DNS
- Disable Security Defaults only when replacing with Conditional Access policies
- Use least-privilege admin roles — Global Admin should be used rarely
- Group-based licensing (requires Entra ID P1) simplifies license management at scale
- Entra Connect synchronizes on-premises AD identities to Microsoft 365/Entra ID""",
    },

    "Data Loss Prevention": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/implement-data-loss-prevention-policies/",
        "body": """## Data Loss Prevention (DLP) in Microsoft 365

**Data Loss Prevention (DLP)** policies help organizations prevent sensitive information from being accidentally or intentionally shared outside the organization or in inappropriate ways.

## What DLP Protects

DLP can detect and protect sensitive information types across:
- **Exchange Online:** Emails and attachments
- **SharePoint Online:** Files in SharePoint sites
- **OneDrive for Business:** Personally shared files
- **Microsoft Teams:** Chat messages and channel posts
- **Endpoint devices (Windows):** Files on managed Windows devices
- **On-premises:** Files on on-premises file servers (with Microsoft Purview)

## Sensitive Information Types (SITs)

DLP identifies sensitive data using **Sensitive Information Types** — pre-built or custom patterns:

**Built-in examples:**
- Credit card numbers (using Luhn algorithm + keyword validation)
- U.S. Social Security Numbers (SSN)
- European VAT numbers
- SWIFT/BIC codes
- Medical terms and drug names (for HIPAA)
- Passport numbers (supports 40+ countries)

**Custom SITs:**
Create your own patterns using regular expressions and keyword lists — e.g., your company's employee ID format or internal project codes.

## DLP Policy Components

A DLP policy consists of:

1. **Locations:** Where to monitor (Exchange, SharePoint, Teams, Endpoint, etc.)
2. **Conditions:** What triggers the rule (sensitive info type found, content shared externally, etc.)
3. **Actions:** What to do when conditions are met
4. **Exceptions:** Conditions that override the rule

### Common Actions

| Action | Description |
|--------|-------------|
| **Block** | Prevent the action entirely |
| **Block with override** | Block but allow user to override with business justification |
| **Notify user** | Show policy tip in the app; email the user |
| **Alert admin** | Send email alert to compliance team |
| **Incident report** | Log to Microsoft Purview compliance portal |
| **Encrypt (email)** | Apply OME encryption to outbound email |

## Policy Tips

When a user is about to violate a DLP policy, they see a **policy tip** — a yellow notification in the app (Outlook, Teams, SharePoint) explaining why their action is being blocked or warned.

Users with appropriate permissions can override with a business justification (if configured). All overrides are logged.

## DLP in Teams

DLP in Microsoft Teams:
- Scans chat messages and channel posts for sensitive content
- Can block sending if a credit card number is detected in a Teams chat
- Supports both 1:1 chats and channel conversations

**Example rule:** If a Teams message contains a credit card number, block the message and notify the sender.

## Endpoint DLP

**Endpoint DLP** extends protection to Windows 10/11 devices managed by Intune:

Monitors and controls:
- Uploading sensitive files to cloud services (Google Drive, Dropbox)
- Copying sensitive files to USB drives
- Printing sensitive documents
- Screen capture of sensitive content (some apps)
- Copying to clipboard and pasting into unsanctioned apps

## Creating a DLP Policy

1. Go to Microsoft Purview Compliance Portal → Data Loss Prevention → Policies → Create Policy
2. Choose a template (Financial, Medical, Privacy, Custom)
3. Select locations
4. Define rules (sensitive info types, conditions)
5. Configure actions (block, notify, alert)
6. Set policy to **Test mode** first → review incidents → then turn on enforcement

**Always test before enforcing** — an overly aggressive DLP policy can disrupt legitimate business processes.

## Key Takeaways

- DLP prevents accidental/intentional sharing of sensitive data across M365 services and endpoints
- Built-in Sensitive Information Types cover common PII, financial, and healthcare data
- Policy tips notify users in-context before they violate a policy
- **Test mode** lets you assess policy impact before enforcement
- Endpoint DLP extends protection to file activities on managed Windows devices
- All policy matches, overrides, and incidents are logged in the Purview compliance portal""",
    },

    "Teams Administration": {
        "readingTime": 10,
        "msLearnUrl": "https://learn.microsoft.com/en-us/training/modules/manage-microsoft-teams/",
        "body": """## Microsoft Teams Administration

As a Microsoft 365 administrator, you manage the Teams environment using the **Microsoft Teams Admin Center** (admin.teams.microsoft.com) and PowerShell.

## Teams Architecture

Microsoft Teams is built on top of Microsoft 365 services:
- **Identity:** Microsoft Entra ID
- **Meetings:** Teams Meeting infrastructure + Azure Media Services
- **Files:** SharePoint Online (channel files) and OneDrive (chat files)
- **Email/Calendar:** Exchange Online
- **Compliance:** Microsoft Purview

Every Teams **team** creates:
- An **Microsoft 365 Group** in Entra ID
- A **SharePoint site** for file storage
- A **Group mailbox** in Exchange

## Teams, Channels, and Chat

### Teams
A team is a collection of people, content, and tools organized around a project or department. Team types:
- **Org-wide:** Automatically includes all users in the tenant (max 10,000 members)
- **Private:** Invite-only membership
- **Public:** Anyone in the org can join

### Channels
Channels are the work areas within a team. Three types:
- **Standard:** Visible to all team members
- **Private:** Visible only to specific team members (has its own SharePoint folder)
- **Shared:** Can include people from outside the team or organization

### Chat
1:1 and group chats outside of teams/channels. Files shared in chat go to OneDrive.

## Teams Policies

### Meeting Policies
Control what users can do in Teams meetings:
- **Allow cloud recording:** Enable/disable recording capability
- **Allow transcription:** Auto-transcription of meetings
- **Who can bypass lobby:** Anyone vs. people in your org vs. organizer only
- **Allow external participants to give/request control:** Screen sharing control
- **Allow IP video:** Enable/disable video for bandwidth management

### Messaging Policies
Control chat and channel messaging behavior:
- Enable/disable: GIFs, memes, stickers, immersive reader
- Allow users to edit/delete sent messages
- Enable read receipts
- Enable priority notifications

### App Permission Policies
Control which apps users can install in Teams:
- **Microsoft apps:** Allow all or specific apps from Microsoft
- **Third-party apps:** Allow all, specific, or block all
- **Custom/LOB apps:** Allow or block custom apps

## Teams Governance

### Team Creation
By default, any Microsoft 365 user can create a team (which creates an M365 Group).

**To restrict team creation:**
- Create an Entra ID group containing users allowed to create teams
- Apply the M365 Groups creation restriction via PowerShell or Entra ID settings

### Expiration Policies
Set teams to expire after a period of inactivity:
- Team owners receive renewal notifications
- Expired teams are soft-deleted (recoverable for 30 days)
- Helps prevent sprawl of abandoned teams

### Naming Policies
Enforce naming conventions for M365 Groups (and therefore teams):
- **Prefix/Suffix:** Auto-append `[Dept]` or `_Confidential` to team names
- **Blocked words:** Prevent offensive or restricted terms in team names

## External Access vs. Guest Access

| | External Access (Federation) | Guest Access |
|--|------------------------------|-------------|
| User type | Users from other M365 tenants | Any email address |
| Management | Managed in your tenant | Added as Entra ID guest users |
| Capabilities | Chat and call only | Full Teams experience in specific teams |
| License required | No | Yes (Entra ID P1 for governance features) |

## Teams Phone (Calling)

If your org uses Teams for calling:
- **Calling Plans:** Microsoft-provided PSTN connectivity (licenses per user)
- **Direct Routing:** Connect your own telephony infrastructure to Teams via a Session Border Controller (SBC)
- **Operator Connect:** Partner carrier provides PSTN in Teams admin center

## Key Takeaways

- Every Teams team creates an M365 Group, SharePoint site, and Group mailbox
- Meeting, messaging, and app policies control the Teams user experience
- Restrict team creation to prevent sprawl; use expiration policies for lifecycle management
- **External Access** = federated chat with other orgs; **Guest Access** = outside users with full team membership
- Teams Phone supports Calling Plans, Direct Routing, and Operator Connect for PSTN calling""",
    },
}


def seed_content(cert_filter=None):
    """Update topics in the database with learning content."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    updated = 0
    skipped = 0
    not_found = []

    for topic_title, data in CONTENT.items():
        if cert_filter:
            cur.execute("""
                SELECT t.id FROM "Topic" t
                JOIN "Module" m ON t."moduleId" = m.id
                JOIN "Certification" c ON m."certificationId" = c.id
                WHERE t.title = %s AND c.code = %s
            """, (topic_title, cert_filter))
        else:
            cur.execute('SELECT id FROM "Topic" WHERE title = %s', (topic_title,))

        rows = cur.fetchall()
        if not rows:
            not_found.append(topic_title)
            skipped += 1
            continue

        for (topic_id,) in rows:
            cur.execute("""
                UPDATE "Topic"
                SET content = %s,
                    "readingTime" = %s,
                    "msLearnUrl" = %s
                WHERE id = %s
            """, (data["body"], data["readingTime"], data["msLearnUrl"], topic_id))
            updated += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✓ Updated {updated} topics with learning content")
    if not_found:
        print(f"⚠  Not found in DB (check topic names): {not_found}")
    if updated == 0 and not_found:
        print("   → Run seed_sample.py first to create topics, then re-run seed_content.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed learning content into Topic table")
    parser.add_argument("--cert", help="Only seed for a specific cert code (e.g. AZ-900)")
    args = parser.parse_args()

    print("Seeding learning content...")
    seed_content(cert_filter=args.cert.upper() if args.cert else None)
