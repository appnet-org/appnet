### Deploy services

run `kubectl apply -Rf hotel_reservation.yaml`
and wait for `kubectl get pods` to show all pods with status `Running`.

### Curl requests
```bash
# Search
curl "http://10.96.88.88:5000/hotels?inDate=2015-04-10&outDate=2015-04-11&lat=38.0235&lon=-122.095"
curl "http://10.96.88.88:5000/recommendations?require=rate&lat=38.0235&lon=-122.095"
curl "http://10.96.88.88:5000/user?username=Cornell_15&password=123654"
curl "http://10.96.88.88:5000/reservation?inDate=2015-04-19&outDate=2015-04-24&lat=nil&lon=nil&hotelId=9&customerName=Cornell_1&username=Cornell_1&password=1111111111&number=1"
```

### wrk & wrk2
```bash
./wrk/wrk -t 1 -c 1 -d 30s http://10.96.88.88:5000 -s config/samples/hotel/hotel.lua -L
./wrk2/wrk -t 10 -c 100 http://10.96.88.88:5000/hotels?inDate=2015-04-10&outDate=2015-04-11&lat=38.0235&lon=-122.095 -d 60s -R 2000
```


### Destroy services
```bash
kubectl delete envoyfilters,pvc,pv,all --all
```