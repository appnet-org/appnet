# QuickStart

This guide will walk you through:

- Deploying a simple echo application.
- Running a simple element chain on the frontend to server communication edge.


## Echo Application
The Echo application is a simple application developed using Go and gRPC. The client sends messages to the frontend, which then relays the messages to the Echo server. Finally, the server echoes the request back to the frontend. The architecture is as follows:

[TODO]

### Deploy 
Run the following command to deploy the echo application.
```bash
kubectl apply -f samples/echo/echo.yaml
```

Then, verify the deployment:
```bash
user@h1:~/adn-controller$ kubectl get pods
NAME                             READY   STATUS    RESTARTS   AGE
echo-frontend-6f9cf6db74-tjvfc   2/2     Running   0          14m
echo-server-594b4797d-9t6gn      2/2     Running   0          14m
user@h1:~/adn-controller$ curl http://10.96.88.88/hello_world
Echo request finished! Length of the request is 12
```

## Example element chain

We will deploy the following chain to the frontend to server edge.

[TODO]

### Run the ADN controller
First, you need to run the ADN controller
```bash
make run
```

For this element chain the ADN configurations is as follows:
```yaml
# TODO
```

Next, in a seperate terminal, apply this yaml file:
```bash
kubectl apply -f config/samples/echo/sample_echo.yaml
```

You should some logs in the controller indicating it is reconciling, which should finish in a few minutes. 

Finally, you can see elements are running:
```bash
# TODO
```

# Clean Up
```bash
kubectl delete all,pvc,pv,envoyfilters,adnconfigs --all
```

# Next Steps
[TODO]

Learn the ADN grammar.
How does ADN optimize chain.