"""Constants and enums for the graph-based workflow."""
from enum import Enum


class SubqueryStatus(str, Enum):
    """Status values for subquery processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class QueryComplexity(str, Enum):
    """Complexity levels for user queries."""
    SIMPLE = "simple"
    COMPLEX = "complex"
    UNKNOWN = "unknown"


# Error messages
ERROR_MESSAGES = {
    "RETRIEVAL_FAILED": "Failed to retrieve relevant documents",
    "EVALUATION_FAILED": "Failed to evaluate document relevance",
    "REFINEMENT_FAILED": "Failed to refine query",
    "ANSWER_FAILED": "Failed to generate answer",
    "NO_RESULTS": "No results available for the query",
    "PROCESSING_FAILED": "Failed to process subquery",
    "COMBINATION_FAILED": "Failed to combine results",
    "RESPONSE_FAILED": "Failed to generate response"
}

# Processing constants
MAX_REFINEMENTS = 3
DEFAULT_RETRIEVAL_COUNT = 3
