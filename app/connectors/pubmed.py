from Bio import Entrez
from typing import List
from app.core.config import settings

Entrez.email = settings.pubmed_email

class PubMedConnector:
    def search(self, query: str, max_documents: int = 5) -> List[dict]:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_documents, sort="relevance")
        record = Entrez.read(handle)
        handle.close()

        pmids = record.get("IdList", [])
        if not pmids:
            return []

        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=",".join(pmids),
            retmode="xml"
        )
        articles = Entrez.read(fetch_handle)
        fetch_handle.close()

        docs = []
        for article in articles["PubmedArticle"]:
            medline = article.get("MedlineCitation", {})
            article_data = medline.get("Article", {})

            title = str(article_data.get("ArticleTitle", "Untitled"))
            abstract = article_data.get("Abstract", {})
            abstract_text = " ".join(abstract.get("AbstractText", [])) if abstract else ""

            authors = []
            for a in article_data.get("AuthorList", []):
                last = a.get("LastName", "")
                fore = a.get("ForeName", "")
                name = f"{fore} {last}".strip()
                if name:
                    authors.append(name)

            pmid = str(medline.get("PMID", ""))
            source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None

            docs.append({
                "external_id": pmid,
                "source_type": "pubmed",
                "title": title,
                "source_url": source_url,
                "raw_text": abstract_text,
                "metadata_json": {
                    "authors": authors,
                    "journal": str(article_data.get("Journal", {}).get("Title", "")),
                    "pub_date": self._extract_pub_date(article_data),
                    "pmid": pmid,
                    "query": query,
                },
            })

        return docs

    def _extract_pub_date(self, article_data: dict) -> str:
        journal = article_data.get("Journal", {})
        issue = journal.get("JournalIssue", {})
        pub_date = issue.get("PubDate", {})
        year = str(pub_date.get("Year", ""))
        month = str(pub_date.get("Month", ""))
        day = str(pub_date.get("Day", ""))
        return "-".join([p for p in [year, month, day] if p])