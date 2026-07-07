# Engineering Log

Running notes on design decisions and lessons learned.


### 2026-07-07

Refined the tool routing logic to prioritize low-latency APIs first, which improved overall response time but occasionally caused suboptimal tool selection when fallback tools had better accuracy. Multi-step planning needs explicit state passing between steps to avoid context loss, especially when chaining heterogeneous tools with varying input/output formats.
