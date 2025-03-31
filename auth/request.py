import requests

# Sample request
response = requests.get("https://chess-demo.mihneaspiridon.workers.dev/",
                        headers={
                            "Action": "Bind",
                            "Token": "--TwY2WWVgrqA8cXMD-iTaOmyHufYqdMaPxaDNqXs-g" # This is a token in the tokens.json file
                        })

print(response)