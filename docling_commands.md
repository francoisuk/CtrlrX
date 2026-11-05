# Running Docling — Reference

## Prerequisites

- **Python 3.10** at `C:\Users\Superdad\AppData\Local\Python310\python.exe`
- **Tesseract** installed at `C:\Program Files\Tesseract-OCR\`
- **tessdata files** copied to `C:\Temp\tessdata\` (eng, fra, osd)
- **Docling** installed in Python 3.10 (version 2.138.0)
- **Pinned dependencies**: transformers 4.56.2, huggingface_hub 0.36.2, numpy 1.26.4

## Environment Variable

Always set this before running Docling in a PowerShell session:

```powershell
$env:TESSDATA_PREFIX = "C:\Temp\tessdata\"
```

This must be set in **every new terminal** unless you add it to your system environment variables permanently.

## Single File — CLI

```powershell
C:\Users\Superdad\AppData\Local\Python310\python.exe -m docling "C:\Path\To\File.pdf" --ocr --force-ocr --ocr-engine tesseract --output "C:\Temp\Output"
```

**Note**: The output folder must exist before running, or Docling falls back to the current directory.

Create it first:

```powershell
mkdir "C:\Temp\Output" -Force
```

## Batch Processing — Python Script

Save as `C:\Temp\batch_convert.py`:

```python
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

ocr_options = TesseractOcrOptions(lang=["eng", "fra"], force_full_page_ocr=True)

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = ocr_options
pipeline_options.do_table_structure = True

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

input_dir = Path(r"C:\Temp\InputPDFs")
output_dir = Path(r"C:\Temp\ConvertedMD")
output_dir.mkdir(parents=True, exist_ok=True)

pdf_files = list(input_dir.glob("*.pdf"))
print(f"Found {len(pdf_files)} PDFs")

for pdf in pdf_files:
    print(f"Processing: {pdf.name}")
    try:
        result = converter.convert(str(pdf))
        output_path = output_dir / f"{pdf.stem}.md"
        result.document.save_as_markdown(output_path, image_mode="placeholder")
        print(f"  -> Saved: {output_path.name}")
    except Exception as e:
        print(f"  -> FAILED: {e}")
```

Run it:

```powershell
$env:TESSDATA_PREFIX = "C:\Temp\tessdata\"
C:\Users\Superdad\AppData\Local\Python310\python.exe C:\Temp\batch_convert.py
```

## Key Points

| Item             | Value                                                  |
| ---------------- | ------------------------------------------------------ |
| Python path      | `C:\Users\Superdad\AppData\Local\Python310\python.exe` |
| Tesseract binary | `C:\Program Files\Tesseract-OCR\tesseract.exe`         |
| tessdata folder  | `C:\Temp\tessdata\`                                    |
| TESSDATA_PREFIX  | `C:\Temp\tessdata\` (trailing backslash)               |
| Languages        | `eng`, `fra`                                           |
| OCR engine       | `tesseract` (or `easyocr`)                             |

## Common Warnings (Ignore These)

- `OSD failed for doc...` — orientation detection can't run, OCR proceeds anyway
- `Error in boxClipToRectangle: box outside rectangle` — cosmetic Tesseract bug
- `Error in pixScanForForeground: invalid box` — cosmetic Tesseract bug
- `Using a slow image processor...` — informational, no impact
- HuggingFace symlink warning — harmless, cached files work fine

## Troubleshooting

| Problem                     | Fix                                    |
| --------------------------- | -------------------------------------- |
| `tesseract not recognized`  | Use full path or set PATH              |
| `tesserocr not installed`   | Already installed via wheel            |
| `WinError 1314`             | Enable Developer Mode                  |
| `rt_detr_v2 not recognized` | transformers must be 4.56.2            |
| Output folder empty         | Create folder before running           |
| Output in wrong location    | Run from a simple path, not `system32` |

## Verifying the Setup

```powershell
C:\Users\Superdad\AppData\Local\Python310\python.exe -c "import transformers, huggingface_hub, numpy, tesserocr; print('transformers:', transformers.__version__); print('huggingface_hub:', huggingface_hub.__version__); print('numpy:', numpy.__version__); print('tesserocr:', tesserocr.tesseract_version())"
```

Expected:

- transformers: 4.56.2
- huggingface_hub: 0.36.2
- numpy: 1.26.4
- tesserocr: tesseract 5.5.3

## Output

Markdown files appear in the output folder. Each PDF produces one `.md` file with the same base name. Images are represented as placeholders (`!image`) rather than embedded base64.

Upload these `.md` files directly to your Open WebUI knowledge base.