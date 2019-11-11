.PHONY: deps clean build

deps:
	go mod tidy

clean: 
	rm -rf ./hello_world
	
build:
	GOOS=linux GOARCH=amd64 go build -o hello_world