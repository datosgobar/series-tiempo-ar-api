SHELL = bash

.PHONY: docs servedocs doctoc

servedocs:
	mkdocs serve

mkdocsdocs:
	mkdocs build
	rsync -vau --remove-source-files site/ docs/
	rm -rf site

serveswaggerdocs:
	echo "Browse to http://localhost:8000/docs/open-api/"
	python -m SimpleHTTPServer 8000

swaggerdocs:
	wget https://github.com/swagger-api/swagger-ui/archive/master.zip -O temp.zip; unzip -jo temp.zip 'swagger-ui-master/dist/*' -d docs/open-api/; rm temp.zip
	sed -i.bak "s/url: \".*\"/url: \"\.\/swagger\.yml\", validatorUrl: null/g" docs/open_api/index.html
	echo ".download-url-wrapper { display: none!important; }" >> docs/open_api/swagger-ui.css
	rm -f docs/open_api/index.html.bak

docs: mkdocsdocs swaggerdocs

doctoc: ## generate table of contents, doctoc command line tool required
        ## https://github.com/thlorenz/doctoc
	doctoc --github --title " " docs/quick-start.md
	bash fix_github_links.sh docs/quick-start.md
	doctoc --github --title " " docs/additional-parameters.md
	bash fix_github_links.sh docs/additional-parameters.md
	doctoc --github --title " " docs/reference/api-reference.md
	bash fix_github_links.sh docs/reference/api-reference.md
	doctoc --github --title " " docs/reference/search-reference.md
	bash fix_github_links.sh docs/reference/search-reference.md
	doctoc --github --title " " docs/spreadsheet-integration.md
	bash fix_github_links.sh docs/spreadsheet-integration.md
	doctoc --github --title " " docs/python-usage.md
	bash fix_github_links.sh docs/python-usage.md



# se puede hacer `make test-queries num=200` para hacer un numero de queries
test-queries:
	python scripts/api_queries.py $(num) $(url)
