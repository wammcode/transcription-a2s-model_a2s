
import os
import subprocess
import argparse
import csv
import math
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **_kwargs):
        return iterable

try:
    import pandas as pd
except ImportError:
    pd = None


dataset = 'saxophone'
model = 'transformer'

# --- Parametros --- archivos xml
ESTIMATED_DIR =    os.path.abspath(f'metrics/amt/saxophone/musicxml')
GROUND_TRUTH_DIR = os.path.abspath(f'metrics/amt/target/musicxml')

# --- Configuration ---
MUSTER_EVAL_SCRIPT = os.path.abspath('MUSTER_v220127/MUSTER/evaluate_XML_voicePlus.sh')
OUTPUT_DIR = os.path.join(ESTIMATED_DIR, 'evaluation_results_muster')
EXCEL_OUTPUT_FILE = ESTIMATED_DIR + "_MUSTER_evaluation.xlsx"
FAILED_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "failed_files_muster.csv")
SUPPORTED_XML_EXTENSIONS = {'.musicxml', '.xml'}
DEFAULT_WORKERS = max(1, min(4, os.cpu_count() or 1))

# --- Metric Headers (from README) ---
METRIC_NAMES = [
    "pitch error rate (%)",
    "missing note rate (%)",
    "extra note rate (%)",
    "onset time error rate (%)",
    "offset time error rate (%)",
    "mean of (1) to (5)",
    "voice error rate (%)",
    "mean of (1) to (5) and (7)",
    "voice precision (%)",
    "voice recall (%)",
    "voice F measure (%)",
    "note value scale error",
    "hand error rate (%)"
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run MUSTER evaluation over matching MusicXML files."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=get_default_workers(),
        help=f"Number of files to evaluate in parallel. Default: {DEFAULT_WORKERS}",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of matching files to process.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse existing per-file MUSTER result .txt files when available.",
    )
    parser.add_argument(
        "--verbose-errors",
        action="store_true",
        help="Print full stdout/stderr for failed files.",
    )
    return parser.parse_args()


def get_default_workers():
    workers = os.environ.get("MUSTER_WORKERS")
    if workers is None:
        return DEFAULT_WORKERS

    try:
        return max(1, int(workers))
    except ValueError:
        return DEFAULT_WORKERS


def print_banner():
    print("##########################################")
    print(f"########## {model} - {dataset} ##########")
    print("##########################################")


def find_musicxml_files(directory):
    files = {}
    for path in Path(directory).iterdir():
        if path.is_file() and path.suffix.lower() in SUPPORTED_XML_EXTENSIONS:
            files[path.stem] = path
    return files


def safe_temp_prefix(file_prefix):
    valid_chars = []
    for char in file_prefix:
        if char.isalnum() or char in {"-", "_", "."}:
            valid_chars.append(char)
        else:
            valid_chars.append("_")
    return "".join(valid_chars)[:80] or "muster"


def create_xml_alias(source_path, alias_path):
    try:
        alias_path.symlink_to(source_path)
    except OSError:
        shutil.copy2(source_path, alias_path)


