from ehrql import create_measures, months, days
from ehrql.measures import INTERVAL
from ehrql.tables.core import patients, clinical_events, practice_registrations
import codelists
measures = create_measures()

# PPED for each month
PPED = INTERVAL.end_date

# Events up to PPED
selected_events = clinical_events.where(clinical_events.date.is_on_or_before(PPED))

# Registration and alive at PPED 
is_registered = (
    practice_registrations.where(practice_registrations.start_date <= PPED)
    .except_where(practice_registrations.end_date < PPED)
    .exists_for_patient()
)
is_alive = patients.is_alive_on(PPED)
aged_17_or_older = patients.age_on(INTERVAL.end_date) >= 17

latest_diagnosis_date = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dm_cod))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)

first_diagnosis_date = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dm_cod))
    .sort_by(clinical_events.date)
    .first_for_patient()
    .date
)

first_referral_date = (
    selected_events 
    .where(clinical_events.snomedct_code.is_in(codelists.dsep_cod))
    .sort_by(clinical_events.date)
    .first_for_patient()
    .date
)

reg_dat = (
    practice_registrations
    .where(practice_registrations.start_date.is_on_or_before(PPED))
    .sort_by(practice_registrations.start_date)
    .first_for_patient()
    .start_date
)

has_dseppu_last12m = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dseppu_cod))
    .where(clinical_events.date.is_after(PPED - months(12)))
    .exists_for_patient()
)

has_dmpcapu_last12m = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dmpcapu_cod))
    .where(clinical_events.date.is_after(PPED - months(12)))
    .exists_for_patient()
)

has_dmpcadec_last12m = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dmpcadec_cod))
    .where(clinical_events.date.is_after(PPED - months(12)))
    .exists_for_patient()
)

invite_events_last12m = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dminvite_cod))
    .where(clinical_events.date.is_after(PPED - months(12)))
    .sort_by(clinical_events.date)
)

first_invite_date = invite_events_last12m.first_for_patient().date
last_invite_date = invite_events_last12m.last_for_patient().date

has_two_invites_last12m = (
    first_invite_date.is_not_null()
    & last_invite_date.is_not_null()
    & (last_invite_date >= first_invite_date + days(7))
)

has_dsepsu_within_279 = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dsepsu_cod))
    .where(first_diagnosis_date.is_not_null() & clinical_events.date.is_on_or_between(first_diagnosis_date, first_diagnosis_date + days(279)))
    .exists_for_patient()
)

has_dsepdec_within_279 = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dsepdec_cod))
    .where(first_diagnosis_date.is_not_null() & clinical_events.date.is_on_or_between(first_diagnosis_date, first_diagnosis_date + days(279)))
    .exists_for_patient()
)

# Denominator 
diagnosed_before_qof_eligibility = first_diagnosis_date.is_not_null() & first_diagnosis_date.is_before("2013-04-01")
diagnosed_before_21_months = first_diagnosis_date.is_not_null() & first_diagnosis_date.is_on_or_before(PPED - months(21))
no_referral_within_9_months = first_diagnosis_date.is_not_null() & first_diagnosis_date.is_after(PPED - months(9)) & first_referral_date.is_null()
referred_in_previous_qof_year = first_referral_date.is_not_null() & first_referral_date.is_on_or_before(PPED - months(12))

referral_unavailable = has_dsepsu_within_279
referral_unsuitable = has_dseppu_last12m
diabetes_qc_unsuitable = has_dmpcapu_last12m
referral_declined = has_dsepdec_within_279
diabetes_qc_declined = has_dmpcadec_last12m
no_response_to_two_care_invites = has_two_invites_last12m

diagnosed_within_3_months = first_diagnosis_date.is_not_null() & first_diagnosis_date.is_after(PPED - months(3))
registration_within_3_months = reg_dat.is_not_null() & reg_dat.is_after(PPED - months(3))

exclusion_criteria = (
    referral_unavailable
    | referral_unsuitable
    | diabetes_qc_unsuitable
    | referral_declined
    | diabetes_qc_declined
    | diagnosed_before_qof_eligibility
    | diagnosed_before_21_months
    | no_referral_within_9_months
    | referred_in_previous_qof_year
    | no_response_to_two_care_invites
    | diagnosed_within_3_months
    | registration_within_3_months
)

base_population = is_registered & is_alive & aged_17_or_older & first_diagnosis_date.is_not_null() 
dm014_denominator = base_population & ~exclusion_criteria

referred_within_279_days = (
    selected_events
    .where(clinical_events.snomedct_code.is_in(codelists.dsep_cod))
    .where(clinical_events.date.is_on_or_between(first_diagnosis_date, first_diagnosis_date + days(279)))
    .exists_for_patient()
)

dm014_numerator = dm014_denominator & referred_within_279_days

measures.define_measure(
    name="dm014",
    numerator=dm014_numerator,
    denominator=dm014_denominator,
    intervals=months(12).starting_on("2023-04-01")
)