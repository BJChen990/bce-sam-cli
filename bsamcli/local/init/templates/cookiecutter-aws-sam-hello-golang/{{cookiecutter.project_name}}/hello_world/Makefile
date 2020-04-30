.PHONY: deps clean build

deps:
	go mod tidy

clean: 
	rm -rf ./index
	
build:
	GOOS=linux GOARCH=amd64 go build -o index