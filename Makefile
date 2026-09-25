SHELL = bash

.PHONY: docs servedocs

# La documentación es un sitio Astro Starlight (src/content/docs). Se publica con GitHub Actions al pushear a master.
servedocs:
	npm run dev

docs:
	npm run build

# se puede hacer `make test-queries num=200` para hacer un numero de queries
test-queries:
	python scripts/api_queries.py $(num) $(url)

