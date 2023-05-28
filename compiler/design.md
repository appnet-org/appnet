# Compiler Design

## Naive Implementation

We translate each SQL statement to corresponding Rust code.

### todos

- For constructors, currently we use clone(copy) rather than move(reference), which is not efficient.
- For select, we currently consider the two type in Rust is "compatible" and use a `new` constructor.  But for star(select *), since we don't have the column information in AST,  we currently assume input and output are of same type, and use `.clone` directly. Maybe we need some context to determine whether to use `.into` and add the impl for `Into` trait. 
    - Maybe transform the `*` to a list of column names, and use the same method as `select`?    
- Do we need special treatment for output?
## Logging



### SQL Code 

