import pytest
from csv_surgeon.shift import lag_column, lead_column


def _rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
    ]


# --- lag ---

def test_lag_default_fill():
    result = list(lag_column(iter(_rows()), "val"))
    assert result[0]["val_lag1"] == ""
    assert result[1]["val_lag1"] == "10"
    assert result[2]["val_lag1"] == "20"
    assert result[3]["val_lag1"] == "30"


def test_lag_periods_2():
    result = list(lag_column(iter(_rows()), "val", periods=2))
    assert result[0]["val_lag2"] == ""
    assert result[1]["val_lag2"] == ""
    assert result[2]["val_lag2"] == "10"
    assert result[3]["val_lag2"] == "20"


def test_lag_custom_fill():
    result = list(lag_column(iter(_rows()), "val", fill="NA"))
    assert result[0]["val_lag1"] == "NA"


def test_lag_custom_out_column():
    result = list(lag_column(iter(_rows()), "val", out_column="prev"))
    assert "prev" in result[0]
    assert result[1]["prev"] == "10"


def test_lag_invalid_periods():
    with pytest.raises(ValueError):
        list(lag_column(iter(_rows()), "val", periods=0))


def test_lag_preserves_other_columns():
    result = list(lag_column(iter(_rows()), "val"))
    assert result[2]["id"] == "3"


# --- lead ---

def test_lead_default_fill():
    result = list(lead_column(iter(_rows()), "val"))
    assert result[0]["val_lead1"] == "20"
    assert result[1]["val_lead1"] == "30"
    assert result[2]["val_lead1"] == "40"
    assert result[3]["val_lead1"] == ""


def test_lead_periods_2():
    result = list(lead_column(iter(_rows()), "val", periods=2))
    assert result[0]["val_lead2"] == "30"
    assert result[1]["val_lead2"] == "40"
    assert result[2]["val_lead2"] == ""
    assert result[3]["val_lead2"] == ""


def test_lead_custom_out_column():
    result = list(lead_column(iter(_rows()), "val", out_column="next_val"))
    assert "next_val" in result[0]


def test_lead_invalid_periods():
    with pytest.raises(ValueError):
        list(lead_column(iter(_rows()), "val", periods=0))


def test_lead_preserves_other_columns():
    result = list(lead_column(iter(_rows()), "val"))
    assert result[1]["id"] == "2"
