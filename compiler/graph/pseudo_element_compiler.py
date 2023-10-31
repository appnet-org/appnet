# This is a pseudo element compiler supporting
# * For elements existing in the original mrpc repository, the pseudo-compiler
# will copy the source code into the "{gen_dir}{engine_name}" directory

import os

support_list = ["logging", "qos", "null", "ratelimit"]


def pseudo_compile(spec: str, gen_dir: str, backend: str):
    assert backend in ["mrpc"], f"backend {backend} not supported"
    ename = spec.split("/")[-1].split(".")[0]
    assert ename in support_list, f"element {ename} not supported"

    if backend == "mrpc":
        phoenix_dir = os.getenv("PHOENIX_DIR")
        assert phoenix_dir is not None, "environment variable PHOENIX_DIR not set"
        os.system(f"mkdir -p {gen_dir}/{ename}_mrpc/api")
        os.system(
            f"cp -Tr {phoenix_dir}/experimental/mrpc/phoenix-api/policy/{ename} {gen_dir}/{ename}_mrpc/api/{ename}"
        )
        os.system(f"mkdir -p {gen_dir}/{ename}_mrpc/plugin")
        os.system(
            f"cp -Tr {phoenix_dir}/experimental/mrpc/plugin/policy/{ename} {gen_dir}/{ename}_mrpc/plugin/{ename}"
        )
