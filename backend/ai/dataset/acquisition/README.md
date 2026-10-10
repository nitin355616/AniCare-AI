# AniCare AI — Dataset Acquisition & Verification Log

This directory documents the provenance verification, external audit results, and ingestion manifests for animal health image datasets used in AniCare AI.

## Governance Standards

1. **Independent Verification**: No dataset is downloaded without resolving its official DOI, publisher metadata, author identity, and license terms.
2. **Zero Web-Scraping**: Datasets scraped from web search engines or unverified social media platforms are strictly banned.
3. **Quarantine by Default**: If an entry in `source_registry.json` fails live verification, its status is immediately changed to `REVIEW_REQUIRED` and downloading is withheld.
4. **License Integrity**: Only datasets with explicit permissive licenses (e.g. `CC-BY-4.0`) that allow research and distribution are eligible for processing.

## Files

- `acquisition_manifest.json`: Machine-readable audit status for each candidate dataset.
- `source_verification_report.md`: Detailed audit findings with live URLs, authors, and restriction analyses.
