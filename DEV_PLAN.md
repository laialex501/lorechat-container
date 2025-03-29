# LoreChat Development Plan: Monitoring & Observability

## Overview

This document outlines the implementation plan for LoreChat's monitoring system. The goal is to create a comprehensive observability layer that provides insights into:
- System performance and health
- User interaction patterns
- Resource utilization
- Error detection and diagnosis

## 1. Event Logging Architecture

### Event Types

```python
class EventType(str, Enum):
    # Chat Events
    CHAT_START = "chat.start"
    CHAT_MESSAGE = "chat.message"
    CHAT_COMPLETE = "chat.complete"
    
    # Graph Events
    GRAPH_NODE_ENTER = "graph.node.enter"
    GRAPH_NODE_EXIT = "graph.node.exit"
    GRAPH_STATE_UPDATE = "graph.state.update"
    
    # Vector Store Events
    VECTOR_SEARCH = "vector.search"
    VECTOR_INSERT = "vector.insert"
    VECTOR_UPDATE = "vector.update"
    
    # LLM Events
    LLM_REQUEST = "llm.request"
    LLM_RESPONSE = "llm.response"
    LLM_ERROR = "llm.error"
```

### Event Context

```python
@dataclass
class EventContext:
    # Request Context
    thread_id: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Component Context
    component: str
    action: str
    
    # Performance Context
    duration_ms: Optional[float] = None
    memory_usage: Optional[int] = None
    
    # Error Context
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)
```

### Logger Implementation

```python
class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger("lorechat")
        self._setup_handlers()
    
    def log_event(
        self,
        event_type: EventType,
        context: EventContext,
        **kwargs: Any
    ) -> None:
        """Log structured event with context."""
        event_data = {
            "event": event_type,
            "context": context.to_dict(),
            **kwargs
        }
        self.logger.info(json.dumps(event_data))
```

## 2. Metrics Collection

### Core Metrics

```python
class MetricsCollector:
    def __init__(self):
        # Response Time Metrics
        self.response_time = Histogram(
            "chat_response_time_seconds",
            "Time taken to generate response",
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
        )
        
        # Token Usage Metrics
        self.token_usage = Counter(
            "llm_token_usage_total",
            "Total tokens used by LLM",
            ["model", "type"]
        )
        
        # Memory Metrics
        self.memory_usage = Gauge(
            "chat_memory_bytes",
            "Memory usage per chat session",
            ["thread_id"]
        )
        
        # Vector Store Metrics
        self.vector_ops = Counter(
            "vector_store_operations_total",
            "Vector store operation count",
            ["operation", "status"]
        )
        
        # Graph Metrics
        self.node_duration = Histogram(
            "graph_node_duration_seconds",
            "Time spent in graph nodes",
            ["node_name"]
        )
```

### Integration Points

1. Chat Service:
```python
class ChatService:
    def process_message(self, query: str, thread_id: str) -> str:
        with EventContext(thread_id=thread_id) as ctx:
            # Track response time
            with self.metrics.response_time.time():
                response = self._generate_response(query)
            
            # Log completion
            self.logger.log_event(
                EventType.CHAT_COMPLETE,
                ctx,
                query=query,
                response_length=len(response)
            )
            
            return response
```

2. Graph Nodes:
```python
def retrieve_context(state: ChatState) -> Dict[str, Any]:
    with EventContext(thread_id=state.thread_id) as ctx:
        # Track node execution
        with metrics.node_duration.labels("retrieve").time():
            docs = vector_store.similarity_search(
                state.messages[-1].content
            )
        
        # Log retrieval
        logger.log_event(
            EventType.GRAPH_NODE_EXIT,
            ctx,
            docs_retrieved=len(docs)
        )
        
        return {"retrieved_docs": docs}
```

3. Vector Store:
```python
def similarity_search(self, query: str, **kwargs: Any) -> List[Document]:
    with EventContext() as ctx:
        try:
            results = self._search(query, **kwargs)
            
            # Track operation
            self.metrics.vector_ops.labels(
                operation="search",
                status="success"
            ).inc()
            
            return results
            
        except Exception as e:
            # Log error with context
            ctx.error = {
                "type": type(e).__name__,
                "message": str(e)
            }
            self.logger.log_event(
                EventType.VECTOR_SEARCH,
                ctx
            )
            raise
```

## 3. Analysis & Visualization

### Real-time Monitoring

1. Metrics Dashboard:
```python
def create_metrics_dashboard():
    """Create Streamlit metrics dashboard."""
    st.title("LoreChat Monitoring")
    
    # Response Time Distribution
    fig = px.histogram(
        get_response_times(),
        nbins=20,
        title="Response Time Distribution"
    )
    st.plotly_chart(fig)
    
    # Memory Usage
    fig = px.line(
        get_memory_usage(),
        title="Memory Usage Over Time"
    )
    st.plotly_chart(fig)
    
    # Error Rate
    fig = px.bar(
        get_error_rates(),
        title="Error Rate by Component"
    )
    st.plotly_chart(fig)
```

