from datetime import date
from dm_reg_dataset_lola import dataset

test_data = {
    # Not expected in the population , out of age range
    1: {
        "patients": {"date_of_birth": date(2010, 1, 1)},
        "practice_registrations": [{"start_date": date(2014, 7, 10)}],
        "clinical_events": [{"date": date(2015, 5, 9), "snomedct_code": "111552007"}],
        "expected_in_population": False,
    },
    # Not expected in population , no diabetes diagnosis
    2: {
        "patients": {"date_of_birth": date(2010, 1, 1)},
        "practice_registrations": [{"start_date": date(2014, 7, 10)}],
        "clinical_events": [{"date": date(2015, 5, 9), "snomedct_code": "999999999"}],
        "expected_in_population": False,
    },
    # Expected in population with no resolved date
    3: {
        "patients": {"date_of_birth": date(2000, 1, 1)},
        "practice_registrations": [{"start_date": date(2014, 7, 10)}],
        "clinical_events": [{"date": date(2015, 5, 9), "snomedct_code": "111552007"}],
        "expected_in_population": True,
        "expected_columns": {
            "pat_age": 24,
            "reg_date": date(2014, 7, 10),
            "dereg_date": None,
            "dm_dat": date(2015, 5, 9),
            "dmlat_dat": date(2015, 5, 9),
            "dmres_dat": None,
        },
    },
    # Expected in population
    4: {
        "patients": {"date_of_birth": date(2000, 1, 1)},
        "practice_registrations": [{"start_date": date(2014, 7, 10)}],
        "clinical_events": [
            {"date": date(2014, 7, 9), "snomedct_code": "111552007"},
            {"date": date(2015, 5, 8), "snomedct_code": "315051004"},
            {"date": date(2015, 5, 9), "snomedct_code": "111552007"},
        ],
        "expected_in_population": True,
        "expected_columns": {
            "pat_age": 24,
            "reg_date": date(2014, 7, 10),
            "dereg_date": None,
            "dm_dat": date(2014, 7, 9),
            "dmlat_dat": date(2015, 5, 9),
            "dmres_dat": date(2015, 5, 8),
        },
    },
}
