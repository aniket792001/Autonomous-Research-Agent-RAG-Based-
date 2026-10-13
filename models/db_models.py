"""
SQLAlchemy ORM Models for AegisAudit AI (Phase 3 Database Management).
Provides enterprise multi-tenant relational schema for Organizations, Users, Documents, Audits, and Findings.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("UserModel", back_populates="organization")
    documents = relationship("DocumentModel", back_populates="organization")
    audits = relationship("AuditRunModel", back_populates="organization")

class UserModel(Base):
    __tablename__ = "users_orm"

    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="auditor", nullable=False)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String(50), ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="users")
    audits_created = relationship("AuditRunModel", back_populates="creator")

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'standard' or 'policy'
    file_size_bytes = Column(Integer, default=0)
    total_pages = Column(Integer, default=1)
    sha256_hash = Column(String(64), index=True, nullable=True)
    storage_path = Column(String(500), nullable=False)
    organization_id = Column(String(50), ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="documents")

class AuditRunModel(Base):
    __tablename__ = "audit_runs_orm"

    id = Column(String(50), primary_key=True, index=True)
    standard_filename = Column(String(255), nullable=False)
    policy_filename = Column(String(255), nullable=False)
    compliance_score = Column(Float, default=0.0)
    total_clauses = Column(Integer, default=0)
    compliant_count = Column(Integer, default=0)
    partial_count = Column(Integer, default=0)
    non_compliant_count = Column(Integer, default=0)
    created_by = Column(String(50), ForeignKey("users_orm.id"), nullable=True)
    organization_id = Column(String(50), ForeignKey("organizations.id"), nullable=True)
    report_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="audits")
    creator = relationship("UserModel", back_populates="audits_created")
    findings = relationship("AuditFindingModel", back_populates="audit_run", cascade="all, delete-orphan")

class AuditFindingModel(Base):
    __tablename__ = "audit_findings"

    id = Column(String(50), primary_key=True, index=True)
    audit_run_id = Column(String(50), ForeignKey("audit_runs_orm.id"), nullable=False)
    clause_id = Column(String(100), index=True, nullable=False)
    clause_title = Column(String(255), nullable=False)
    requirement_summary = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    risk_level = Column(String(50), nullable=False)
    evidence_found = Column(Text, nullable=True)
    gap_analysis = Column(Text, nullable=True)
    remediation_recommendation = Column(Text, nullable=True)
    citations_json = Column(Text, nullable=True)

    audit_run = relationship("AuditRunModel", back_populates="findings")
