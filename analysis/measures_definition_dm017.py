from ehrql import INTERVAL, create_measures, months
from ehrql.tables.core import practice_registrations, patients, clinical_events
from codelists import dm_cod, dmres_cod

measures = create_measures()
INTERVAL.end_date

# Events up to month end
selected_events = clinical_events.where(clinical_events.date <= INTERVAL.end_date)

# Base population at month end
aged_17_or_older = patients.age_on(INTERVAL.end_date) >= 17
is_alive = patients.is_alive_on(INTERVAL.end_date)

is_registered = (
    practice_registrations.where(practice_registrations.start_date <= INTERVAL.end_date)
    .except_where(practice_registrations.end_date < INTERVAL.end_date)
    .exists_for_patient()
)

# Diabetes "unresolved" status at month end
latest_diabetes_diagnosis_date = (
    selected_events.where(clinical_events.snomedct_code.is_in(dm_cod))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)

latest_diabetes_resolved_date = (
    selected_events.where(clinical_events.snomedct_code.is_in(dmres_cod))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)

has_unresolved_diabetes = latest_diabetes_diagnosis_date.is_not_null() & (
    latest_diabetes_resolved_date.is_null()
    | (latest_diabetes_resolved_date < latest_diabetes_diagnosis_date)
)

# DM017 register membership at month end
on_dm017_register = (
    aged_17_or_older & is_alive & is_registered & has_unresolved_diabetes
)

# Measures
# Count on register each month
measures.define_measure(
    name="dm017_register_count",
    numerator=on_dm017_register,
    denominator=on_dm017_register,
    group_by={"sex": patients.sex},
    intervals=months(12).starting_on("2023-04-01"),
)

# Prevalence: % of registered patients aged 17+ and alive
# measures.define_measure(
#     name="dm017_register_prevalence",
#     numerator=on_dm017_register,
#     denominator=aged_17_or_older & is_alive & is_registered,
#     intervals=months(12).starting_on("2023-04-01"),
# )
