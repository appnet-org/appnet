# Graph Compiler

## Preparations

> Please make sure that you clone the adn repository under `$HOME`.
> ```bash
> git clone https://github.com/app-defined-networks ~/app-defined-networks
> ```

Clone the multithreaded version of phoenix repository at `$HOME`.

```bash
git clone https://github.com/kristoff-starling/phoenix --recursive -b multi ~/phoenix
```

Install necessary dependencies and set environment variables.

```bash
source ~/app-defined-networks/compiler/install.sh
```

## Usage

```bash
python3 ~/app_defined_networks/compiler/main.py [--verbose] [--pseudo_element] [--spec path_to_spec] [--backend BACKEND] [--dry_run]

# An example
python3 ~/app-defined-networks/compiler/main.py --verbose --pseudo_element --spec ~/app-defined-networks/compiler/graph/examples/demo.yml --backend mrpc --dry_run
```
* `--verbose`: if used, request graphs (i.e., element chains) on each edge will be printed on the terminal.
* `--pseudo_element`: use the pseudo element compiler provided by the graph compiler, which reads element properties in `element/property/` and copy existing implementations from the phoenix local repository.
* `--spec path_to_spec`: path to the user specification file.
* `--backend BACKEND`: currently, only mrpc backend is supported.
* `--dry_run`: if used, the compiler will not send remote commands into the container.

The compiler will automatically install engines on all the machines and generate `attach_all.sh` and `detach_all.sh` in `graph/gen`.

## Deployment

### Mrpc

Fire up phoenixos and hotel applications.

```bash
# in all worker machines
docker pull kristoffstarling/hotel-service:multi

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

After running the compiler, use `attach_all.sh` and `detach_all.sh` to attach/detach elements.

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
