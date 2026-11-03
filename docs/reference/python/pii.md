# PII scanner

::: dpdpkit.pii.database
    options:
      members: [scan_database, DatabaseScan, ColumnFinding, ReadOnlyError]

::: dpdpkit.pii.files
    options:
      members: [scan_files, FileScan, FileFinding]

::: dpdpkit.pii.report
    options:
      members: [build_report, diff_registry, Report, ReportRow, RegistryDiff]

::: dpdpkit.pii.columns
    options:
      members: [classify_column, classify_columns, ColumnMatch]

::: dpdpkit.pii.recognizers.india_recognizers
