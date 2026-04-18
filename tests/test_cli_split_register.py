"""Smoke-test that register_split_parser wires up correctly."""
import argparse
from csv_surgeon.cli_split import register_split_parser


def test_register_split_by_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_split_parser(sub)
    args = parser.parse_args(["split-by", "data.csv", "--column", "dept"])
    assert args.column == "dept"
    assert args.input == "data.csv"
    assert args.func.__name__ == "cmd_split_by"


def test_register_split_chunk_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_split_parser(sub)
    args = parser.parse_args(["split-chunk", "data.csv", "--size", "100"])
    assert args.size == 100
    assert args.func.__name__ == "cmd_split_chunk"


def test_split_by_default_outdir():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_split_parser(sub)
    args = parser.parse_args(["split-by", "data.csv", "--column", "x"])
    assert args.outdir == "."


def test_split_chunk_default_outdir():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_split_parser(sub)
    args = parser.parse_args(["split-chunk", "data.csv", "--size", "50"])
    assert args.outdir == "."
