GC_PROJECT_ID = web-latex-compiler-262817
VERSION = $(shell git rev-parse --abbrev-ref HEAD)

.PHONY: clean
clean:
	@echo "Cleanup unnecessary files"
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

.PHONY: push
push/%:	# web or worker
	@echo "Build docker image and push to GCR"
	@docker build . -t eu.gcr.io/${GC_PROJECT_ID}/$*:${VERSION} --target $* 
	@docker push eu.gcr.io/${GC_PROJECT_ID}/$*:${VERSION}

.PHONY: codestyle
codestyle:
	@echo "Run code style checker"
	@pipenv run ./codestyle.sh

.PHONY: deploy
deploy:
	@make push/worker
	@make push/web
	cd ./terraform && terraform taint google_compute_instance.default
	cd ./terraform && terraform taint google_cloud_run_service.web
	cd ./terraform && terraform apply -auto-approve
