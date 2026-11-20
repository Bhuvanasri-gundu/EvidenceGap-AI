"""Biomedical Knowledge Graph Construction Module.

Constructs multi-relational graphs of papers, topics, diseases, interventions,
technologies, and outcomes using NetworkX.
Explicitly differentiates ontology-defined edges from literature co-occurrence edges.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from config.settings import GRAPHS_DIR
from src.knowledge_graph.concept_extractor import concept_extractor
from src.ontology.mesh_mapper import mesh_mapper

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builds and analyzes multi-relational knowledge graphs of scientific research."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or GRAPHS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.graph = nx.MultiDiGraph()

    def build_from_corpus(
        self,
        documents: List[Dict[str, Any]],
        max_docs: int = 500,
    ) -> nx.MultiDiGraph:
        """Build knowledge graph from paper texts, MeSH annotations, and extracted entities."""
        self.graph.clear()
        logger.info("Building knowledge graph from %d corpus documents...", min(len(documents), max_docs))

        # 1. Add ontology-defined edges first
        for term, data in mesh_mapper.hierarchy.items():
            self.graph.add_node(term, type="concept", category="ontology_concept")
            for broader in data["broader"]:
                self.graph.add_node(broader, type="concept", category="ontology_concept")
                self.graph.add_edge(term, broader, relation="subclass_of", source_type="ontology")
            for narrower in data["narrower"]:
                self.graph.add_node(narrower, type="concept", category="ontology_concept")
                self.graph.add_edge(narrower, term, relation="subclass_of", source_type="ontology")

        # 2. Add literature-derived nodes and edges
        for doc in documents[:max_docs]:
            pmid = str(doc.get("pmid", ""))
            if not pmid:
                continue

            title = doc.get("title", "")
            abstract = doc.get("abstract", "")
            paper_node = f"PMID:{pmid}"

            self.graph.add_node(
                paper_node,
                type="paper",
                label=title[:60] + "..." if len(title) > 60 else title,
                pmid=pmid,
                year=doc.get("pub_year"),
                source_type="literature",
            )

            # Link to MeSH terms
            for mesh in doc.get("mesh_terms") or []:
                self.graph.add_node(mesh, type="concept", category="mesh_heading")
                self.graph.add_edge(paper_node, mesh, relation="indexed_with", source_type="literature")

            # Extract typed entities
            text = f"{title} {abstract}"
            extracted = concept_extractor.extract_entities(text)

            for cat, terms in extracted.items():
                for t in terms:
                    concept_id = t.title()
                    self.graph.add_node(concept_id, type="concept", category=cat.lower())
                    relation = "studies" if cat == "Disease" else "evaluates" if cat == "Technology" else "targets"
                    self.graph.add_edge(paper_node, concept_id, relation=relation, source_type="literature")

        logger.info(
            "Knowledge Graph constructed: %d nodes, %d edges",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )
        return self.graph

    def get_visualization_data(self, max_nodes: int = 100) -> Dict[str, Any]:
        """Convert graph subset to node/edge format for React frontend visualization."""
        nodes = []
        edges = []

        # Subgraph of top nodes by degree
        top_nodes = sorted(self.graph.degree, key=lambda x: x[1], reverse=True)[:max_nodes]
        sub_nodes = set([n for n, _ in top_nodes])
        subgraph = self.graph.subgraph(sub_nodes)

        for n, data in subgraph.nodes(data=True):
            nodes.append({
                "id": str(n),
                "label": data.get("label", str(n)),
                "type": data.get("category", data.get("type", "concept")),
                "properties": data,
            })

        for u, v, data in subgraph.edges(data=True):
            edges.append({
                "source": str(u),
                "target": str(v),
                "relation": data.get("relation", "relates_to"),
                "source_type": data.get("source_type", "literature"),
            })

        return {"nodes": nodes, "edges": edges}

    def save_graph(self, filename: str = "knowledge_graph.json") -> Path:
        """Export graph to JSON for persistence."""
        out_path = self.output_dir / filename
        data = self.get_visualization_data(max_nodes=500)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out_path


builder = KnowledgeGraphBuilder()
