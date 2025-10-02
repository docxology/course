# Module: integration.export

**File:** `src/curriculum/integration/export.py`

## Description

Export service for generating various output formats.

## Classes

### `ExportService`

Service for exporting content in various formats.

**Methods:** 15


**Method List:**

- `__init__`: Initialize export service.

- `export_content`: Export content in specified format.

- `export_course`: Export entire course in specified format.

- `_export_scorm_package`: Export course as SCORM package.

- `_export_pdf_book`: Export course as PDF book.

- `_export_epub_book`: Export course as EPUB book.

- `export_user_progress`: Export user progress report.

- `export_assessment_results`: Export assessment results.

- `generate_certificate`: Generate course completion certificate.

- `export_analytics_report`: Export analytics report.

- `batch_export`: Export multiple content items.

- `get_supported_formats`: Get list of supported export formats.

- `validate_export_options`: Validate export options for format.

- `estimate_export_size`: Estimate file size for export.

- `_format_bytes`: Format bytes to human readable format.
