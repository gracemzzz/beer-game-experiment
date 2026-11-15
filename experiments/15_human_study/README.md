# Human Beer Game study

**[Open the three-page PDF](HUMAN_STUDY_DESIGN.pdf)** | [Editable text](HUMAN_STUDY_DESIGN.md)

1. **Model and hypotheses:** the ordering model, its meaning and H1–H6.
2. **Measurements and regression:** stock weighting, performance outcomes and H5/H6 estimation.
3. **Experiment design:** the four groups, brief procedure and sample-size calculation.

This is a proposed human study. The completed AI data remain separate.

## Calculations and technical notes

[Planning notebook](notebooks/POWER_AND_MEASURES.ipynb) | [Full measurement equations](02_MEASUREMENT_MODEL.md) | [Sample-size assumptions](03_SAMPLE_SIZE.md) | [Detailed protocol](01_STUDY_DESIGN.md) | [Data specification](04_DATA_COLLECTION.md) | [References](05_LITERATURE.md)

## Update the report

Edit `HUMAN_STUDY_DESIGN.md`, then run from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/export_human_study_pdf.py
```

The PDF is generated directly from that text. Keep it to the three sections above. The replaced long report is preserved under `maintenance/human_report_history/`, outside the current study folder. No participant collection or API calls run during export.
