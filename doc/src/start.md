# QuickStart

This guide will walk you through:

- Deploying a simple echo application.
- Running a simple element chain on the frontend to server communication edge.


## Echo Application
The Echo application is a simple application developed using Go and gRPC. The client sends messages to the frontend, which then relays the messages to the Echo server. Finally, the server echoes the request back to the frontend. The architecture is as follows:

![Echo Application](./figures/echo-app.png "Echo Application")

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

![Example Chain](./figures/echo-chain.png "Example Chain")

### Run the ADN controller
First, you need to run the ADN controller
```bash
make run
```

For this element chain the ADN configurations is as follows:
```yaml
apiVersion: api.core.adn.io/v1
kind: Adnconfig
metadata:
  name: sample-echo # Name of the Adnconfig
spec:
  appName: echo # Name of the application
  clientService: frontend # Name of the client service (must be a valid service in the same namespace as the Adnconfig)
  serverService: server # Name of the server service (must be a valid service in the same namespace as the Adnconfig)
  method: echo # Name of the RPC method (defined in the proto file)
  appManifestFile: /users/xzhu/adn-controller/config/samples/echo/echo.yaml # Path to the application manifest file
  clientChain:
    - name: fault # Name of the first element in the client chain
      file: /users/xzhu/adn-controller/config/samples/echo/fault.adn # Path to the fault injection element file
      parameters:
        probability: "0.02" # Probability of fault injection
    - name: logging # Name of the second element in the client chain
      file: /users/xzhu/adn-controller/config/samples/echo/logging.adn # Path to the logging element file
  serverChain:
    - name: firwall # Name of the first element in the server chain
      file: /users/xzhu/adn-controller/config/samples/echo/firewall.adn # Path to the firewall element file
      parameters:
        body: apple # Key and value to be used in the firewall element
  anyChain:
    - name: metrics # Name of the first element in the any(unconstraint) chain
      file: /users/xzhu/adn-controller/config/samples/echo/metrics.adn # Path to the metrics element file
  proto: /users/xzhu/adn-controller/config/samples/echo/echo.proto # Path to the protobuf definition of client service to server service communication
```

Next, in a seperate terminal, apply this yaml file:
```bash
kubectl apply -f config/samples/echo/sample_echo.yaml
```

You should some logs in the controller indicating it is reconciling, which should finish in a few minutes. 

Finally, test the installation by running:
```bash
# TODO
```

# Clean Up

When you're finish experimenting with the echo application, uninstall and clean it up using the following command:
```bash
kubectl delete all,pvc,pv,envoyfilters,adnconfigs --all
```

# Next Steps
[TODO]

Learn the ADN grammar.
How does ADN optimize chain.