### Deploy services

run `kubectl apply -f echo.yaml`
and wait for `kubectl get pods` to show all pods with status `Running`.

### Curl requests
```bash
# Search
curl http://10.96.88.88?key=test
```

### wrk & wrk2
```bash
./wrk/wrk -t 1 -c 1 -d 30s http://10.96.88.88?key=hello -L
./wrk2/wrk -t 10 -c 100 http://10.96.88.88?key=hello -d 60s -R 2000
```


### Destroy services
```bash
kubectl delete envoyfilters,pvc,pv,all --all
```