"""
Scraper for Microsoft Learn training module content.

Strategy:
1. Use the MS Learn Catalog API to discover unit URLs for each module.
2. Fetch each unit page (SSR HTML) and extract article text from #module-unit-content.
3. Concatenate unit texts into one markdown block per topic.

No Playwright required — MS Learn unit pages are server-side rendered.
"""

import json
import time
import re
import urllib.request
from typing import Optional
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ─── Topic → MS Learn module UID mapping ─────────────────────────────────────
# UIDs come from the MS Learn Catalog API (https://learn.microsoft.com/api/learn/catalog)
# Each entry: (db_topic_title, module_uid)

CERT_MODULES = {
    "AZ-900": [
        ("Cloud Service Types",           "learn.wwl.describe-cloud-service-types"),
        ("Benefits of Cloud",             "learn.wwl.describe-benefits-use-cloud-services"),
        ("Cloud Deployment Models",       "learn.wwl.describe-cloud-compute"),
        ("Regions and Availability Zones","learn.wwl.describe-core-architectural-components-of-azure"),
        ("Resource Organization",         "learn.wwl.describe-core-architectural-components-of-azure"),
        ("Compute Services",              "learn.wwl.describe-azure-compute-networking-services"),
        ("Networking Services",           "learn.wwl.describe-azure-compute-networking-services"),
        ("Storage Services",              "learn.wwl.describe-azure-storage-services"),
        ("Identity and Access",           "learn.wwl.describe-azure-identity-access-security"),
        ("Cost Management",               "learn.wwl.describe-cost-management-azure"),
        ("Governance Tools",              "learn.wwl.describe-features-tools-azure-for-governance-compliance"),
        ("Deployment Tools",              "learn.wwl.describe-features-tools-manage-deploy-azure-resources"),
        ("Monitoring Tools",              "learn.wwl.describe-monitoring-tools-azure"),
    ],
    "AZ-104": [
        ("Identity and Governance",       "learn.wwl.manage-azure-active-directory-identities"),
        ("Networking",                    "learn.wwl.configure-virtual-networks"),
    ],
    "MD-102": [
        ("Windows Autopilot",             "learn.wwl.deploy-devices-windows-autopilot"),
        ("Intune Enrollment",             "learn.wwl.enroll-devices-use-intune"),
        ("Compliance Policies",           "learn.wwl.implement-device-compliance-policies"),
        ("App Protection Policies",       "learn.wwl.execute-mobile-application-management"),
        ("BitLocker",                     "learn.wwl.deploy-device-data-protection"),
        ("Configuration Profiles",        "learn.wwl.execute-device-profiles"),
        ("Defender for Endpoint",         "learn.wwl.manage-defender-endpoint"),
        ("Windows Update Rings",          "learn.wwl.implement-endpoint-protection"),
        ("Conditional Access",            "learn.wwl.plan-implement-administer-conditional-access"),
        ("Remote Actions",                "learn.wwl.harden-endpoints-monitor-security-intune-defender-endpoint"),
        ("App Deployment",                "learn.wwl.execute-mobile-application-management"),
        ("Entra ID Join",                 "learn.wwl.deploy-devices-windows-autopilot"),
        ("Co-management",                 "learn.wwl.implement-endpoint-protection"),
        ("Intune Roles",                  "learn.wwl.discover-microsoft-intune-essentials"),
    ],
    "MS-102": [
        ("Tenant Configuration",          "learn.wwl.configure-microsoft-365-experience"),
        ("Microsoft Entra ID",            "learn.azure-security.manage-users-and-groups-in-aad"),
        ("Conditional Access",            "learn.wwl.plan-implement-administer-conditional-access"),
        ("Hybrid Identity",               "learn.wwl.implement-manage-hybrid-identity"),
        ("Self-Service Password Reset",   "learn.azure.allow-users-to-reset-their-password"),
        ("Exchange Online",               "learn.wwl.examine-exchange-online-protection"),
        ("Microsoft Teams",               "learn.wwl.configure-deploy-manage-teams-devices"),
        ("Defender for Office 365",       "learn.wwl.examine-microsoft-defender-office-365"),
        ("Microsoft Purview",             "learn.wwl.apply-manage-sensitivity-labels"),
        ("Data Loss Prevention",          "learn.wwl.create-configure-data-loss-prevention-policies"),
        ("Reports and Monitoring",        "learn.wwl.respond-to-data-loss-prevention-alerts-microsoft-365"),
        ("Service Health",                "learn.wwl.configure-microsoft-365-experience"),
        ("Teams Administration",          "learn.wwl.configure-deploy-manage-teams-devices"),
        ("SharePoint Online",             "learn.wwl.manage-sharepoint-online-use-windows-powershell"),
        ("Licensing",                     "learn.azure-security.manage-users-and-groups-in-aad"),
    ],
}

# Skip these unit types — they have no real article content
SKIP_UNIT_SUFFIXES = ("knowledge-check", "summary", "introduction", "exercise")


def _fetch(url: str) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"      [fetch error] {url}: {e}")
        return None


