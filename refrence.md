Based on the state and flow we've settled on, here are the nodes you need to create — one Python function each, matching the table from earlier:

intake — parses/merges user message into destination, total_days, interests, budget_hint, start_date, end_date; decides if something required is missing.
router — LLM call using RouterDecision; judges what's still missing and picks one route (travel, budget, currency, hotel, weather, retriever, web_search, verify_search, direct_answer).
tools — this is just your existing get_tool_node(retriever) ToolNode, not something new to write.
collect — non-LLM node; reads the latest ToolMessage and files it into rag_context / place_info / hotel_results / weather_results / currency_notes; updates gathered_sources.
generator — LLM call forced into TravelPlan structured output.
validator — non-LLM node; runs Pydantic validation on travel_plan, sets/clears validation_error.

Plus two conditional edge functions (not graph nodes, but Python functions you register with add_conditional_edges):

route_after_intake — intake → router or intake → END
route_after_router — router → tools or router → generator
(you'll also want a route_after_validator — validator → generator or validator → END)

So: 5 real nodes (intake, router, collect, generator, validator) + 1 reused node (tools = your ToolNode) + 3 conditional-edge functions.