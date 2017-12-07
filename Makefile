docs: ## generate Sphinx HTML documentation, including API docs
	mkdocs build
	$(BROWSER) site/index.html

servedocs:
	mkdocs serve

doctoc: ## generate table of contents, doctoc command line tool required
        ## https://github.com/thlorenz/doctoc
	doctoc --title " " docs/api_reference.md
	bash fix_github_links.sh docs/api_reference.md
	doctoc --title " " docs/quick_start.md
	bash fix_github_links.sh docs/quick_start.md
