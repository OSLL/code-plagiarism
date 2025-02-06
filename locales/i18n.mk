LOCALES_DIR                 := locales/


translate-help:
	@echo "Translate:"
	@echo "  translate-extract      Extracts all lines that need to be translated;"
	@echo "  translate-update       Updates all po files with new code changes;"
	@echo "  translate-compile      Compile message catalogs to MO files;"
	@echo "  translate-init         Initializing a new language for translation;"
	@echo "      LANGUAGE=..."
	@echo "  translate-help         Displays information about available translation targets."
	@echo

translate-extract:
	pybabel extract --mapping-file ${LOCALES_DIR}/babel.cfg \
		--keywords _ \
		--version ${UTIL_VERSION} \
		--project ${UTIL_NAME} \
		--charset "utf-8" \
		--copyright-holder "Codeplag Development Team" \
		--last-translator "Artyom Semidolin" \
		--output-file ${LOCALES_DIR}/${UTIL_NAME}.pot .

translate-update: translate-extract
	pybabel update --input-file ${LOCALES_DIR}/${UTIL_NAME}.pot \
		--update-header-comment \
		--domain ${UTIL_NAME} \
		--ignore-pot-creation-date \
		--output-dir ${LOCALES_DIR}/translations

translate-compile:
	pybabel compile --directory ${LOCALES_DIR}/translations \
		--domain ${UTIL_NAME}

translate-init:
	@if [ -n "$(LANGUAGE)" ]; then \
		pybabel init --input-file ${LOCALES_DIR}/${UTIL_NAME}.pot \
			--output-dir ${LOCALES_DIR}/translations \
			--domain ${UTIL_NAME} \
			--locale ${LANGUAGE}; \
	else \
		echo "You should provide the 'LANGUAGE' variable for initializing translation."; \
		exit 1; \
	fi
