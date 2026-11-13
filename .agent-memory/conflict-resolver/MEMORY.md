# Conflict Resolver Memory
- Scope: only conflicted hunks handed over by the Orchestrator.
- Known hotspot: `engine/dashboard_generator.py` is a single ~2.4k-line f-string — conflicts there are usually in CSS/HTML blocks; keep `{{ }}` escaping intact.
