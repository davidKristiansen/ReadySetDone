.PHONY: docs clean-docs  completions install-completions clean-completions

COMPLETION_DIR := completions
ZSH_COMPLETION_DIR := $(if $(ZDOTDIR),$(ZDOTDIR)/.zfunc,$(HOME)/.zfunc)

docs:
	uv pip install -r docs/requirements.txt || true
	uv run sphinx-build -b html docs/ docs/_build/html

clean-docs:
	rm -rf docs/_build

completions:
	mkdir -p $(COMPLETION_DIR)
	register-python-argcomplete rsd > $(COMPLETION_DIR)/_rsd
	register-python-argcomplete rsdd > $(COMPLETION_DIR)/_rsdd

install-completions: completions
	mkdir -p $(ZSH_COMPLETION_DIR)
	cp $(COMPLETION_DIR)/_rsd $(ZSH_COMPLETION_DIR)/
	cp $(COMPLETION_DIR)/_rsdd $(ZSH_COMPLETION_DIR)/
	@echo "✅ Completion files installed to $(ZSH_COMPLETION_DIR)"
	@echo "🔁 Add this to your shell config if not already present:"
	@echo ""
	@echo "    fpath+=($(ZSH_COMPLETION_DIR))"
	@echo "    autoload -Uz compinit && compinit"
	@echo ""
	@echo "💡 Then restart your shell or run: exec zsh"

clean-completions:
	rm -rf $(COMPLETION_DIR)
