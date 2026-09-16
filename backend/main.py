import pathlib
import shutil
import subprocess
import sys
import tempfile

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from yaml_builder import build_yaml

BACKEND_DIR = pathlib.Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
RENDERCV_BIN = str(pathlib.Path(sys.executable).parent / "rendercv")

app = FastAPI()


@app.post("/api/generate-cv")
async def generate_cv(request: Request):
    form = await request.json()

    if not (form.get("name") or "").strip():
        raise HTTPException(status_code=400, detail="姓名為必填欄位")
    if not (form.get("email") or "").strip():
        raise HTTPException(status_code=400, detail="Email 為必填欄位")

    yaml_data = build_yaml(form)

    tmp_dir = tempfile.mkdtemp(prefix="cvbuilder_")
    tmp_path = pathlib.Path(tmp_dir)
    yaml_path = tmp_path / "cv.yaml"
    pdf_path = tmp_path / "cv.pdf"

    try:
        yaml_path.write_text(
            yaml.safe_dump(yaml_data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                RENDERCV_BIN,
                "render",
                str(yaml_path),
                "--pdf-path",
                str(pdf_path),
                "-nomd",
                "-nopng",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0 or not pdf_path.exists():
            error_message = (result.stderr or result.stdout or "產生 PDF 失敗").strip()
            raise HTTPException(status_code=400, detail=error_message[-4000:])
    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    filename = f"{form['name'].strip().replace(' ', '_')}_CV.pdf"
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
        background=BackgroundTask(shutil.rmtree, tmp_dir, ignore_errors=True),
    )


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
