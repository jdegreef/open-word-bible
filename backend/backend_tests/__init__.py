"""The backend's tests read a few books of content/, not all of it
(owb/subset.py): importing everything and building search from it in every
language took 17 minutes before the first search test, and the CI job
neared its 45-minute limit as languages were added. These books hold what
the tests look for (John 3:16, Genesis 1, Psalms, Philippians 4:6-7,
Romans, Philemon for the history tests) and text in every site language.
Set OWB_ONLY_BOOKS="" to test on everything, as
.github/workflows/backend-full.yml does each night."""
import os

TEST_BOOKS = ("GEN", "RUT", "PSA", "JHN", "ROM", "GAL", "PHP", "COL", "PHM")

os.environ.setdefault("OWB_ONLY_BOOKS", ",".join(TEST_BOOKS))
