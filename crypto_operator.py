import kopf
import crypto_tools


@kopf.on.create('crypto.tools', 'v1', 'cryptovaluecalculator')
@kopf.timer('crypto.tools', 'v1', 'cryptovaluecalculator', interval=60.0)
def process_crypto_crd(spec, patch, logger, **kwargs):
    """ When a CryptoValueCalculator resource is created, 
        calculate the value based on coin's market price and amount specified. 
        Then configure an annotation on the resource with the calculated value. Repeat every 60s. """
    value = crypto_tools.get_value(spec['coin'], spec['amount'])
    patch.metadata.annotations['value'] = "$" + str(value)
