# Graph Compiler

## Usage

Install the multithreaded version of Mrpc hotel-reservation application.

```bash
# in $HOME
git clone https://github.com/kristoff-starling/phoenix -b multi
# in all worker machines
docker pull kristoffstarling/hotel-service:multi
```

Fire up phoenixos and hotel applications.

```bash
# in $HOME/phoenix/eval/hotel-bench
# By default, the services are deployed at
# Frontend - h2
# Geo      - h3
# Profile  - h4
# Rate     - h5
# Search   - h6
./start_container
./start_phoenix
# in another terminal
./start_service
```

Install necessary dependencies and environment variables.

```bash
# in compiler/
. ./install.sh
```

Run the compiler.

```bash
# in compiler/
python3 main.py [--verbose] [--pseudo_element] [--spec path_to_spec] [--backend BACKEND]
```
* `--verbose`: makes the compiler more chatty.
* `--pseudo_element`: use the pseudo element compiler provided by the graph compiler, which reads element properties in `element/property/` and copy existing implementations from the phoenix local repository.
* `--spec path_to_spec`: if not specified, `example_spec/dummy.yml` will be used by default.
* `--backend BACKEND`: if not specified, the graph compiler generates mrpc scripts by default.

The compiler will automatically install engines on all the machines and generate an `attach_all.sh` and `detach_all.sh` in `graph/gen`.

```bash
chmod +x graph/attach_all.sh
chmod +x graph/detach_all.sh
./attach_all.sh  # attach all engines
./detach_all.sh  # detach all engines
```

## Limitations

* Container name is hard-coded (only support hotel reservation).
* Service deployment information is currently provided by the user in the specification file (should query the controller instead).
* The graph compiler will generate a globally-unique element name for each element instance, but it requires the element's library name to be identical to the element's specification filename.