def parse_metrics_file(output_txt_file):
    with open(output_txt_file, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                values_part = line.split(":", 1)[1] if ":" in line else line
                return values_part.split()
    raise ValueError(f"Result file is empty: {output_txt_file}")


def parse_metric_value(value):
    if value is None or str(value).strip().lower() in {"", "none", "null", "nan", "n/a", "na"}:
        return 0

    try:
        parsed_value = float(value)
    except ValueError:
        return value

    return 0 if math.isnan(parsed_value) else parsed_value


def tail_text(value, max_lines=8):
    lines = [line for line in value.strip().splitlines() if line.strip()]
    return "\n".join(lines[-max_lines:])


class EvaluationError(Exception):
    def __init__(self, file_prefix, message, returncode=None, stdout="", stderr="", command=None):
        super().__init__(message)
        self.file_prefix = file_prefix
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command or []


def write_results(all_results):
    cols = ['File'] + METRIC_NAMES

    if pd is not None:
        try:
            df = pd.DataFrame(all_results)
            df = df[cols].fillna(0)
            df.to_excel(EXCEL_OUTPUT_FILE, index=False)
            print(f"\nEvaluation complete. Results saved to '{EXCEL_OUTPUT_FILE}'")
            return
        except Exception as e:
            print(f"Failed to write to Excel file: {e}")

    csv_output_file = os.path.splitext(EXCEL_OUTPUT_FILE)[0] + ".csv"
    try:
        with open(csv_output_file, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=cols)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nEvaluation complete. Results saved to '{csv_output_file}'")
        print("Install pandas and openpyxl if you need .xlsx output.")
    except Exception as e:
        print(f"Failed to write results file: {e}")


def write_failed_results(failed_results):
    if not failed_results:
        return

    cols = ["File", "Return Code", "Message", "Command", "Stdout Tail", "Stderr Tail"]
    try:
        with open(FAILED_OUTPUT_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=cols)
            writer.writeheader()
            writer.writerows(failed_results)
        print(f"Failed-file details saved to '{FAILED_OUTPUT_FILE}'")
    except Exception as e:
        print(f"Failed to write failed-file log: {e}")


def build_file_results(file_prefix, metrics_values):
    if len(metrics_values) < len(METRIC_NAMES):
        raise ValueError(
            f"Expected {len(METRIC_NAMES)} metrics, got {len(metrics_values)}."
        )

    file_results = {"File": file_prefix}
    for index, name in enumerate(METRIC_NAMES):
        file_results[name] = parse_metric_value(metrics_values[index])
    return file_results


def read_existing_result(file_prefix):
    output_path_prefix = Path(OUTPUT_DIR) / f"{file_prefix}_results"
    output_txt_file = Path(f"{output_path_prefix}.txt")
    if not output_txt_file.is_file():
        return None

    try:
        return build_file_results(file_prefix, parse_metrics_file(output_txt_file))
    except ValueError:
        return None


def evaluate_one_file(file_prefix, gt_source_path, est_source_path, tmp_root, resume=False):
    output_path_prefix = Path(OUTPUT_DIR) / f"{file_prefix}_results"
    output_txt_file = Path(f"{output_path_prefix}.txt")

    if resume:
        existing_result = read_existing_result(file_prefix)
        if existing_result is not None:
            return existing_result

    with tempfile.TemporaryDirectory(
        prefix=f"{safe_temp_prefix(file_prefix)}_",
        dir=tmp_root,
    ) as temp_dir:
        temp_dir = Path(temp_dir)
        gt_path_prefix = temp_dir / "ground_truth"
        est_path_prefix = temp_dir / "estimated"

        create_xml_alias(gt_source_path, gt_path_prefix.with_suffix(".xml"))
        create_xml_alias(est_source_path, est_path_prefix.with_suffix(".xml"))

        command = [
            "bash",
            MUSTER_EVAL_SCRIPT,
            str(gt_path_prefix),
            str(est_path_prefix),
            str(output_path_prefix),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(MUSTER_EVAL_SCRIPT),
        )

    try:
        metrics_values = parse_metrics_file(output_txt_file)
    except Exception as e:
        raise EvaluationError(
            file_prefix,
            str(e),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        ) from e

    if result.returncode != 0:
        raise EvaluationError(
            file_prefix,
            "MUSTER returned a non-zero exit code.",
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        )

    try:
        return build_file_results(file_prefix, metrics_values)
    except ValueError as e:
        raise EvaluationError(
            file_prefix,
            str(e),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            command=command,
        ) from e


def run_evaluation(workers=DEFAULT_WORKERS, limit=None, resume=False, verbose_errors=False):
    """
    Runs the MUSTER evaluation script for all corresponding files
    and stores the results in an Excel file.
    """
    workers = max(1, workers)
    print_banner()

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get list of file prefixes (e.g., "C-Jam-Blues")
    try:
        gt_files = find_musicxml_files(GROUND_TRUTH_DIR)
        est_files = find_musicxml_files(ESTIMATED_DIR)
    except FileNotFoundError as e:
        print(f"Error: Directory not found - {e.filename}")
        print("Please ensure the script is run from the 'Experimentos 2026 TMP' directory.")
        return

    files_to_process = sorted(gt_files.keys() & est_files.keys())
    if limit is not None:
        files_to_process = files_to_process[:limit]

    if not files_to_process:
        print("No matching .musicxml/.xml files found in both directories.")
        return

    if not os.path.isfile(MUSTER_EVAL_SCRIPT):
        print(f"Error: '{MUSTER_EVAL_SCRIPT}' not found.")
        print("Please ensure the path to the evaluation script is correct.")
        return

    print(f"Found {len(files_to_process)} matching files to process.")
    print(f"Running with {workers} parallel worker(s).")

    all_results = [None] * len(files_to_process)
    failed_results = []
    tmp_root = os.path.join(OUTPUT_DIR, "_tmp_parallel")
    os.makedirs(tmp_root, exist_ok=True)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_file = {}
        for index, file_prefix in enumerate(files_to_process):
            future = executor.submit(
                evaluate_one_file,
                file_prefix,
                gt_files[file_prefix],
                est_files[file_prefix],
                tmp_root,
                resume,
            )
            future_to_file[future] = (index, file_prefix)

        for future in tqdm(
            as_completed(future_to_file),
            total=len(future_to_file),
            desc="Processing files",
            unit="file",
        ):
            index, file_prefix = future_to_file[future]
            try:
                all_results[index] = future.result()
            except EvaluationError as e:
                failed_results.append(
                    {
                        "File": e.file_prefix,
                        "Return Code": e.returncode,
                        "Message": str(e),
                        "Command": " ".join(e.command),
                        "Stdout Tail": tail_text(e.stdout),
                        "Stderr Tail": tail_text(e.stderr),
                    }
                )
                print(f"\nFailed {file_prefix}: {e}")
                if verbose_errors:
                    print(f"Command: {' '.join(e.command)}")
                    print(f"Return Code: {e.returncode}")
                    print(f"Output:\n{e.stdout}")
                    print(f"Error Output:\n{e.stderr}")
            except Exception as e:
                failed_results.append(
                    {
                        "File": file_prefix,
                        "Return Code": None,
                        "Message": str(e),
                        "Command": "",
                        "Stdout Tail": "",
                        "Stderr Tail": "",
                    }
                )
                print(f"\nAn unexpected error occurred for {file_prefix}: {e}")

    try:
        os.rmdir(tmp_root)
    except OSError:
        pass

    all_results = [result for result in all_results if result is not None]

    if not all_results:
        print("No results were generated. Please check the logs for errors.")
        return

    write_results(all_results)
    if failed_results:
        print(f"{len(failed_results)} file(s) failed. See logs above for details.")
        write_failed_results(failed_results)


if __name__ == "__main__":
    args = parse_args()
    run_evaluation(
        workers=args.workers,
        limit=args.limit,
        resume=args.resume,
        verbose_errors=args.verbose_errors,
    )
