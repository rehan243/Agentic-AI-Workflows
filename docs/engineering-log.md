# Engineering Log

Running notes on design decisions and lessons learned.


### 2026-07-07

Refined the tool routing logic to prioritize low-latency APIs first, which improved overall response time but occasionally caused suboptimal tool selection when fallback tools had better accuracy. Multi-step planning needs explicit state passing between steps to avoid context loss, especially when chaining heterogeneous tools with varying input/output formats.

### 2026-07-08

experimented with dynamic tool prioritization to improve multi-step planning, but found that overly aggressive routing caused some steps to timeout when the chosen tools were slow or unresponsive. balancing the routing logic to include fallback options helped mitigate this, but added complexity to the orchestration layer.
