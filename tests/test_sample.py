"""Tests for csv_surgeon.sample."""
import pytest

from csv_surgeon.sample import sample_fraction, sample_rows, systematic_sample


@pytest.fixture()
def _rows():
    return [{"id": str(i), "val": str(i * 10)} for i in range(20)]


def test_sample_rows_count(_rows):
    result = sample_rows(_rows, 5, seed=0)
    assert len(result) == 5


def test_sample_rows_reproducible(_rows):
    a = sample_rows(_rows, 7, seed=42)
    b = sample_rows(_rows, 7, seed=42)
    assert a == b


def test_sample_rows_different_seeds(_rows):
    a = sample_rows(_rows, 7, seed=1)
    b = sample_rows(_rows, 7, seed=2)
    assert a != b


def test_sample_rows_n_larger_than_population(_rows):
    result = sample_rows(_rows, 100, seed=0)
    assert len(result) == len(_rows)


def test_sample_fraction_bounds(_rows):
    result = list(sample_fraction(_rows, 1.0))
    assert result == _rows


def test_sample_fraction_zero_raises(_rows):
    with pytest.raises(ValueError):
        list(sample_fraction(_rows, 0.0))


def test_sample_fraction_negative_raises(_rows):
    with pytest.raises(ValueError):
        list(sample_fraction(_rows, -0.1))


def test_sample_fraction_reproducible(_rows):
    a = list(sample_fraction(_rows, 0.5, seed=7))
    b = list(sample_fraction(_rows, 0.5, seed=7))
    assert a == b


def test_systematic_sample_step2(_rows):
    result = list(systematic_sample(_rows, step=2))
    assert result == _rows[::2]


def test_systematic_sample_with_offset(_rows):
    result = list(systematic_sample(_rows, step=3, offset=1))
    expected = [_rows[i] for i in range(1, 20, 3)]
    assert result == expected


def test_systematic_sample_step_zero_raises(_rows):
    with pytest.raises(ValueError):
        list(systematic_sample(_rows, step=0))
