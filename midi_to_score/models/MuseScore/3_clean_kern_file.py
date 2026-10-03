#!/usr/bin/env python3
"""CLI para limpiar archivos Humdrum .krn."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional

RESERVED_WORDS = ("clef", "k[", "*M")
RESERVED_DOT = "."
RESERVED_DOT_ENCODED_CHARACTER = "."
CLEF_CHANGE_OTHER_VOICES = "*"
COMMENT_SYMBOLS = ("*", "!")
SPINE_PATH_TOKENS = {"*^", "*v", "*x", "*+", "*-"}


def _read_src_file(text: str) -> List[List[str]]:
    """Adecuar el contenido .krn al formato base para limpiar tokens."""
    if not text.strip():
        return []

    lines = text.splitlines()

    header_found = False
    lines_no_comments: List[List[str]] = []
    for line in lines:
        if "**kern" in line:
            header_found = True
        if line.strip().startswith("!"):
            continue
        lines_no_comments.append(line.split("\t"))

    if not header_found:
        raise ValueError("No se encontro ninguna cabecera '**kern' en el archivo.")
    if not lines_no_comments:
        return []

    return lines_no_comments


def clean_kern_token(in_token: str) -> Optional[str]:
    """Convertir un token kern a su version CLEAN."""
    out_token = None

    if any(reserved_word in in_token for reserved_word in RESERVED_WORDS):
        out_token = in_token
    elif in_token == RESERVED_DOT:
        out_token = RESERVED_DOT_ENCODED_CHARACTER
    elif in_token.strip() in SPINE_PATH_TOKENS:
        out_token = in_token.strip()
    elif in_token.strip() == CLEF_CHANGE_OTHER_VOICES:
        out_token = in_token
    elif any(in_token.startswith(comment_symbol) for comment_symbol in COMMENT_SYMBOLS):
        out_token = None
    elif in_token.startswith("s"):
        out_token = "s"
    elif "=" in in_token:
        out_token = "="
    elif "q" not in in_token:
        if "rr" in in_token:
            match = re.search(r"rr[0-9]+", in_token)
            if match:
                out_token = match.group(0)
        elif "r" in in_token:
            out_token = in_token.split("r")[0] + "r"
        else:
            match = re.search(r"\[*\d+[.]*[a-gA-G]+[n#-]*\]*", in_token)
            if match:
                out_token = match.group(0)

    return out_token


def _postprocess_kern_rows(cleaned_rows: List[List[str]]) -> List[List[str]]:
    """Reemplazar '*' por la ultima clave explicita vista en su columna."""
    if not cleaned_rows:
        return cleaned_rows

    out_rows: List[List[str]] = []
    last_clef_by_column: dict[int, str] = {}

    for row in cleaned_rows:
        new_row = list(row)
        for col_idx, token in enumerate(new_row):
            if token == CLEF_CHANGE_OTHER_VOICES and col_idx in last_clef_by_column:
                new_row[col_idx] = last_clef_by_column[col_idx]
        for col_idx, token in enumerate(new_row):
            if token.startswith("*clef"):
                last_clef_by_column[col_idx] = token
        out_rows.append(new_row)

    return out_rows


def clean_kern_file(text: str) -> List[List[str]]:
    """Convertir una partitura kern completa al formato CLEAN, preservando voces por fila."""
    input_rows = _read_src_file(text=text)
    if not input_rows:
        return []

    cleaned_rows: List[List[str]] = []
    for row in input_rows:
        cleaned_row = [clean_kern_token(token) for token in row]
        if all(token is None for token in cleaned_row):
            continue
        normalized_row = [
            token if token is not None else RESERVED_DOT_ENCODED_CHARACTER
            for token in cleaned_row
        ]
        cleaned_rows.append(normalized_row)

    return _postprocess_kern_rows(cleaned_rows)


def clean_kern_text(text: str) -> str:
    """Limpia el contenido de un archivo .krn y devuelve el nuevo texto."""
    cleaned_rows = clean_kern_file(text=text)
    if not cleaned_rows:
        return ""

    out_lines = ["\t".join(row) for row in cleaned_rows]
    return "\n".join(out_lines) + "\n"


def _assert_krn_extension(path: Path, arg_name: str) -> None:
    if path.suffix.lower() != ".krn":
        raise ValueError(f"{arg_name} debe tener extension .krn: {path}")


def _clean_single_file(in_path: Path, out_path: Path) -> None:
    _assert_krn_extension(in_path, "input_krn")
    _assert_krn_extension(out_path, "output_krn")

    if not in_path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {in_path}")
    if not in_path.is_file():
        raise IsADirectoryError(f"La ruta de entrada no es un archivo: {in_path}")

    raw_text = in_path.read_text(encoding="utf-8", errors="replace")
    cleaned_text = clean_kern_text(raw_text)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(cleaned_text, encoding="utf-8")


def _clean_directory(in_dir: Path, out_dir: Path, recursive: bool) -> tuple[int, int]:
    if not in_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta de entrada: {in_dir}")
    if not in_dir.is_dir():
        raise NotADirectoryError(f"La ruta de entrada no es una carpeta: {in_dir}")
    if out_dir.exists() and out_dir.is_file():
        raise FileExistsError(f"La salida debe ser una carpeta, no un archivo: {out_dir}")

    files = sorted(in_dir.rglob("*.krn") if recursive else in_dir.glob("*.krn"))
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos .krn en: {in_dir}")

    processed = 0
    skipped = 0
    skipped_details: list[str] = []

    for in_file in files:
        relative = in_file.relative_to(in_dir)
        if recursive:
            out_file = out_dir / relative
        else:
            out_file = out_dir / in_file.name
        try:
            _clean_single_file(in_file, out_file)
            processed += 1
        except Exception as exc:
            skipped += 1
            if len(skipped_details) < 10:
                skipped_details.append(f"{in_file.name}: {exc}")

    if skipped_details:
        print("Advertencia: algunos archivos se omitieron por error:")
        for detail in skipped_details:
            print(f"- {detail}")

    return processed, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Limpia archivos .krn. Soporta archivo->archivo, archivo->carpeta y "
            "carpeta->carpeta."
        )
    )
    parser.add_argument("input_path", type=Path, help="Ruta de entrada (archivo .krn o carpeta).")
    parser.add_argument("output_path", type=Path, help="Ruta de salida (archivo .krn o carpeta).")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="En modo carpeta, procesa .krn recursivamente y mantiene subcarpetas.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    in_path: Path = args.input_path
    out_path: Path = args.output_path
    recursive: bool = args.recursive

    try:
        if in_path.is_file():
            if out_path.exists() and out_path.is_dir():
                out_file = out_path / in_path.name
            else:
                out_file = out_path
            _clean_single_file(in_path, out_file)
            print(f"Archivo limpio guardado en: {out_file}")
            return 0

        if in_path.is_dir():
            processed, skipped = _clean_directory(in_path, out_path, recursive=recursive)
            print(f"Archivos limpios guardados en: {out_path}")
            print(f"Total procesados: {processed}")
            print(f"Total omitidos: {skipped}")
            return 0

        raise FileNotFoundError(f"La ruta de entrada no existe: {in_path}")
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
