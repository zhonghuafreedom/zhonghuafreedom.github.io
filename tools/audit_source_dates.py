#!/usr/bin/env python3
"""Offline, read-only DOM/ledger audit for all 54 dossiers' source dates."""

from __future__ import annotations

import csv
from pathlib import Path

from check_languages import (
    SOURCE_DATE_LEDGER_PATH,
    loaded_documents,
    source_date_audit_statistics,
    source_date_ledger_issues,
)

BATCH12_SOURCE_DATE_CORRECTIONS_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "batch12-source-date-corrections.tsv"
)


def main() -> int:
    documents = loaded_documents()
    issues = source_date_ledger_issues(documents, require_file=True)
    stats = source_date_audit_statistics(documents)
    print(f"unique_sources={stats['unique_sources']}")
    print(f"blank_dates={stats['blank_dates']}")
    print(f"attr_visible_conflicts={stats['attr_visible_conflicts']}")
    print(f"datetime_visible_conflicts={stats['datetime_visible_conflicts']}")
    print(f"ten_language_source_inconsistencies={stats['cross_language_inconsistencies']}")
    print(f"suspicious_fabricated_01_01={stats['suspicious_01_01']}")
    with SOURCE_DATE_LEDGER_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    undated = [row for row in rows if row["verification_status"] == "UNDATED_CONFIRMED"]
    manual = [row for row in rows if row["verification_status"] == "MANUAL_REVIEW_REQUIRED"]
    if not BATCH12_SOURCE_DATE_CORRECTIONS_PATH.exists():
        issues.append(
            "batch12 source-date correction ledger is missing: "
            f"{BATCH12_SOURCE_DATE_CORRECTIONS_PATH}"
        )
        corrections = []
    else:
        with BATCH12_SOURCE_DATE_CORRECTIONS_PATH.open(
            encoding="utf-8", newline=""
        ) as handle:
            corrections = list(csv.DictReader(handle, delimiter="\t"))
        expected_correction = {
            "batch_tag": "reread:batch12",
            "slug": "transnational-repression",
            "source_id": "s1",
            "old_url": "https://freedomhouse.org/report/transnational-repression",
            "old_audited_date": "2021-01-15",
            "old_verification_status": "VERIFIED_SOURCE_DATE",
            "new_url": (
                "https://freedomhouse.org/article/"
                "new-report-transnational-repression-growing-threat-global-democracy"
            ),
            "new_audited_date": "2021-02-04",
            "new_verification_status": "CORRECTED_VERIFIED_SOURCE_DATE",
            "supersedes": (
                "source-date-ledger.tsv:transnational-repression:s1"
            ),
        }
        if len(corrections) != 1:
            issues.append(
                "batch12 source-date correction ledger must contain exactly "
                f"one data row, found {len(corrections)}"
            )
        elif any(
            corrections[0].get(field, "") != value
            for field, value in expected_correction.items()
        ):
            issues.append(
                "batch12 transnational-repression/s1 source-date correction "
                "does not match the independently fixed old/new contract"
            )
    print(f"undated_confirmed={len(undated)}")
    for row in undated:
        print(f"UNDATED\t{row['slug']}\t{row['source_id']}\t{row['url']}")
    print(f"manual_review_required={len(manual)}")
    for row in manual:
        print(f"MANUAL_REVIEW_REQUIRED\t{row['slug']}\t{row['source_id']}\t{row['url']}\t{row['note']}")
    print(f"batch12_source_date_corrections={len(corrections)}")
    for row in corrections:
        print(
            "CORRECTED_SOURCE_DATE\t"
            f"{row.get('slug', '')}\t{row.get('source_id', '')}\t"
            f"{row.get('old_audited_date', '')}\t"
            f"{row.get('new_audited_date', '')}\t"
            f"{row.get('new_url', '')}"
        )
    if issues:
        print("Source-date audit failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Source-date audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
