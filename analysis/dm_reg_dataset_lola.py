from ehrql import create_dataset, show, codelist_from_csv
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
from codelists import *
#codelists
dm_cod = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-dm_cod.csv", column="code")
dmres_cod = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-dmres_cod.csv", column="code")

index_date = "2024-03-31"
#prior events
prior_events = clinical_events.where(clinical_events.date.is_on_or_before(index_date))

#registration
has_registration = practice_registrations.for_patient_on(index_date).exists_for_patient()

registration_start_date = (
practice_registrations.where(
    practice_registrations.start_date
    .is_on_or_before(index_date))
    .sort_by(practice_registrations.start_date)
    .first_for_patient()
    .start_date
)

registration_end_date = (
practice_registrations.where(
    practice_registrations.end_date
    .is_on_or_before(index_date))
    .sort_by(practice_registrations.end_date)
    .first_for_patient()
    .end_date
)
#patient's age 
was_17_or_older = patients.age_on(index_date) >= 17 
was_alive = patients.is_alive_on(index_date)


#latest diabetes diagnosis date
has_diabetes_diagnosis = clinical_events.snomedct_code.is_in(dm_cod)
latest_diabetes_diagnosis_date= (
    prior_events
    .where(has_diabetes_diagnosis)
    .sort_by(clinical_events.date) 
    .last_for_patient()
    .date
)

#diabetes resolved date
diabetes_resolved = (clinical_events.snomedct_code.is_in(dmres_cod))
latest_diabetes_resolved_date = (prior_events
.where(diabetes_resolved)
.sort_by(clinical_events.date)
.last_for_patient()
.date
)

# first diabetes diagnosis date
first_diabetes_diagnosis_date= (
    prior_events
    .where(has_diabetes_diagnosis)
    .sort_by(clinical_events.date) 
    .first_for_patient()
    .date
)
show(practice_registrations, head=5)

#rule 1: diabetes diagnosis on or before index date and latest diagnosis NOT followed by resolved

dm_reg_r1 = (
    (latest_diabetes_resolved_date < latest_diabetes_diagnosis_date) |
    (latest_diabetes_resolved_date.is_null() & latest_diabetes_diagnosis_date.is_not_null())
)
# # rule 2: patients 17 or older

dm_reg_r2 = (
    was_17_or_older &
    was_alive &
    has_registration
)


# create dataset 
dataset = create_dataset()
dataset.define_population(dm_reg_r1 & dm_reg_r2)

dataset.pat_age = patients.age_on(index_date)
dataset.reg_date = registration_start_date
dataset.dereg_date = registration_end_date
dataset.dm_lat = first_diabetes_diagnosis_date
dataset.dmlat_dat = latest_diabetes_diagnosis_date
dataset.dmres_dat = latest_diabetes_resolved_date