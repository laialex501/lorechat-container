"""Unit tests for the enhanced state management."""
from app.chat.graph.constants import QueryComplexity, SubqueryStatus
from app.chat.graph.enhanced_state import SubQuery, create_enhanced_chat_state
from langchain.schema import Document
from langchain_core.messages import AIMessage, HumanMessage

# Test constants
TEST_QUERY = "What is the capital of France?"
TEST_ANSWER = "The capital of France is Paris."
TEST_CONTENT = "Paris is the capital of France"
TEST_URL = "https://example.com"
TEST_THREAD_ID = "test-thread-id"
TEST_QUERY_POPULATION = "What is the population of Paris?"


class TestSubQuery:
    """Tests for the SubQuery class."""

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        # Execute
        subquery = SubQuery(text=TEST_QUERY)
        
        # Verify
        assert subquery.text == TEST_QUERY
        assert subquery.status == SubqueryStatus.PENDING
        assert subquery.retrieved_docs == []
        assert subquery.refinement_count == 0
        assert subquery.result == ""
        assert subquery.sources == []
        assert subquery.id is not None  # Should have a UUID

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        # Setup
        docs = [Document(page_content=TEST_CONTENT, metadata={"url": TEST_URL})]
        
        # Execute
        subquery = SubQuery(
            text=TEST_QUERY,
            status=SubqueryStatus.COMPLETE,
            retrieved_docs=docs,
            refinement_count=2,
            result=TEST_ANSWER,
            sources=[TEST_URL]
        )
        
        # Verify
        assert subquery.text == TEST_QUERY
        assert subquery.status == SubqueryStatus.COMPLETE
        assert subquery.retrieved_docs == docs
        assert subquery.refinement_count == 2
        assert subquery.result == TEST_ANSWER
        assert subquery.sources == [TEST_URL]
        assert subquery.id is not None  # Should have a UUID

    def test_unique_ids(self):
        """Test that each SubQuery gets a unique ID."""
        # Execute
        subquery1 = SubQuery(text="Query 1")
        subquery2 = SubQuery(text="Query 2")
        
        # Verify
        assert subquery1.id != subquery2.id


class TestEnhancedChatState:
    """Tests for the EnhancedChatState class."""

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        # Execute
        state = create_enhanced_chat_state()
        
        # Verify
        assert state["messages"] == []
        assert state["subqueries"] == []
        assert state["original_query"] == ""
        assert state["query_complexity"] == QueryComplexity.SIMPLE
        assert state["combined_answer"] is None
        assert state["thread_id"] is not None  # Should have a UUID

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        # Setup
        messages = [
            HumanMessage(content=TEST_QUERY),
            AIMessage(content=TEST_ANSWER)
        ]
        subqueries = [
            SubQuery(text=TEST_QUERY, status=SubqueryStatus.COMPLETE)
        ]
        
        # Execute
        state = create_enhanced_chat_state(
            messages=messages,
            subqueries=subqueries,
            original_query=TEST_QUERY,
            query_complexity=QueryComplexity.SIMPLE,
            combined_answer=TEST_ANSWER,
            thread_id=TEST_THREAD_ID
        )
        
        # Verify
        assert state["messages"] == messages
        assert state["subqueries"] == subqueries
        assert state["original_query"] == TEST_QUERY
        assert state["query_complexity"] == QueryComplexity.SIMPLE
        assert state["combined_answer"] == TEST_ANSWER
        assert state["thread_id"] == TEST_THREAD_ID

    def test_unique_thread_ids(self):
        """Test that each EnhancedChatState gets a unique thread ID."""
        # Execute
        state1 = create_enhanced_chat_state()
        state2 = create_enhanced_chat_state()
        
        # Verify
        assert state1["thread_id"] != state2["thread_id"]

    def test_attribute_and_dictionary_access(self):
        """Test both attribute and dictionary-style access to state attributes."""
        # Setup
        state = create_enhanced_chat_state()
        
        # Execute - dictionary style
        state["original_query"] = TEST_QUERY
        state["query_complexity"] = QueryComplexity.COMPLEX
        state["combined_answer"] = TEST_ANSWER
        
        # Verify - dictionary style
        assert state["original_query"] == TEST_QUERY
        assert state["query_complexity"] == QueryComplexity.COMPLEX
        assert state["combined_answer"] == TEST_ANSWER

    def test_adding_messages(self):
        """Test adding messages to the state."""
        # Setup
        state = create_enhanced_chat_state()
        
        # Execute
        messages = []
        messages.append(HumanMessage(content=TEST_QUERY))
        messages.append(AIMessage(content=TEST_ANSWER))
        state["messages"] = messages
        
        # Verify
        assert len(state["messages"]) == 2
        assert state["messages"][0].content == TEST_QUERY
        assert state["messages"][1].content == TEST_ANSWER

    def test_adding_subqueries(self):
        """Test adding subqueries to the state."""
        # Setup
        state = create_enhanced_chat_state()
        
        # Execute
        subqueries = []
        subqueries.append(SubQuery(text=TEST_QUERY))
        subqueries.append(SubQuery(text=TEST_QUERY_POPULATION))
        state["subqueries"] = subqueries
        
        # Verify
        assert len(state["subqueries"]) == 2
        assert state["subqueries"][0].text == TEST_QUERY
        assert state["subqueries"][1].text == TEST_QUERY_POPULATION
