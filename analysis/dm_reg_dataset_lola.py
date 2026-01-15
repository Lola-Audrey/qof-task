from ehrql import codelist_from_csv, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events

index_date = "2024-03-31"

#codelists
dm_cod = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-dm_cod.csv", column="code")
dmres_cod = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-dmres_cod.csv", column="code")

#patient's age 
is_17_or_older = patients.age_on(index_date) >= 17 
is_alive = patients.is_alive_on(index_date)

pat_age = is_17_or_older & is_alive


