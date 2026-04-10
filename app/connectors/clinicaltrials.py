import requests
from typing import List, Dict, Any

class ClinicalTrialsConnector:
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def fetch_trials(self, query: str, max_documents: int = 5) -> List[Dict[str, Any]]:
        params = {
            "query.term": query,
            "pageSize": max_documents,
            "format": "json",
        }

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        studies = data.get("studies", [])
        docs = []

        for study in studies:
            protocol = study.get("protocolSection", {})
            ident = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            conditions_mod = protocol.get("conditionsModule", {})
            arms_mod = protocol.get("armsInterventionsModule", {})
            desc_mod = protocol.get("descriptionModule", {})
            design_mod = protocol.get("designModule", {})
            outcomes_mod = protocol.get("outcomesModule", {})

            nct_id = ident.get("nctId")
            title = ident.get("briefTitle") or "Untitled"

            conditions = conditions_mod.get("conditions", [])
            interventions = [
                item.get("name")
                for item in arms_mod.get("interventions", [])
                if item.get("name")
            ]
            phases = design_mod.get("phases", [])
            overall_status = status.get("overallStatus")

            brief_summary = desc_mod.get("briefSummary", "")
            primary_outcomes = [
                item.get("measure")
                for item in outcomes_mod.get("primaryOutcomes", [])
                if item.get("measure")
            ]

            raw_text_parts = []
            if brief_summary:
                raw_text_parts.append(brief_summary)
            if primary_outcomes:
                raw_text_parts.append("Primary outcomes: " + "; ".join(primary_outcomes))

            docs.append({
                "external_id": nct_id,
                "source_type": "clinicaltrials",
                "title": title,
                "source_url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None,
                "raw_text": "\n".join(raw_text_parts),
                "metadata_json": {
                    "condition": conditions,
                    "intervention": interventions,
                    "phase": phases,
                    "status": overall_status,
                }
            })

        return docs