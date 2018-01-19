.PHONY: install
## Install the prerequisites
install:
	python3 setup.py develop

.PHONY: compile
## Perform the whole compilation process
compile: clean flatten merge schemas

.PHONY: clean
## Remove the build folder
clean:
	@rm -rf build

.PHONY: flatten
## Flatten the ref links in the specifications
flatten: specs-sources
	scripts/flatten.sh build/bo specs-sources/api .bo
	scripts/flatten.sh build/pro specs-sources/api .pro
	scripts/flatten.sh build/client specs-sources/api

specs-sources:
	@if [ ! -e ../specs-sources ]; then echo "No `specs-sources` folder find in parent directory"; exit 1; fi
	ln -s ../specs-sources specs-sources

.PHONY: merge
## Merge specs into single files
merge:
	python3 -m swag.merger build/client > build/client.yml
	python3 -m swag.merger build/bo > build/bo.yml
	python3 -m swag.merger build/pro > build/pro.yml

.PHONY: schemas
## Generate the rspec schemas
schemas:
	@mkdir -p build/schemas
	python3 -m swag.rspec build/client build/bo build/pro --destination build/schemas/

.PHONY: container
## Build and push the container
container:
	docker build --pull -t classheroes/specs-compiler:latest .
	docker push classheroes/specs-compiler:latest

.PHONY: help
# taken from this gist https://gist.github.com/rcmachado/af3db315e31383502660
## Show this help message.
help:
	$(info Usage: make [target...])
	$(info Available targets)
	@awk '/^[a-zA-Z\-\_0-9]+:/ {                    \
		nb = sub( /^## /, "", helpMsg );              \
		if(nb == 0) {                                 \
			helpMsg = $$0;                              \
			nb = sub( /^[^:]*:.* ## /, "", helpMsg );   \
		}                                             \
		if (nb)                                       \
			print  $$1 "\t" helpMsg;                    \
	}                                               \
	{ helpMsg = $$0 }'                              \
	$(MAKEFILE_LIST) | column -ts $$'\t' |          \
	grep --color '^[^ ]*'

.DEFAULT_GOAL := help
