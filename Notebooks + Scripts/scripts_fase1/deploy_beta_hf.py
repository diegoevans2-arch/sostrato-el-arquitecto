"""Publica la beta de Sóstrato (renuevo_ui + las dos paletas) en un Space estático PÚBLICO de Hugging Face (demo de portafolio, datos anonimizados).

Uso, con el Python de Anaconda (es el que tiene huggingface_hub y el login de ORG):
    python deploy_beta_hf.py --dry-run      arma el paquete y revisa sus referencias, sin subir
    python deploy_beta_hf.py                sube a diegoevans2-arch/sostrato-el-arquitecto

No toca las carpetas de origen: las copia a un temporal, sin maquetas_visualizacion/datos,
porque las vistas llevan sus datos dentro. En esta red la subida por Xet se cuelga, por eso va desactivada.
La portada va en la raíz del Space: HF sirve solo la carpeta de app_file, y con ella en renuevo_ui/ lo demás da 404.
"""
import argparse
import os
import pathlib
import re
import shutil
import tempfile

os.environ["HF_HUB_DISABLE_XET"] = "1"
from huggingface_hub import HfApi  # noqa: E402

DOC = pathlib.Path(__file__).resolve().parents[2] / "Documentación"
MAQUETAS = ["maquetas_visualizacion_arena", "maquetas_visualizacion"]
CAMPUS = ["C01", "C02", "C03", "C04", "C05", "C06", "C07"]
README = """---
title: Sóstrato el Arquitecto
emoji: 🏛️
colorFrom: yellow
colorTo: red
sdk: static
app_file: index.html
pinned: false
short_description: Proyección de ocupación de salas 2027–2031
---

Demo de portafolio: ocupación proyectada de salas y laboratorios 2027–2031 (Monte Carlo + predicción conforme).
Datos anonimizados: institución, campus, edificios y materias renombrados; geometría 3D rotada.
Código: https://github.com/diegoevans2-arch/sostrato-el-arquitecto · Autor: Diego Evans Pérez Paz.
"""


def armar(destino):
    for f in (DOC / "renuevo_ui").iterdir():
        shutil.copy2(f, destino / f.name)
    for c in MAQUETAS:
        shutil.copytree(DOC / c, destino / c, ignore=shutil.ignore_patterns("datos", "__pycache__"))
    (destino / "README.md").write_text(README, encoding="utf-8", newline="\n")
    pagina = destino / "index.html"
    t = pagina.read_text(encoding="utf-8")
    assert t.count("../maquetas_visualizacion") == 1 and t.count("../${carpeta}/") == 1
    t = t.replace("../maquetas_visualizacion", "maquetas_visualizacion").replace("../${carpeta}/", "${carpeta}/")
    pagina.write_text(t, encoding="utf-8", newline="")


def revisar(destino):
    faltan = []
    for p in MAQUETAS:
        faltan += [f"{p}/DEMO_SOSTRATO.html"] if not (destino / p / "DEMO_SOSTRATO.html").exists() else []
        faltan += [f"{p}/A4_campus_3d_proyectado_{c}.html" for c in CAMPUS if not (destino / p / f"A4_campus_3d_proyectado_{c}.html").exists()]
    faltan += [f"salas_{c}.js" for c in CAMPUS if not (destino / f"salas_{c}.js").exists()]
    faltan += [m for m in re.findall(r'src="([^"?]+\.js)', (destino / "index.html").read_text(encoding="utf-8")) if not (destino / m).exists()]
    archivos = [f for f in destino.rglob("*") if f.is_file()]
    print(len(archivos), "archivos,", sum(f.stat().st_size for f in archivos) // 2**20, "MB; mayor:", max(f.stat().st_size for f in archivos) // 2**20, "MB")
    if faltan:
        raise SystemExit(f"Faltan: {faltan}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="diegoevans2-arch/sostrato-el-arquitecto")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--salida", help="con --dry-run, deja el paquete en esta carpeta para probarlo en local")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        destino = pathlib.Path(tmp)
        armar(destino)
        revisar(destino)
        if args.dry_run:
            if args.salida:
                shutil.copytree(destino, args.salida, dirs_exist_ok=True)
            print("Paquete correcto; no se subió nada.")
            return
        api = HfApi(token=os.environ.get("HF_TOKEN"))
        api.create_repo(args.repo, repo_type="space", space_sdk="static", private=False, exist_ok=True)
        assert not api.repo_info(args.repo, repo_type="space").private, "El Space quedó privado"
        api.upload_folder(repo_id=args.repo, repo_type="space", folder_path=destino, commit_message="Demo de Sóstrato (datos anonimizados)", delete_patterns=["renuevo_ui/*"])
        print("Publicado: https://huggingface.co/spaces/" + args.repo)


if __name__ == "__main__":
    main()
