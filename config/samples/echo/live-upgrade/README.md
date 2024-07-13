```bash
sed -i 's|<APPNET_DIR_PATH>|'"$(pwd)"'|g' config/samples/echo/live-upgrade/sample_echo_sidecar_v1.yaml
sed -i 's|<APPNET_DIR_PATH>|'"$(pwd)"'|g' config/samples/echo/live-upgrade/sample_echo_sidecar_v2.yaml

k apply -f config/samples/echo/live-upgrade/sample_echo_sidecar_v1.yaml
k apply -f config/samples/echo/live-upgrade/sample_echo_sidecar_v2.yaml
```