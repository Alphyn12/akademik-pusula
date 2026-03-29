"""
Utility helpers for UI-level data transformations.

Extracted from app.py as part of the Faz-3 architectural refactor.
These are pure functions with no Streamlit state dependency.
"""
from typing import Optional

import pandas as pd


def tr_lower(text: str) -> str:
    """
    Turkish-aware lowercase conversion.

    Standard str.lower() does not correctly handle the dotted/dotless I
    distinction in Turkish (İ → i, I → ı). This function handles those
    edge cases before delegating to built-in lower().
    """
    if not text:
        return ""
    return text.replace("İ", "i").replace("I", "ı").lower()


def generate_scihub_link(row: pd.Series, sci_hub_base: str) -> Optional[str]:
    """
    Generates a Sci-Hub URL for a given article row if a DOI is available.

    Args:
        row: A pandas Series representing a single article record.
        sci_hub_base: The base URL of the Sci-Hub mirror (e.g. 'https://sci-hub.ist').

    Returns:
        A fully-formed Sci-Hub URL string, or None if no usable DOI exists.
    """
    doi = row.get("DOI")
    if pd.notna(doi) and str(doi) != "-":
        clean_doi = (
            str(doi)
            .replace("https://doi.org/", "")
            .replace("http://dx.doi.org/", "")
        )
        return f"{sci_hub_base.rstrip('/')}/{clean_doi}"
    return None
