SHELL = bash

.PHONY: docs servedocs doctoc

docs:
	mkdocs build
	$(BROWSER) site/index.html

servedocs:
	mkdocs serve

doctoc: ## generate table of contents, doctoc command line tool required
        ## https://github.com/thlorenz/doctoc
	doctoc --github --title " " docs/api_reference.md
	bash fix_github_links.sh docs/api_reference.md
	doctoc --github --title " " docs/quick_start.md
	bash fix_github_links.sh docs/quick_start.md
	doctoc --github --title " " docs/spreadsheet_integration.md
	bash fix_github_links.sh docs/spreadsheet_integration.md

swaggerdocs:
	wget https://github.com/swagger-api/swagger-ui/archive/master.zip -O temp.zip; unzip -jo temp.zip 'swagger-ui-master/dist/*' -d docs/; rm temp.zip
	sed -i.bak "s/url: \".*\"/url: \"\.\/swagger\.yml\"/g" docs/index.html
	echo ".download-url-wrapper { display: none!important; }" >> docs/swagger-ui.css
	rm -f docs/index.html.bak

serveswaggerdocs:
	echo "Browse to http://localhost:8000/docs/swagger/"
	python -m SimpleHTTPServer 8000	
