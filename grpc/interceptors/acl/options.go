package acl

import (
	"google.golang.org/grpc"
)

var (
	defaultOptions = &options{
		content: "null", // disabled
		blockedCount:     0,
	}
)

func WithContent(content string) CallOption {
	return CallOption{applyFunc: func(o *options) {
		o.content = content
	}}
}

type options struct {
	content string
	blockedCount int32
}

type CallOption struct {
	grpc.EmptyCallOption // make sure we implement private after() and before() fields so we don't panic.
	applyFunc            func(opt *options)
}

func reuseOrNewWithCallOptions(opt *options, callOptions []CallOption) *options {
	if len(callOptions) == 0 {
		return opt
	}
	optCopy := &options{}
	*optCopy = *opt
	for _, f := range callOptions {
		f.applyFunc(optCopy)
	}
	return optCopy
}

func filterCallOptions(callOptions []grpc.CallOption) (grpcOptions []grpc.CallOption, aclOptions []CallOption) {
	for _, opt := range callOptions {
		if co, ok := opt.(CallOption); ok {
			aclOptions = append(aclOptions, co)
		} else {
			grpcOptions = append(grpcOptions, opt)
		}
	}
	return grpcOptions, aclOptions
}