# 4. Tích hợp Adapters

AgentTrace hỗ trợ sẵn (out-of-the-box) các Adapter cho các hệ thống Agent nổi tiếng nhất hiện nay.

## 1. OpenAI Adapter

Giúp theo dõi các sự kiện "Tool Calling" khi sử dụng trực tiếp OpenAI SDK.

```python
from agenttrace.adapters.openai import OpenAITracer

# Khởi tạo adapter với tracer của bạn
openai_tracer = OpenAITracer(tracer)

# Khi lấy response từ OpenAI, truyền vào để phân tích
response = client.chat.completions.create(...)
openai_tracer.trace_completion(run_id, response)
```

## 2. LangChain Adapter

Sử dụng cơ chế Callback Handler của LangChain để tự động bắt trọn mọi sự kiện (Tool, LLM, Chain).

```python
from agenttrace.adapters.langchain import AgentTraceCallbackHandler
from langchain.agents import initialize_agent

callback = AgentTraceCallbackHandler(tracer, run_id)

agent = initialize_agent(
    tools, 
    llm, 
    agent="zero-shot-react-description",
    callbacks=[callback] # Truyền callback vào
)
agent.run("What is 2 + 2?")
```

## 3. LlamaIndex Adapter

Cắm trực tiếp vào hệ thống Event Dispatcher của LlamaIndex.

```python
from agenttrace.adapters.llamaindex import LlamaIndexTracer
from llama_index.core import set_global_handler

# Đăng ký global handler
handler = LlamaIndexTracer(tracer, run_id)
set_global_handler(handler)

# Mọi Query Engine hay Agent của LlamaIndex giờ đây đều được theo dõi
```

## 4. MCP Proxy (Model Context Protocol)

Theo dõi giao tiếp chuẩn MCP giữa IDE/Agent và các MCP Server.

```python
from agenttrace.adapters.mcp import MCPTracerProxy

proxy = MCPTracerProxy(tracer, run_id, target_server_url="http://localhost:3000")
proxy.start(port=8080)
# Bây giờ IDE của bạn kết nối vào localhost:8080 thay vì 3000
```

---

[Tiếp theo: Tích hợp IDE Antigravity →](05-ide-integration.md)
