package main

import (
	"flag"

	"github.com/baidubce/bce-cfc-go/pkg/cfc"
)

func main() {
	flag.Parse()
	// 进入框架，处理函数事件
	cfc.Main()
}
