import pytest
import pandas as pd

from src.transform import validate_response, transform_records


# --- fixtures ---

def minimal_response():
    return [
        {
            "city": {
                "id": 5128581,
                "name": "New York",
                "country": "US",
                "population": 8175133,
                "timezone": -14400,
                "sunrise": 1778270000,
                "sunset": 1778320000,
                "coord": {"lat": 40.7128, "lon": -74.006},
            },
            "list": [
                {
                    "dt": 1778284800,
                    "dt_txt": "2026-05-09 00:00:00",
                    "main": {
                        "temp": 60.51,
                        "feels_like": 58.57,
                        "temp_min": 59.0,
                        "temp_max": 62.0,
                        "humidity": 49,
                        "pressure": 1015,
                    },
                    "wind": {"speed": 7.07, "deg": 200, "gust": 9.1},
                    "clouds": {"all": 20},
                    "visibility": 10000,
                    "pop": 0.2,
                    "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
                }
            ],
        }
    ]


# --- validate_response ---

class TestValidateResponse:
    def test_valid_input_passes(self):
        validate_response(minimal_response())

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="non-empty list"):
            validate_response([])

    def test_not_a_list_raises(self):
        with pytest.raises(ValueError, match="non-empty list"):
            validate_response("not a list")

    def test_missing_list_key_raises(self):
        data = [{"city": {"id": 1, "name": "X"}}]
        with pytest.raises(ValueError, match="missing required 'list' field"):
            validate_response(data)

    def test_empty_list_field_raises(self):
        data = [{"city": {"id": 1}, "list": []}]
        with pytest.raises(ValueError, match="missing required 'list' field"):
            validate_response(data)

    def test_missing_city_key_raises(self):
        data = [{"list": [{"dt": 1}]}]
        with pytest.raises(ValueError, match="missing required 'city' field"):
            validate_response(data)

    def test_item_not_dict_raises(self):
        with pytest.raises(ValueError, match="must be a dict"):
            validate_response(["not a dict"])


# --- transform_records ---

class TestTransformRecords:
    def test_returns_dataframe(self):
        result = transform_records(minimal_response())
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns_present(self):
        result = transform_records(minimal_response())
        for col in ["city_name", "city_country", "main_temp", "weather_main"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_row_count_matches_forecast_entries(self):
        result = transform_records(minimal_response())
        assert len(result) == 1

    def test_city_metadata_broadcast_to_all_rows(self):
        data = minimal_response()
        data[0]["list"].append({**data[0]["list"][0], "dt": 9999999, "dt_txt": "2026-05-09 03:00:00"})
        result = transform_records(data)
        assert len(result) == 2
        assert (result["city_name"] == "New York").all()

    def test_invalid_dt_txt_rows_dropped(self):
        data = minimal_response()
        data[0]["list"].append({**data[0]["list"][0], "dt": 9999, "dt_txt": "not-a-date"})
        result = transform_records(data)
        assert len(result) == 1

    def test_weather_column_flattened(self):
        result = transform_records(minimal_response())
        assert "weather_main" in result.columns
        assert "weather" not in result.columns
