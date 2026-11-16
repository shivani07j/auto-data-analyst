import argparse

from . import __version__
from .load import load_raw
from .pipeline import run_pipeline, save_clean, write_log, LOG_PATH


def build_parser():
    parser = argparse.ArgumentParser(
        prog="autoanalyst",
        description="Clean a CSV file and write the clean data and a cleaning log.",
    )
    parser.add_argument("csv", help="path to the CSV file to clean")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    raw = load_raw(args.csv)
    clean, log = run_pipeline(raw)
    saved = save_clean(clean)
    write_log(raw, clean, log)

    print("Raw shape:  ", raw.shape)
    print("Clean shape:", clean.shape)
    print("Saved:", ", ".join(saved))
    print("Log written to", LOG_PATH)