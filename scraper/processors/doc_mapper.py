"""
Maps questions to Microsoft Learn documentation URLs based on content analysis.
"""

import re
from typing import Optional


# Keyword → MS Learn URL patterns for AZ-900
AZ900_DOC_MAP = {
    "cloud models": "https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/considerations/fundamental-concepts",
    "public cloud": "https://learn.microsoft.com/en-us/azure/architecture/framework/",
    "private cloud": "https://learn.microsoft.com/en-us/azure/architecture/framework/",
    "hybrid cloud": "https://learn.microsoft.com/en-us/azure/architecture/framework/",
    "iaas": "https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-overview",
    "paas": "https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-overview",
    "saas": "https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-overview",
    "azure region": "https://learn.microsoft.com/en-us/azure/availability-zones/overview",
    "availability zone": "https://learn.microsoft.com/en-us/azure/availability-zones/overview",
    "azure resource manager": "https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview",
    "resource group": "https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal",
    "subscription": "https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/create-subscription",
    "management group": "https://learn.microsoft.com/en-us/azure/governance/management-groups/overview",
    "azure active directory": "https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/active-directory-whatis",
    "azure ad": "https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/active-directory-whatis",
    "rbac": "https://learn.microsoft.com/en-us/azure/role-based-access-control/overview",
    "role-based access control": "https://learn.microsoft.com/en-us/azure/role-based-access-control/overview",
    "azure policy": "https://learn.microsoft.com/en-us/azure/governance/policy/overview",
    "azure virtual machine": "https://learn.microsoft.com/en-us/azure/virtual-machines/overview",
    "vm": "https://learn.microsoft.com/en-us/azure/virtual-machines/overview",
    "azure storage": "https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction",
    "blob storage": "https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction",
    "azure sql": "https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview",
    "cosmos db": "https://learn.microsoft.com/en-us/azure/cosmos-db/introduction",
    "azure kubernetes": "https://learn.microsoft.com/en-us/azure/aks/intro-kubernetes",
    "aks": "https://learn.microsoft.com/en-us/azure/aks/intro-kubernetes",
    "azure container": "https://learn.microsoft.com/en-us/azure/container-instances/container-instances-overview",
    "azure functions": "https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview",
    "serverless": "https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview",
    "azure monitor": "https://learn.microsoft.com/en-us/azure/azure-monitor/overview",
    "azure security center": "https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction",
    "defender for cloud": "https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction",
    "azure cost management": "https://learn.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview",
    "total cost of ownership": "https://learn.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview",
    "tco": "https://learn.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview",
    "sla": "https://learn.microsoft.com/en-us/azure/reliability/overview",
    "service level agreement": "https://learn.microsoft.com/en-us/azure/reliability/overview",
}


def find_documentation_links(question_text: str, cert_code: str) -> list[dict]:
    """
    Find relevant documentation links for a question based on keyword matching.
    Returns a list of {url, title} dicts.
    """
    text_lower = question_text.lower()
    found_links = {}

    doc_map = _get_doc_map(cert_code)

    for keyword, url in doc_map.items():
        if keyword in text_lower and url not in found_links:
            title = _url_to_title(url)
            found_links[url] = {"url": url, "title": title}
            if len(found_links) >= 3:
                break

    return list(found_links.values())


def _get_doc_map(cert_code: str) -> dict:
    """Get the keyword→URL map for a specific cert."""
    maps = {
        "AZ-900": AZ900_DOC_MAP,
        "AZ-104": AZ900_DOC_MAP,  # Use same map for now, extend later
        "MD-102": AZ900_DOC_MAP,
        "MS-102": AZ900_DOC_MAP,
    }
    return maps.get(cert_code, AZ900_DOC_MAP)


def _url_to_title(url: str) -> str:
    """Convert a URL to a human-readable title."""
    path = url.split("learn.microsoft.com/en-us/")[-1].rstrip("/")
    parts = path.split("/")
    # Take last 2 meaningful parts
    title = " › ".join(
        part.replace("-", " ").title()
        for part in parts[-2:]
        if part and part != "overview"
    )
    return title or "Microsoft Learn Documentation"
