"""
Smart Fuzzy Search Engine
Adapted for your exact model structure
Uses RapidFuzz for typo-tolerant search
No external APIs required
"""

from rapidfuzz import fuzz
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Query


class FuzzySearchEngine:
    """
    Lightweight fuzzy search engine that works with SQLAlchemy queries
    """
    
    def __init__(self, fuzzy_threshold: int = 70):
        """
        Args:
            fuzzy_threshold: Minimum similarity score (0-100) for matches
        """
        self.fuzzy_threshold = fuzzy_threshold
    
    def search_records(self,
                      records: List[Any],
                      query: str,
                      search_fields: List[str],
                      field_weights: Optional[Dict[str, float]] = None) -> List[Dict]:
        """
        Search through records with fuzzy matching
        
        Args:
            records: List of SQLAlchemy model instances
            query: Search query string
            search_fields: Fields to search in (e.g., ['first_name', 'email'])
            field_weights: Optional weights for each field
            
        Returns:
            List of dicts with records and relevance scores
        """
        if not query or not records:
            return []
        
        query = query.strip().lower()
        
        if not field_weights:
            field_weights = {field: 1.0 for field in search_fields}
        
        results = []
        
        for record in records:
            score, match_details = self._calculate_match_score(
                query, record, search_fields, field_weights
            )
            
            if score >= self.fuzzy_threshold:
                results.append({
                    'record': record,
                    'search_score': round(score, 2),
                    'matched_field': match_details.get('matched_field'),
                    'match_type': match_details.get('match_type')
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['search_score'], reverse=True)
        
        return results
    
    def _calculate_match_score(self,
                               query: str,
                               record: Any,
                               search_fields: List[str],
                               field_weights: Dict[str, float]) -> tuple:
        """
        Calculate weighted match score for a record
        """
        field_scores = {}
        max_score = 0
        matched_field = None
        match_type = None
        
        for field in search_fields:
            # Get field value from SQLAlchemy model
            field_value = getattr(record, field, None)
            
            if field_value is None:
                continue
            
            field_value = str(field_value).lower().strip()
            
            if not field_value:
                continue
            
            # Strategy 1: Exact substring match (highest priority)
            if query in field_value:
                score = 100
                field_scores[field] = score
                if score > max_score:
                    max_score = score
                    matched_field = field
                    match_type = 'exact'
                continue
            
            # Strategy 2: Fuzzy matching with RapidFuzz
            fuzzy_score = fuzz.partial_ratio(query, field_value)
            
            # Strategy 3: Token-based matching (word-by-word)
            token_score = self._token_match_score(query, field_value)
            
            # Use the best score
            score = max(fuzzy_score, token_score)
            field_scores[field] = score
            
            if score > max_score:
                max_score = score
                matched_field = field
                match_type = 'fuzzy' if fuzzy_score > token_score else 'token'
        
        # Calculate weighted average
        if not field_scores:
            return 0, {}
        
        total_weight = sum(field_weights.get(f, 1.0) for f in field_scores.keys())
        
        if total_weight == 0:
            return 0, {}
        
        weighted_score = sum(
            score * field_weights.get(field, 1.0) 
            for field, score in field_scores.items()
        ) / total_weight
        
        match_details = {
            'matched_field': matched_field,
            'match_type': match_type,
            'field_scores': field_scores
        }
        
        return weighted_score, match_details
    
    def _token_match_score(self, query: str, text: str) -> float:
        """
        Score based on individual word matching
        """
        query_tokens = set(query.split())
        text_tokens = set(text.split())
        
        if not query_tokens:
            return 0
        
        # Count matching tokens
        matching = query_tokens & text_tokens
        
        # Calculate Jaccard similarity
        jaccard = len(matching) / len(query_tokens | text_tokens)
        
        return jaccard * 100


def apply_fuzzy_search_to_query(
    base_query: Query,
    model_class: Any,
    fuzzy_query: str,
    search_fields: List[str],
    field_weights: Optional[Dict[str, float]] = None,
    fuzzy_threshold: int = 70
) -> List[Any]:
    """
    Helper function to apply fuzzy search to existing SQLAlchemy query
    
    Usage:
        base_query = db.query(User).filter(User.organization_id == org_id)
        results = apply_fuzzy_search_to_query(
            base_query=base_query,
            model_class=User,
            fuzzy_query="john doe",
            search_fields=['first_name', 'last_name', 'email']
        )
    
    Returns:
        List of model instances sorted by relevance
    """
    # Execute base query to get all records
    all_records = base_query.all()
    
    if not all_records:
        return []
    
    # Apply fuzzy search
    engine = FuzzySearchEngine(fuzzy_threshold=fuzzy_threshold)
    fuzzy_results = engine.search_records(
        records=all_records,
        query=fuzzy_query,
        search_fields=search_fields,
        field_weights=field_weights
    )
    
    # Extract just the records (sorted by relevance)
    return [result['record'] for result in fuzzy_results]


def get_fuzzy_search_metadata(
    base_query: Query,
    fuzzy_query: str,
    search_fields: List[str],
    field_weights: Optional[Dict[str, float]] = None,
    fuzzy_threshold: int = 70
) -> Dict:
    """
    Get fuzzy search results WITH metadata (scores, matched fields, etc.)
    
    Returns dict with:
        - records: List of model instances
        - metadata: Search scores and match details for each record
    """
    all_records = base_query.all()
    
    if not all_records:
        return {'records': [], 'metadata': []}
    
    engine = FuzzySearchEngine(fuzzy_threshold=fuzzy_threshold)
    fuzzy_results = engine.search_records(
        records=all_records,
        query=fuzzy_query,
        search_fields=search_fields,
        field_weights=field_weights
    )
    
    records = [result['record'] for result in fuzzy_results]
    metadata = [
        {
            'search_score': result['search_score'],
            'matched_field': result['matched_field'],
            'match_type': result['match_type']
        }
        for result in fuzzy_results
    ]
    
    return {'records': records, 'metadata': metadata}