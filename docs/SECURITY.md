# PDF NEXUS — Security & Privacy Policy

## 1. Document Privacy & Processing
- **No Third-Party Uploads by Default**: Core PDF text editing, redaction, and conversions execute locally on the PDF NEXUS engine without uploading private documents to external SaaS services.
- **True Redaction**: The redaction engine physically removes the underlying text objects from the PDF vector stream. No hidden text, metadata tags, or searchable ghost text remain.
- **Isolated Untrusted Execution**: Embedded PDF JavaScript is disabled during processing to prevent code execution vulnerabilities.

---

## 2. API & Storage Security
- **Magic Byte Validation**: Uploaded documents are verified by inspecting binary headers (e.g. `%PDF-` signature), preventing disguised executable files from being uploaded.
- **Path Traversal Protection**: All file resolution is guarded by `safe_resolve_path` to guarantee that file access remains strictly quarantined inside authorized upload/export roots.
- **File Size Limits**: Hard limits of 50MB per document protect against resource exhaustion attacks.
- **Modern Authentication**: Passwords hashed with `bcrypt` (adaptive work factor). Stateless tokens signed with HMAC-SHA256 (`HS256`).
- **CORS Control**: Strict CORS policies prevent cross-origin scripting attacks.
