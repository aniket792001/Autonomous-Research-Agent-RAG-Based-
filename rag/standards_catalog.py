"""
Regulatory Standards & Frameworks Catalog for AegisAudit AI.
Provides pre-seeded, industry-standard compliance frameworks for instant auditing.
"""

from pathlib import Path
from typing import Dict, Any, List
from core.config import settings
from core.logger import logger

STANDARDS_CATALOG: Dict[str, Dict[str, Any]] = {
    "iso_27001_2022": {
        "key": "iso_27001_2022",
        "title": "ISO/IEC 27001:2022",
        "full_name": "ISO/IEC 27001:2022 Information Security Management System (ISMS)",
        "badge": "Security & Risk",
        "category": "International Standard",
        "clause_count": 93,
        "description": "The global benchmark for establishing, implementing, maintaining and continually improving an information security management system.",
        "key_controls": [
            "A.5.15 Access control & authentication",
            "A.5.24 Information security incident management planning",
            "A.8.1 User endpoint devices & mobile working",
            "A.8.5 Secure authentication procedures & MFA",
            "A.8.7 Protection against malware & EDR",
            "A.8.8 Management of technical vulnerabilities",
            "A.8.12 Data leakage prevention (DLP)",
            "A.8.20 Network security & segmentation",
            "A.8.24 Use of cryptography & key management"
        ],
        "content": """# ISO/IEC 27001:2022 - Annex A Information Security Controls

## Domain 5: Organizational Controls
### Control A.5.15: Access control
Rules to control physical and logical access to information and other associated assets shall be established and implemented based on business and information security requirements. The organization must enforce least privilege, role-based access control (RBAC), and regular entitlement reviews every 90 days.

### Control A.5.24: Information security incident management planning and preparation
The organization shall plan and prepare for managing information security incidents by defining, establishing and communicating information security incident management processes, roles and responsibilities. The incident response plan must define severity triage levels, escalation chains, and mandatory response timeframes (maximum 1 hour for critical incidents).

### Control A.5.29: Information security during disruption
The organization shall establish processes to maintain information security at an appropriate level during disruption. Disaster recovery and business continuity plans must be tested at least annually with documented RTO (Recovery Time Objective) and RPO (Recovery Point Objective) targets.

## Domain 8: Technological Controls
### Control A.8.1: User endpoint devices
Information stored on, processed by or accessible via user endpoint devices shall be protected. Mobile and remote workstation policies shall mandate full-disk encryption (AES-256 or BitLocker), centralized mobile device management (MDM), remote wipe capability, and automated idle lock after a maximum of 10 minutes.

### Control A.8.5: Secure authentication
Secure authentication technologies and procedures shall be implemented based on information access restrictions and the topic-specific policy on access control. Multi-Factor Authentication (MFA) must be strictly enforced for all remote access, privileged administrative accounts, and production cloud infrastructure.

### Control A.8.7: Protection against malware
Protection against malware shall be implemented and supported by appropriate user awareness. All endpoint and server systems must run continuously updating Endpoint Detection & Response (EDR) software with real-time file system monitoring and centralized alerting.

### Control A.8.8: Management of technical vulnerabilities
Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities evaluated and appropriate measures taken. Automated vulnerability scanning must occur at least weekly, with critical CVE patches deployed within 14 days of vendor release.

### Control A.8.12: Data leakage prevention
Data leakage prevention measures shall be applied to systems, networks and any other devices that process, store or transmit sensitive information. Outbound communications, email attachments, and external USB storage devices must be monitored and restricted using automated DLP mechanisms.

### Control A.8.20: Network security
Networks and network devices shall be secured, managed and controlled to protect information in systems and applications. Production networks must be logically isolated from development, testing, and corporate office networks using zero-trust firewall rules and encrypted VPN gateways.

### Control A.8.24: Use of cryptography
Rules for the effective use of cryptography, including cryptographic key management, shall be defined and implemented. All sensitive data-at-rest must be encrypted using AES-256 or higher, and all data-in-transit must enforce TLS 1.3 (with TLS 1.2 minimum). Cryptographic keys must be rotated at least annually.
"""
    },
    "soc_2_type_ii": {
        "key": "soc_2_type_ii",
        "title": "SOC 2 Type II",
        "full_name": "AICPA SOC 2 Type II - Trust Services Criteria",
        "badge": "Trust & Privacy",
        "category": "AICPA Framework",
        "clause_count": 64,
        "description": "Standardized criteria evaluating an organization's controls related to Security, Availability, Processing Integrity, Confidentiality, and Privacy.",
        "key_controls": [
            "CC6.1 Logical access security architecture & controls",
            "CC6.2 User registration, modification & de-provisioning",
            "CC6.6 Perimeter & boundary protection against unauthorized access",
            "CC6.8 Defense against malicious software & intrusion",
            "CC7.1 Vulnerability assessment & patch management",
            "CC7.2 Security anomaly & audit log monitoring",
            "CC7.3 Security incident response execution & post-mortem",
            "CC8.1 Change management & peer review procedures"
        ],
        "content": """# AICPA SOC 2 Type II - Trust Services Criteria (Common Criteria)

## Common Criteria 6: Logical and Physical Access Controls
### Criterion CC6.1: Access Architecture
The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events. All production systems require individual authenticated identities; shared or generic administrative credentials are explicitly prohibited.

### Criterion CC6.2: User Registration & Lifecycle
Prior to issuing system credentials and granting system access, the entity registers and authorizes new internal and external users. Access permissions must be approved by the asset owner. Offboarding procedures must revoke all physical and logical access within 24 hours of employee departure.

### Criterion CC6.6: Boundary Protection
The entity implements boundary protection measures to safeguard system components against unauthorized communication and external network intrusion. Ingress and egress traffic must traverse modern next-generation firewalls with default-deny rules. Remote administrative connections require MFA and encrypted bastion hosts.

### Criterion CC6.8: Malicious Software Defense
The entity implements controls to prevent or detect and act upon the introduction of unauthorized or malicious software. Workstations and production virtual machines must run host-based anti-malware and Endpoint Detection and Response (EDR) agents with continuous heuristic scanning.

## Common Criteria 7: System Operations & Incident Management
### Criterion CC7.1: Vulnerability Management
To meet its objectives, the entity uses detection and monitoring procedures to identify changes to configurations that result in the introduction of new vulnerabilities, and implements corrective actions. Monthly authenticated vulnerability scans must be conducted across all public and internal IP spaces.

### Criterion CC7.2: Security Anomaly Monitoring
The entity monitors system components and the operation of those components for anomalies that are indicative of malicious acts, natural disasters, and errors. Centralized log management (SIEM) must aggregate system, access, and audit logs with at least 365 days of retention.

### Criterion CC7.3: Incident Response
The entity evaluates and responds to identified security events and incidents to remediate and document the incidents. An Incident Response Team (IRT) must maintain documented incident playbooks, conduct semi-annual tabletop simulations, and complete post-incident root-cause analyses within 5 business days.

## Common Criteria 8: Change Management
### Criterion CC8.1: Change Authorization & Deployment
The entity authorizes, designs, develops or acquires, configures, tests, approves, and implements changes to infrastructure, data, software, and procedures. All source code modifications require automated CI/CD pipeline testing, vulnerability scanning, and mandatory peer code review before merge to production.
"""
    },
    "gdpr_compliance": {
        "key": "gdpr_compliance",
        "title": "GDPR (EU 2016/679)",
        "full_name": "EU General Data Protection Regulation (GDPR)",
        "badge": "Data Privacy",
        "category": "Regulatory Law",
        "clause_count": 99,
        "description": "Comprehensive European regulation on data protection and privacy for all individuals within the European Union and the European Economic Area.",
        "key_controls": [
            "Article 25: Data protection by design and by default",
            "Article 32(1)(a): Pseudonymisation and encryption of personal data",
            "Article 32(1)(b): Confidentiality, integrity, availability and resilience",
            "Article 32(1)(d): Regular testing and evaluation of technical measures",
            "Article 33: Notification of personal data breach within 72 hours",
            "Article 35: Data Protection Impact Assessment (DPIA)"
        ],
        "content": """# EU General Data Protection Regulation (Regulation (EU) 2016/679)

## Chapter IV: Controller and Processor
### Article 25: Data protection by design and by default
The controller shall implement appropriate technical and organisational measures, such as pseudonymisation, which are designed to implement data-protection principles, such as data minimisation, in an effective manner. By default, only personal data which are necessary for each specific purpose of the processing are collected, stored, and retained.

### Article 32: Security of processing - Mandate 1
Taking into account the state of the art, costs of implementation, and nature of processing, the controller and processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including:
(a) the pseudonymisation and encryption of personal data in transit and at rest using modern cryptographic algorithms;
(b) the ability to ensure the ongoing confidentiality, integrity, availability and resilience of processing systems and services.

### Article 32: Security of processing - Mandate 2
The controller and processor shall implement:
(c) the ability to restore the availability and access to personal data in a timely manner in the event of a physical or technical incident;
(d) a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of the processing.

### Article 33: Notification of a personal data breach to the supervisory authority
In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority competent in accordance with Article 55, unless the personal data breach is unlikely to result in a risk to the rights and freedoms of natural persons.

### Article 35: Data protection impact assessment (DPIA)
Where a type of processing in particular using new technologies, and taking into account the nature, scope, context and purposes of the processing, is likely to result in a high risk to the rights and freedoms of natural persons, the controller shall, prior to the processing, carry out an assessment of the impact of the envisaged processing operations on the protection of personal data.
"""
    },
    "nist_csf_2_0": {
        "key": "nist_csf_2_0",
        "title": "NIST CSF 2.0",
        "full_name": "NIST Cybersecurity Framework 2.0 (Govern, Identify, Protect, Detect, Respond, Recover)",
        "badge": "Federal & Enterprise",
        "category": "NIST Framework",
        "clause_count": 106,
        "description": "The definitive guidance released by the National Institute of Standards and Technology for reducing cybersecurity risks across six core functions.",
        "key_controls": [
            "GV.OC-01 Organizational Mission & Cybersecurity Context",
            "PR.AA-01 Identity management & credential issuance",
            "PR.AA-05 Access permissions & separation of duties",
            "PR.DS-01 Confidentiality, integrity & availability of data-at-rest",
            "PR.DS-02 Protection of data-in-transit",
            "DE.CM-01 Continuous network and compute monitoring",
            "RS.MA-01 Incident response plan execution"
        ],
        "content": """# NIST Cybersecurity Framework 2.0 (NIST CSF 2.0)

## Function 1: Govern (GV)
### Subcategory GV.OC-01: Organizational Context
The organizational context—including mission, stakeholder expectations, legal and regulatory requirements—is understood and informs cybersecurity risk management decisions. Cybersecurity roles and governance committees must meet at least quarterly.

## Function 2: Protect (PR)
### Subcategory PR.AA-01: Identity and Access Management
Identities and credentials for authorized users, services, and hardware are managed, verified, and revoked. Unique user identifiers must be issued, passwords must adhere to NIST SP 800-63B standards (minimum 12 characters), and credentials must never be hardcoded into configuration files or scripts.

### Subcategory PR.AA-05: Least Privilege Access
Access permissions, entitlements, and authorizations are managed in accordance with the principles of least privilege and separation of duties. Privileged administrative rights require formal management authorization and regular recertification.

### Subcategory PR.DS-01: Protection of Data at Rest
Data at rest across databases, block storage, and local backups is protected using cryptographic algorithms approved by FIPS 140-3. Cryptographic keys must be protected against unauthorized disclosure and maintained in dedicated hardware security modules (HSMs).

### Subcategory PR.DS-02: Protection of Data in Transit
Data in transit across external public networks and between internal subnets is protected against eavesdropping and tampering using TLS 1.3 or IPsec with strong forward secrecy cipher suites.

## Function 3: Detect (DE)
### Subcategory DE.CM-01: Continuous Monitoring
Networks, computing infrastructure, and physical environments are continuously monitored to locate potential cybersecurity events. Security Operations Center (SOC) telemetry must alert on unauthorized access attempts, configuration drift, and known indicators of compromise (IoCs).

## Function 4: Respond (RS)
### Subcategory RS.MA-01: Incident Plan Execution
The incident management plan is executed once an incident is declared. Response procedures must include containment, evidence preservation, stakeholder notifications, and regulatory disclosures within legally defined time constraints.
"""
    }
}

class StandardsCatalogService:
    @staticmethod
    def list_standards() -> List[Dict[str, Any]]:
        """Returns metadata for all available pre-seeded standards."""
        return list(STANDARDS_CATALOG.values())

    @staticmethod
    def get_standard_meta(key: str) -> Dict[str, Any]:
        """Returns metadata for a specific standard key."""
        return STANDARDS_CATALOG.get(key, STANDARDS_CATALOG["iso_27001_2022"])

    @staticmethod
    def get_standard_file_path(key: str) -> Path:
        """
        Retrieves or dynamically writes the standard content to a text file in data/standards/.
        Returns the absolute Path to the file.
        """
        standards_dir = settings.DATA_DIR / "standards"
        standards_dir.mkdir(parents=True, exist_ok=True)
        
        meta = STANDARDS_CATALOG.get(key, STANDARDS_CATALOG["iso_27001_2022"])
        target_file = standards_dir / f"{key}.txt"
        
        # Write if not present or empty
        if not target_file.exists() or target_file.stat().st_size == 0:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(meta["content"])
            logger.info(f"StandardsCatalogService: Initialized pre-seeded standard at {target_file}")
            
        return target_file
