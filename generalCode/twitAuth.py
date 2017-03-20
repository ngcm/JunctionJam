import twitter


def getAPI():
	api = twitter.Api(
        consumer_key        = '9FMZFKB9j1iFYm7TdaRCt2se7',
        consumer_secret     = 'pOl3VsfcV9DeI8za9bq81SGdJElmwl22iWvtSYzJZpjnzjoB3T',
        access_token_key    = '832234517855399937-lDYcVSYqhOXUUDyVFKxL3xwE369EwX7',
        access_token_secret = 'h3TFKem3kzvHEYfCxniBRV9juDQLFZKK2kkT523BHfbG2'
        )
	return api
