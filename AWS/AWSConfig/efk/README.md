# EFK Stack Installation on EKS

1. The contents of the [config](config) directory are needed for this install.
2. Create a service account for tiller and apply the rbac yaml:

```
kubectl create serviceaccount tiller --namespace kube-system
kubectl apply -f rbac-config.yaml
helm init --service-account tiller
```

3. Install the chart:

```
helm install --name ccp-efk -f overrides.yaml <path/to/chart>/ccp-efk-0.3.3.tgz
```

4. wait for pods to come up

```
kubectl get pods
```

5. Open port-forward to kibana

```
kubectl port-forward $(kubectl get po -l app=kibana -o name) 5601:5601
```
6. Point your browser to the kibana dashboard at http://localhost:5601