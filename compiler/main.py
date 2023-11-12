import argparse
import os

from compiler.graph import graph_base_dir
from compiler.graph.backend import scriptgen
from compiler.graph.frontend import GCParser
from compiler.graph.pseudo_element_compiler import pseudo_compile

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--spec_path", help="User specification file", type=str, required=True
    )
    parser.add_argument("--verbose", help="Print Debug info", action="store_true")
    parser.add_argument("--pseudo_element", action="store_true")
    parser.add_argument("--backend", type=str, required=True, choices=["mrpc"])
    parser.add_argument(
        "--mrpc_dir",
        type=str,
        default=os.path.join(os.getenv("HOME"), "phoenix/experimental/mrpc"),
    )
    parser.add_argument("--dry_run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        os.environ["DRY_RUN"] = "1"

    parser = GCParser()
    graphirs, service_pos = parser.parse(args.spec_path)

    compiled_spec = set()
    for gir in graphirs.values():
        gir.optimize(args.pseudo_element)
        for element in gir.elements["req_client"] + gir.elements["req_server"]:
            for spec in element.spec:
                if spec not in compiled_spec:
                    if args.pseudo_element:
                        pseudo_compile(
                            spec, os.path.join(graph_base_dir, "gen"), args.backend
                        )
                    else:
                        raise NotImplementedError("element compiler not implemented")
                compiled_spec.add(spec)

    scriptgen(graphirs, args.backend, service_pos)

    if args.verbose:
        print("=======================================")
        print("Summary:")
        for gir in graphirs.values():
            print(gir)
