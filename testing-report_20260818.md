\# TODAY is 2026-08-17

This report combines the latest operator testing from \`origin/gamma` with the

local verification work completed on 2026-08-17/18.

\## Document Changes / Requested Work

\- Add a date/time insert button to the NchantdOfficeScript toolbar with the 

  \`Ctrl+D` hotkey.

\- Sort node names beginning with \`_` to the top.

\- Refresh the ToolBox after node deletion.

\- After node deletion, navigate to the previous node; fall back to a sibling,

  then to the parent.

\- Identify and reduce bottlenecks in new-document creation.

\- Fix NchantdOfficeMatrix so internally stored matrix values persist and

  restore when no external file is open.

\- Disable the NchantdOfficeMatrix toolbar formula entry until 0.0.3.

\- Fix NchantdOfficeScript external documents so Save writes back to the

  external file. Internal script saving already works and must remain unchanged.

\## Journal Scope Clarification

\- Full journal text save/restore and journal retention already work. Do not

  change those paths.

\- Remaining journal work is parsing, including PII parsing and redaction

  integration.

\- Pycurity already provides PII tools. NchantdOffice should integrate those

  tools; any expansion of base PII functionality belongs in pycurity.

\## Newly Reported Bug

\`bootstrap_app_user` fails because nchantrs \`NchantdUser.get_password` calls a

missing \`verify_password` method; the available method appears to be `

verify_pword`. The complete operator traceback is preserved in git history at `

origin/gamma` commit \`3799b3f`.

\## Verification State

\- Qt collection guard: 2 passed.

\- Palette extraction: 30 upstream tests passed; 9 downstream tests passed.

\- Chart native-crash regression: 16 tests passed.

\- Max-node cap + redirect: 35 tests passed.

\- Journal tab-focus restore regression: 7 tests passed. This does not change

  journal storage or retention.

\- User-tier compatibility: 7 tests passed.

\- Pyof worker native-abort guards: 2 tests passed.

The latest safe suite before this report consolidation reached 833 passed with

19 failures. Those failure clusters were subsequently addressed, but a final

full-suite count must be rerun after the merge.

