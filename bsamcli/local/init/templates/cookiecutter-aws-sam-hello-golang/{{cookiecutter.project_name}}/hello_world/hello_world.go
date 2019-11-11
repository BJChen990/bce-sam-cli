package main

import (
	"io"
	"log"

	"github.com/baidubce/bce-cfc-go/pkg/cfc"
)

// HelloWorldHandler xxx
type HelloWorldHandler struct {
}

func init() {
	// 注册handler
	cfc.RegisterNamedHandler("hello_handler", &HelloWorldHandler{})
}

// Handle xxx
func (h *HelloWorldHandler) Handle(input io.Reader, output io.Writer, context cfc.InvokeContext) error {
	log.Printf("reqid=%s, brn=%s, name=%s, ver=%s, mem=%d\n",
		context.GetRequestID(), context.GetFunctionBrn(), context.GetFunctionName(),
		context.GetFunctionVersion(), context.GetMemoryLimitMB())

	_, err := io.Copy(output, input)
	return err
}
