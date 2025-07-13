# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= poetry run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets for documentation workflow
clean-build:
	@echo "Removing build directory..."
	@Remove-Item -Recurse -Force "$(BUILDDIR)" -ErrorAction SilentlyContinue
	@echo "Clean complete."

html-clean: clean-build html
	@echo "HTML documentation built successfully."

linkcheck:
	@echo "Checking external links..."
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)
	@echo "Link check complete."

serve:
	@echo "Starting local documentation server..."
	@cd "$(BUILDDIR)/html" && python -m http.server 8000

validate:
	@echo "Validating documentation..."
	@$(SPHINXBUILD) -W -b html "$(SOURCEDIR)" "$(BUILDDIR)/validate" $(SPHINXOPTS)
	@echo "Validation complete (warnings treated as errors)."

# Quick development build (warnings allowed)
dev:
	@echo "Building documentation for development..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Development build complete. Open build/html/index.html to view."

# Production build (fail on warnings)
prod:
	@echo "Building documentation for production..."
	@$(SPHINXBUILD) -W -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "Production build complete."

# Build all formats
all: html linkcheck
	@echo "All documentation formats built successfully."

.PHONY: clean-build html-clean linkcheck serve validate dev prod all