2. Log Analysis:
```python
def analyze_logs(
    start_time: datetime,
    end_time: datetime
) -> Dict[str, Any]:
    """Analyze logs for time period."""
    return {
        "total_requests": count_events(EventType.CHAT_START),
        "avg_response_time": calculate_avg_response_time(),
        "error_rate": calculate_error_rate(),
        "token_usage": get_token_usage_stats(),
        "popular_queries": get_popular_queries()
    }
```

### Performance Optimization

1. Automatic Alerting:
```python
class PerformanceMonitor:
    def check_metrics(self) -> None:
        """Check metrics against thresholds."""
        # Response time alerts
        if self.get_p95_response_time() > 2.0:
            self.alert("High response time detected")
            
        # Memory usage alerts
        if self.get_memory_usage() > 500_000_000:
            self.alert("High memory usage detected")
            
        # Error rate alerts
        if self.get_error_rate() > 0.05:
            self.alert("High error rate detected")
```

2. Optimization Recommendations:
```python
def generate_recommendations() -> List[str]:
    """Generate optimization recommendations."""
    recs = []
    
    # Check vector store performance
    if get_avg_search_time() > 0.5:
        recs.append(
            "Consider optimizing vector store index"
        )
    
    # Check memory usage
    if get_memory_growth_rate() > 0.1:
        recs.append(
            "Investigate potential memory leaks"
        )
    
    # Check token usage
    if get_token_usage_rate() > 1000:
        recs.append(
            "Consider implementing token usage caching"
        )
    
    return recs
```

## Implementation Steps

1. Core Infrastructure
- [ ] Set up structured logging
- [ ] Implement metrics collection
- [ ] Create monitoring dashboard

2. Component Integration
- [ ] Add logging to chat service
- [ ] Add logging to graph nodes
- [ ] Add logging to vector store
- [ ] Add logging to LLM service

3. Analysis Tools
- [ ] Build real-time monitoring
- [ ] Implement log analysis
- [ ] Create alerting system

4. Documentation
- [ ] Document event types
- [ ] Document metrics
- [ ] Create troubleshooting guide

## Data Management

### Retention Strategy

1. Log Rotation:
```python
LOG_RETENTION = {
    "raw_events": {
        "retention_days": 30,
        "max_size_gb": 10,
        "compression": True
    },
    "aggregated_metrics": {
        "retention_days": 365,
        "resolution": {
            "1m": "7d",    # 1-minute resolution for 7 days
            "5m": "30d",   # 5-minute resolution for 30 days
            "1h": "90d",   # 1-hour resolution for 90 days
            "1d": "365d"   # 1-day resolution for 1 year
        }
    }
}
```

2. Data Aggregation:
```python
class MetricsAggregator:
    def aggregate_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
        resolution: str
    ) -> pd.DataFrame:
        """Aggregate metrics for time period."""
        metrics = {
            "response_time": {
                "p50": self._calculate_percentile(50),
                "p95": self._calculate_percentile(95),
                "p99": self._calculate_percentile(99)
            },
            "error_rate": self._calculate_error_rate(),
            "throughput": self._calculate_throughput(),
            "memory_usage": {
                "mean": self._calculate_mean_memory(),
                "max": self._calculate_max_memory()
            }
        }
        return pd.DataFrame(metrics)

    def cleanup_old_data(self) -> None:
        """Remove data beyond retention period."""
        for metric_type, config in LOG_RETENTION.items():
            self._cleanup_metric(
                metric_type,
                days=config["retention_days"]
            )
```

3. Storage Optimization:
```python
class StorageManager:
    def optimize_storage(self) -> None:
        """Optimize metric storage."""
        # Compress old data
        self._compress_old_logs()
        
        # Downsample metrics
        self._downsample_metrics()
        
        # Archive cold data
        self._archive_cold_data()
```

### Analysis Capabilities

1. Trend Analysis:
```python
def analyze_trends(
    metric: str,
    window: str = "7d"
) -> Dict[str, Any]:
    """Analyze metric trends."""
    return {
        "current_value": get_current_value(metric),
        "change_vs_previous": get_change_rate(metric, window),
        "trend": calculate_trend(metric, window),
        "forecast": predict_next_value(metric)
    }
```

2. Pattern Detection:
```python
def detect_patterns() -> List[Dict[str, Any]]:
    """Detect usage patterns."""
    patterns = []
    
    # Usage patterns
    patterns.extend(
        detect_usage_patterns(
            window="30d",
            min_confidence=0.8
        )
    )
    
    # Error patterns
    patterns.extend(
        detect_error_patterns(
            window="7d",
            threshold=0.05
        )
    )
    
    # Performance patterns
    patterns.extend(
        detect_performance_patterns(
            window="24h",
            deviation_threshold=2.0
        )
    )
    
    return patterns
```

## Success Metrics

1. System Health
- Response time P95 < 2s
- Error rate < 1%
- Memory usage < 500MB per session

2. Observability
- 100% trace coverage
- All errors logged with context
- All performance metrics collected

3. Usability
- Real-time monitoring dashboard
- Automated alerts
- Clear error messages

4. Data Management
- Log retention compliance
- Successful data aggregation
- Efficient storage utilization
