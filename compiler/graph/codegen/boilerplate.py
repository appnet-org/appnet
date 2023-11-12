attach_toml = """
addon_engine = "{current}"
tx_channels_replacements = [
    [
        "{req_prev}",
        "{current}",
        0,
        0,
    ],
    [
        "{current}",
        "{req_next}",
        0,
        0,
    ],
]
rx_channels_replacements = [
    [
        "{res_next}",
        "{current}",
        0,
        0,
    ],
    [
        "{current}",
        "{res_prev}",
        0,
        0,
    ],
]
group = {Group}
op = "attach"
"""

detach_toml = """
addon_engine = "{current}"
tx_channels_replacements = [["{req_prev}", "{req_next}", 0, 0]]
rx_channels_replacements = [["{res_next}Engine", "{res_prev}Engine", 0, 0]]
op = "detach"

"""
