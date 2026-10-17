# Implementation audit

The checkout is MAS-LAMIH/SemanicIAAgentique, a Python >=3.11 fork of
tutorielIAAgentique. No research protocol PDF was found in the workspace outside
the installed environment. The supplied frozen brief therefore governs Milestone 1.

## Existing implementation

The src layout contains a Groq ReAct loop and several LangGraph multi-agent
examples. Tools are ordinary string-to-string functions (web search, Wikipedia,
calculation, subprocess Python). Groq clients are created at import time;
several multi-agent modules also execute workflows at import. python-dotenv
loads a root .env. The root requirements are unpinned and there is no lockfile.
The existing tests are executable demonstrations, not isolated assertion-based
unit tests; they require external search, Wikipedia, and sometimes Groq.
The pyproject uses Hatchling and declares no runtime dependencies.

## Reuse and adaptation

Retain Python, the src layout, and the existing tutorial unchanged. Its tool
registry can later wrap the semantic executor, but a string alone is insufficient
for evidence, applicability, or verified achievement. Do not reuse eval or the
Python subprocess tool as a contract evaluator. No tutorial imports are needed
for this milestone. Place the isolated implementation in src/semantic_action,
contracts in contracts/, and unittest tests in tests/semantic_action/. Use a
separate requirements-semantic.txt to avoid changing the tutorial's environment.
Only RDFLib is added; HTTP, fixtures, traces, and tests use the standard library.
The existing packaging declaration must include the new module for installed use.

## Licenses and risks

The repository LICENSE is GPL-3.0. Installed distribution metadata identifies
requests (Apache-2.0), python-dotenv (BSD-3-Clause), groq (Apache-2.0), LangChain
and LangGraph components (MIT), ddgs (MIT), Wikipedia-API (MIT),
sentence-transformers (Apache-2.0), FAISS (MIT), and RDFLib (BSD-3-Clause).
These are a direct-dependency inventory, not a transitive license compliance
opinion; review bundled artifacts and transitive licenses before redistribution.

Risks: mutable upstream dependency resolution; missing Groq credentials;
network-denied live tools; model availability; import-time execution; a local
fixture is not evidence about real providers. Keep the executor allowlisted to
the controlled local service, fail closed on unsupported contracts, and keep the
oracle independent of declared effects. No LLM, embedding download, provider B/C,
registry, substitution planner, or experimental conclusion is introduced.

## Baseline validation

Before changes: all tutorial dependency imports and package consistency passed;
calculator and subprocess arithmetic passed. The existing tools demonstration
failed at external search with proxy HTTP 403. Importing the agent failed because
GROQ_API_KEY was absent. No live tutorial behavior is claimed as verified.
