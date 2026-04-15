-- PostgreSQL schema for AI Invoice Image Processing System

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) RBAC
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  module VARCHAR(100) NOT NULL,
  action VARCHAR(50) NOT NULL,
  code VARCHAR(150) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE role_permissions (
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  role_id UUID NOT NULL REFERENCES roles(id),
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2) Invoice type metadata
CREATE TABLE invoice_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  prompt_ocr_id UUID,
  prompt_extract_id UUID,
  prompt_validate_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE invoice_type_fields (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_type_id UUID NOT NULL REFERENCES invoice_types(id) ON DELETE CASCADE,
  field_key VARCHAR(100) NOT NULL,
  field_label VARCHAR(120) NOT NULL,
  field_type VARCHAR(50) NOT NULL,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  is_header BOOLEAN NOT NULL DEFAULT TRUE,
  validation_rule JSONB NOT NULL DEFAULT '{}'::jsonb,
  display_order INT NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(invoice_type_id, field_key)
);

-- 3) File upload metadata
CREATE TABLE uploaded_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_file_name VARCHAR(255) NOT NULL,
  file_ext VARCHAR(10) NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  file_size BIGINT NOT NULL,
  file_hash_sha256 CHAR(64) NOT NULL,
  storage_provider VARCHAR(30) NOT NULL,
  storage_path TEXT NOT NULL,
  uploaded_by UUID NOT NULL REFERENCES users(id),
  batch_name VARCHAR(120),
  remarks TEXT,
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(file_hash_sha256)
);

-- 4) Invoice main
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  uploaded_file_id UUID NOT NULL REFERENCES uploaded_files(id),
  invoice_type_id UUID NOT NULL REFERENCES invoice_types(id),
  status VARCHAR(30) NOT NULL,
  assignment_status VARCHAR(20) NOT NULL DEFAULT 'UNASSIGNED',
  assigned_reviewer_id UUID REFERENCES users(id),
  uploaded_by UUID NOT NULL REFERENCES users(id),
  reviewed_by UUID REFERENCES users(id),

  invoice_no VARCHAR(120),
  vendor_name VARCHAR(255),
  invoice_date DATE,
  currency VARCHAR(10),
  total_amount NUMERIC(18,2),

  ocr_text TEXT,
  clarity_score NUMERIC(5,2),
  ai_confidence_score NUMERIC(5,2),
  required_fields_complete BOOLEAN,

  ai_provider VARCHAR(50),
  ai_model VARCHAR(100),
  ai_raw_json JSONB,
  final_json JSONB,
  validation_result JSONB,
  review_recommendation TEXT,

  version_no INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  approved_at TIMESTAMPTZ,
  rejected_at TIMESTAMPTZ
);

-- 5) Field values (AI vs Human)
CREATE TABLE invoice_field_values (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  invoice_type_field_id UUID NOT NULL REFERENCES invoice_type_fields(id),
  ai_value TEXT,
  ai_confidence NUMERIC(5,2),
  final_value TEXT,
  value_source VARCHAR(20) NOT NULL DEFAULT 'AI',
  modified_by UUID REFERENCES users(id),
  modified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(invoice_id, invoice_type_field_id)
);

-- 6) Line items
CREATE TABLE invoice_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  line_no INT,
  description TEXT,
  qty NUMERIC(18,4),
  unit_price NUMERIC(18,4),
  amount NUMERIC(18,2),
  currency VARCHAR(10),
  ai_confidence NUMERIC(5,2),
  final_source VARCHAR(20) NOT NULL DEFAULT 'AI',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7) System settings (AI key/model/prompt/currency)
CREATE TABLE system_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  setting_group VARCHAR(50) NOT NULL,
  setting_key VARCHAR(100) NOT NULL,
  setting_value JSONB NOT NULL,
  is_encrypted BOOLEAN NOT NULL DEFAULT FALSE,
  updated_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(setting_group, setting_key)
);

-- 8) Prompt templates
CREATE TABLE prompt_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_type VARCHAR(30) NOT NULL,
  name VARCHAR(120) NOT NULL,
  version INT NOT NULL,
  provider VARCHAR(50) NOT NULL,
  model VARCHAR(100) NOT NULL,
  template TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(prompt_type, name, version)
);

ALTER TABLE invoice_types
  ADD CONSTRAINT fk_prompt_ocr FOREIGN KEY (prompt_ocr_id) REFERENCES prompt_templates(id),
  ADD CONSTRAINT fk_prompt_extract FOREIGN KEY (prompt_extract_id) REFERENCES prompt_templates(id),
  ADD CONSTRAINT fk_prompt_validate FOREIGN KEY (prompt_validate_id) REFERENCES prompt_templates(id);

-- 9) Audit logs + revision history
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id UUID REFERENCES users(id),
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  action VARCHAR(50) NOT NULL,
  before_data JSONB,
  after_data JSONB,
  ip_address INET,
  user_agent TEXT,
  request_id VARCHAR(100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE invoice_revisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  field_key VARCHAR(100) NOT NULL,
  old_value TEXT,
  new_value TEXT,
  modified_by UUID NOT NULL REFERENCES users(id),
  modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index suggestions
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_uploaded_files_uploaded_by ON uploaded_files(uploaded_by);
CREATE INDEX idx_uploaded_files_batch_name ON uploaded_files(batch_name);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_assignment_status ON invoices(assignment_status);
CREATE INDEX idx_invoices_assigned_reviewer ON invoices(assigned_reviewer_id);
CREATE INDEX idx_invoices_uploaded_by ON invoices(uploaded_by);
CREATE INDEX idx_invoices_invoice_no ON invoices(invoice_no);
CREATE INDEX idx_invoices_vendor_name ON invoices(vendor_name);
CREATE INDEX idx_invoices_invoice_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_total_amount ON invoices(total_amount);
CREATE INDEX idx_invoices_created_at ON invoices(created_at);
CREATE INDEX idx_invoice_field_values_invoice_id ON invoice_field_values(invoice_id);
CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