def _get_module_units(module_uid: str) -> Optional[dict]:
    """
    Query the MS Learn Catalog API for a module's units and firstUnitUrl.
    Returns {"slug": str, "units": [uid, ...], "firstUnitUrl": str} or None.
    """
    url = f"https://learn.microsoft.com/api/learn/catalog?uid={module_uid}&locale=en-us"
    html = _fetch(url)
    if not html:
        return None
    try:
        data = json.loads(html)
        modules = data.get("modules", [])
        mod = next((m for m in modules if module_uid in m["uid"]), None)
        if not mod:
            return None
        # Extract module slug from firstUnitUrl
        first_url = mod.get("firstUnitUrl", "")
        # e.g. https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/1-introduction/
        m = re.search(r"/training/modules/([^/]+)/", first_url)
        slug = m.group(1) if m else module_uid.split(".")[-1]
        return {
            "slug": slug,
            "units": mod.get("units", []),
            "firstUnitUrl": first_url,
        }
    except Exception as e:
        print(f"      [catalog parse error] {module_uid}: {e}")
        return None


def _unit_url(module_slug: str, unit_index: int, unit_uid: str) -> str:
    """Construct a unit page URL from module slug, index (1-based), and unit UID."""
    unit_slug = unit_uid.split(".")[-1]
    return (
        f"https://learn.microsoft.com/en-us/training/modules/"
        f"{module_slug}/{unit_index}-{unit_slug}/"
    )


def _extract_unit_content(html: str) -> str:
    """Extract article text from #module-unit-content on a MS Learn unit page."""
    soup = BeautifulSoup(html, "lxml")

    # Remove non-content elements
    for tag in soup.select("script, style, noscript, .xp-tag, .metadata, iframe"):
        tag.decompose()

    content_el = soup.select_one("#module-unit-content")
    if not content_el:
        return ""

    return _html_to_markdown(content_el)


def _html_to_markdown(el) -> str:
    """Convert a BeautifulSoup element to readable markdown text."""
    lines: list[str] = []

    def walk(node):
        if not hasattr(node, "name"):
            return
        name = node.name

        if name in ("h1", "h2"):
            text = node.get_text(" ", strip=True)
            if text:
                lines.append(f"\n## {text}\n")
        elif name == "h3":
            text = node.get_text(" ", strip=True)
            if text:
                lines.append(f"\n### {text}\n")
        elif name in ("h4", "h5", "h6"):
            text = node.get_text(" ", strip=True)
            if text:
                lines.append(f"\n**{text}**\n")
        elif name == "p":
            text = node.get_text(" ", strip=True)
            if text and len(text) > 10:
                lines.append(f"\n{text}\n")
        elif name in ("ul", "ol"):
            for li in node.find_all("li", recursive=False):
                text = li.get_text(" ", strip=True)
                if text:
                    lines.append(f"- {text}")
            lines.append("")
        elif name == "table":
            for row in node.find_all("tr"):
                cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
                if any(cells):
                    lines.append("- " + " | ".join(c for c in cells if c))
            lines.append("")
        elif name in ("div", "section", "article", "main"):
            for child in node.children:
                walk(child)

    walk(el)

    text = "\n".join(lines)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _estimate_reading_time(text: str) -> int:
    words = len(text.split())
    return max(2, round(words / 200))


def scrape_module_content(module_uid: str, module_title: str) -> Optional[dict]:
    """
    Scrape all content units for a single MS Learn module.
    Returns {"content": str, "msLearnUrl": str, "readingTime": int} or None.
    """
    print(f"    Querying catalog for: {module_uid}")
    info = _get_module_units(module_uid)
    if not info:
        print(f"      → module not found in catalog")
        return None

    slug = info["slug"]
    units = info["units"]
    module_url = f"https://learn.microsoft.com/en-us/training/modules/{slug}/"

    content_parts: list[str] = []

    for i, unit_uid in enumerate(units, 1):
        unit_slug_last = unit_uid.split(".")[-1]

        # Skip non-content units
        if any(unit_slug_last.endswith(s) for s in SKIP_UNIT_SUFFIXES):
            continue

        url = _unit_url(slug, i, unit_uid)
        html = _fetch(url)
        if not html:
            continue

        unit_text = _extract_unit_content(html)
        if len(unit_text) > 50:
            content_parts.append(unit_text)
            print(f"      unit {i}: {len(unit_text)}b")
        time.sleep(0.3)

    if not content_parts:
        print(f"      → no content extracted")
        return None

    combined = "\n\n---\n\n".join(content_parts)
    return {
        "content": combined,
        "msLearnUrl": module_url,
        "readingTime": _estimate_reading_time(combined),
    }


def scrape_cert_content(cert_code: str) -> list[dict]:
    """
    Scrape MS Learn content for all topics of a given cert.
    Returns list of {title, msLearnUrl, content, readingTime}.
    """
    modules = CERT_MODULES.get(cert_code.upper(), [])
    if not modules:
        print(f"  No modules defined for {cert_code}")
        return []

    results: list[dict] = []
    cache: dict[str, Optional[dict]] = {}  # uid → scraped result

    for topic_title, module_uid in modules:
        print(f"  Topic: {topic_title}")

        if module_uid not in cache:
            cache[module_uid] = scrape_module_content(module_uid, topic_title)
            time.sleep(0.5)

        scraped = cache[module_uid]
        if not scraped:
            continue

        results.append({
            "title": topic_title,
            "msLearnUrl": scraped["msLearnUrl"],
            "content": scraped["content"],
            "readingTime": scraped["readingTime"],
        })
        print(f"    → {len(scraped['content'])}b, ~{scraped['readingTime']} min read")

    return results
