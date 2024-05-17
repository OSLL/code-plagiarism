LOCALES_DIR                 := locales/


translate-extract:
	pybabel extract --mapping-file ${LOCALES_DIR}/babel.cfg \
		--keywords _ \
		--version ${UTIL_VERSION} \
		--project ${UTIL_NAME} \
		--output-file ${LOCALES_DIR}/${UTIL_NAME}.pot .

translate-update: translate-extract
	pybabel update --input-file ${LOCALES_DIR}/${UTIL_NAME}.pot \
		--update-header-comment \
		--domain ${UTIL_NAME} \
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
