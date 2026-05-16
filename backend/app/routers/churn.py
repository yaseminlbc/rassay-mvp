# This router has been retired.
#
# The /clients/{id}/risk and /clients/{id}/xai endpoints it contained had two
# problems that made them unreachable:
#   1. The router prefix "/api/v1/clients" + the include_router prefix "/api/v1"
#      in main.py produced a double-prefixed URL: /api/v1/api/v1/clients/...
#   2. path parameters were typed as `int`, incompatible with string company_ids.
#
# Both capabilities now live in the correct location:
#   GET /api/v1/customers/{company_id}      → app/customers.py (risk_score included)
#   GET /api/v1/customers/{company_id}/xai  → app/customers.py → xai_service.py
