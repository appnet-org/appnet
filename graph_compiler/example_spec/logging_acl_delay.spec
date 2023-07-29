# declarations

[
    delay, config=(prob=0.1, delay_ms=100),
    property=(drop=True, state=True, record=False)
]

[
    acl, config=(),
    property=(drop=True, state=False, record=False, read=[payload])
]

[
    logging, config=(),
    property=(drop=False, state=False, record=True, read=[src, dst, type])
]

# orders

logging -> acl;
acl -> delay;
