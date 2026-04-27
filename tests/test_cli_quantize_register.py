"""Ensure register_quantize_parser wires up the sub-command correctly."""
import argparse
from csv_surgeon.cli_quantize import register_quantize_parser, cmd_quantize


def _make_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    register_quantize_parser(sub)
    return root


def test_register_creates_quantize_subcommand():
    p = _make_parser()
    ns = p.parse_args(["quantize", "data.csv", "--column", "score", "--bins", "4"])
    assert ns.command == "quantize"
    assert ns.column == "score"
    assert ns.bins == 4


def test_register_sets_func():
    p = _make_parser()
    ns = p.parse_args(["quantize", "data.csv", "--column", "v"])
    assert ns.func is cmd_quantize


def test_default_edges_is_empty_string():
    p = _make_parser()
    ns = p.parse_args(["quantize", "data.csv", "--column", "v"])
    assert ns.edges == ""


def test_default_labels_is_empty_string():
    p = _make_parser()
    ns = p.parse_args(["quantize", "data.csv", "--column", "v"])
    assert ns.labels == ""


def test_inplace_flag_defaults_false():
    p = _make_parser()
    ns = p.parse_args(["quantize", "data.csv", "--column", "v"])
    assert ns.inplace is False


def test_inplace_flag_can_be_set():
    p = _make_parser()
    ns = p.parse_args(["quantize", "data.csv", "--column", "v", "--inplace"])
    assert ns.inplace is True
