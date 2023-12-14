package fault

import (
	"google.golang.org/grpc"
)

var (
	defaultOptions = &options{
		abortProbability: -1, // disabled
		abortedCount:     0,
	}
)

func WithAbortProbability(probability float64) CallOption {
	if probability < 0 || probability > 1 {
		panic("probability must be between 0 and 1")
	}

	return CallOption{applyFunc: func(o *options) {
		o.abortProbability = probability
	}}
}

type options struct {
	abortProbability float64
	abortedCount     int32
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

func filterCallOptions(callOptions []grpc.CallOption) (grpcOptions []grpc.CallOption, faultOptions []CallOption) {
	for _, opt := range callOptions {
		if co, ok := opt.(CallOption); ok {
			faultOptions = append(faultOptions, co)
		} else {
			grpcOptions = append(grpcOptions, opt)
		}
	}
	return grpcOptions, faultOptions
}