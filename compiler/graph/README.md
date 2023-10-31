# Graph Compiler

## Limitations

* Container name is hard-coded (only support hotel reservation).
* Service deployment information is currently provided by the user in the specification file (should query the controller instead).
* The graph compiler will generate a globally-unique element name for each element instance, but it requires the element's library name to be identical to the element's specification filename.