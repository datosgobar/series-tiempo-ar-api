docs: ## generate Sphinx HTML documentation, including API docs
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
