import datetime
import logging
from difflib import SequenceMatcher
from typing import Dict, Any, Optional

from zeep import Client
from zeep.exceptions import Fault

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The WSDL URL for the v9 ANAF web service
WSDL_URL = "https://webservicesp.anaf.ro/PlatitorTvaRest/api/v9/ws?wsdl"

def get_company_details(cui: str, expected_name: str, name_match_threshold: float = 0.6) -> Optional[Dict[str, Any]]:
    """
    Fetches and verifies company details from the ANAF v9 web service.

    This function retrieves company data using its CUI, then compares the
    official name from ANAF with an expected name to ensure they are similar.

    Args:
        cui: The company's CUI (Cod Unic de Înregistrare).
        expected_name: The name of the company you expect to find (e.g., from a scraper).
        name_match_threshold: A value between 0 and 1 for name similarity.
                              Defaults to 0.6 (60% match).

    Returns:
        A dictionary with the company's details if the CUI is valid and the
        name is a reasonable match, otherwise None.
    """
    try:
        client = Client(wsdl=WSDL_URL)
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        payload = [{"cui": cui, "data": current_date}]

        response = client.service.wsPlatitorTva(payload)

        if not response or not response.found:
            logger.warning(f"CUI {cui} not found in ANAF database.")
            return None

        company_data = response.found[0]
        anaf_name = company_data.date_generale.denumire

        # Compare the name from ANAF with the expected name
        similarity = SequenceMatcher(None, anaf_name.lower(), expected_name.lower()).ratio()

        if similarity < name_match_threshold:
            logger.warning(
                f"Name mismatch for CUI {cui}. "
                f"ANAF: '{anaf_name}', Expected: '{expected_name}', "
                f"Similarity: {similarity:.2f}"
            )
            return None

        logger.info(f"Successfully verified CUI {cui} for company '{anaf_name}'.")
        return {
            "cui": company_data.date_generale.cui,
            "name": anaf_name,
            "address": company_data.date_generale.adresa,
            "phone": company_data.date_generale.telefon,
            "vat_registered": company_data.date_generale.scpTVA,
            "status": {
                "vat_active_from": company_data.inregistrare_scop_Tva.d_inceput_ScpTVA,
                "vat_inactive": company_data.stare_inregistrare_scop_TVA.stare_inactivare,
                "reactivation_date": company_data.stare_inregistrare_scop_TVA.d_reactivare_TVA,
                "cancellation_date": company_data.stare_inregistrare_scop_TVA.d_anulare_TVA,
            }
        }

    except Fault as e:
        logger.error(f"SOAP Fault for CUI {cui}: {e.message}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred for CUI {cui}: {e}")
        return None
