from dinajpur_engine import DinajpurUnifiedEngine

e = DinajpurUnifiedEngine()
# Let's inspect raw_resp inside _query_archive_api
res = e._query_archive_api(exam='hsc', year='2025', board='tec', roll='208579', reg='1502385808')
print("Keys:", list(res.keys()))
print("Msg:", repr(res.get('msg')))
print("Raw res:", res)
