# building a Kubernetes operator with Python...

As part of my day job, wrangling k8s clusters, I came across this Python project: 

Kubernetes Operator Pythonic Framework (kopf)
https://github.com/nolar/kopf

As a learning exercise, I decided to build a simple operator around a new custom k8s resource that I'm calling a CryptoValueCalculator or CVC for short. It's a simple, almost a silly idea, but it was fun to build.

## Custom resource definitions...
While not required, I wanted my operator to interact with a custom k8s resource. I had an idea for a resource that would have a specific crypto-currency type and a hypothetical amount that someone may be holding of that currency.

For example:
```apiVersion: crypto.tools/v1
kind: CryptoValueCalculator
metadata:
  name: bitcoin-stash
spec:
  coin: bitcoin
  amount: 0.0023
```
The role of the operator would be to "watch" for these resources and run a calculation using whatever the current market price of the particular coin is to determine the value held.

To enable this new resource type, I needed a definition. In Kubernetes, these are literally called custom resource definitions or CRDs. Below is the CRD I wrote to define my CryptoValueCalculator resource:

```
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: cryptovaluecalculators.crypto.tools
spec:
  scope: Namespaced
  group: crypto.tools
  names:
    kind: CryptoValueCalculator
    plural: cryptovaluecalculators
    singular: cryptovaluecalculator
    shortNames:
      - cvc
      - cvcs
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              x-kubernetes-preserve-unknown-fields: true
              properties:
                coin:
                  type: string
                  description: The specific crypto coin.
                  enum:
                  - bitcoin
                  - ethereum
                  - dogecoin
                  - shiba-inu
                amount:
                  type: number
                  description: The amount of specified crypto currency.
              required:
               - coin
               - amount
            status:
              type: object
              x-kubernetes-preserve-unknown-fields: true
          required:
            - spec
      additionalPrinterColumns:
        - name: Coin
          type: string
          priority: 0
          jsonPath: .spec.coin
          description: The specific crypto coin.
        - name: Amount
          type: number
          priority: 0
          jsonPath: .spec.amount
          description: The amount of specified crypto currency.
        - name: Value
          type: string
          priority: 0
          jsonPath: .metadata.annotations.value
          description: The current value of specified crypto currency based on given amount and market value in USD.
```
## Writing the operator...
The kopf framework and provided documentation made this part super simple. (It also helped that my operator logic is very simple). With the CRD defined, all I needed was a few lines of Python to calculate the crypto-currency value when an implementation of my CRD is created. I also used the timer feature in kopf so the value will automatically be re-calculated on a schedule.

I'm using the CoinGecko API for my price information:
 https://www.coingecko.com/en/api/documentation

## Running the operator...
I did my development and testing with a kind cluster. Kind is a way of running Kubernetes clusters on top of Docker and it's perfect for this sort of use-case: https://kind.sigs.k8s.io/

With the kind cluster up and running, the CRD needs to be applied:

`kubectl apply -f crd.yaml`

Next, kopf and the Python environment need to be configured. I'm using Python 3.10.0 w/ pyenv. To install kopf:
 
 `pip install kopf`

Now the operator code can be executed:

`kopf run crypto_operator.py`

To test the operator, I have some example CVCs in /examples:

`kubectl apply -f examples/bitcoin.yaml`

`kubectl apply -f examples/ethereum.yaml`

We can then see these resources and the calculated 'value' field:

```
 ~/development/space_debris/ kubectl get cvc
NAME               COIN       AMOUNT   VALUE
bitcoin-stash      bitcoin    0.0023   $94.8106
lump-of-ethereum   ethereum   1.47     $4550.7672
```

## future improvements...
At some point, the next step for this experiment would be to put the Python operator code into a Docker image that could be deployed into a Kubernetes cluster along with the necessary RBAC.

Maybe I'd add another printer column field to the CRD with logic to calculate the price change from the last update... 

There are all sorts of features that could be tacked onto this etc... maybe re-write the operator in golang to be more Kubernetes-native?