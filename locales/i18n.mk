LOCALES_DIR                 := locales/
TRANSLATIONS_DIR            := ${LOCALES_DIR}/translations


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
	sed -ri '2 s/[0-9]{4}/2024-2025/' ${LOCALES_DIR}/${UTIL_NAME}.pot
	sed -i -e '4d;10d;$$ d' ${LOCALES_DIR}/${UTIL_NAME}.pot

translate-update: translate-extract
	pybabel update --input-file ${LOCALES_DIR}/${UTIL_NAME}.pot \
		--update-header-comment \
		--domain ${UTIL_NAME} \
		--ignore-pot-creation-date \
		--output-dir ${TRANSLATIONS_DIR}
	sed -i -e '8d;$$ d' ${TRANSLATIONS_DIR}/en/LC_MESSAGES/${UTIL_NAME}.po
	sed -i -e '8d;$$ d' ${TRANSLATIONS_DIR}/ru/LC_MESSAGES/${UTIL_NAME}.po

translate-compile:
	pybabel compile --directory ${TRANSLATIONS_DIR} \
		--domain ${UTIL_NAME}

translate-init:
	@if [ -n "$(LANGUAGE)" ]; then \
		pybabel init --input-file ${LOCALES_DIR}/${UTIL_NAME}.pot \
			--output-dir ${TRANSLATIONS_DIR} \
			--domain ${UTIL_NAME} \
			--locale ${LANGUAGE}; \
	else \
		echo "You should provide the 'LANGUAGE' variable for initializing translation."; \
		exit 1; \
	fi
