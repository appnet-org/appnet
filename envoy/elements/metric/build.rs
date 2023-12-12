// Specify the location of proto files here
const PROTO: &str = "../../ping_pb/ping.proto";
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed={PROTO}");
    prost_build::compile_protos(&[PROTO], &["../../ping_pb"])?;
    Ok(())
}
