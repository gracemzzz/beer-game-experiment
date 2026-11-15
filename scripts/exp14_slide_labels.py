"""User-specified hypothesis wording shared by the two presentation figures."""

HYPOTHESIS_LABELS = {
    "H1": "Tight deadlines increase pipeline underweighting",
    "H2": "Tight deadlines increase total holding and backlog costs.",
}


def hypothesis_heading(hypothesis):
    return f"{hypothesis}: {HYPOTHESIS_LABELS[hypothesis]}".replace(" increase ", " increase\n", 1)
