# Asset Manager

### Starting the Docker Container

On your docker machine run:
`sudo docker run -p 5000:5000 -d --rm --name asset_manager sprutner/asset_manager:latest`

The server will now be reachable at http://<ip of docker server>:5000
If you're running this locally, it will be http://localhost:5000


## Adding a new asset to the databsse

Submit a POST request to `http://<ip of docker server>:5000/assets` with JSON data in the following format:

```json
{
	"name":"antarctica",
	"asset_type": "antenna",
	"asset_class": "yagi"
}
```

## Getting all assets

Submit a GET request to `http://<ip of docker server>:5000/assets` and you will receive an object containing all assets

## Getting an asset by name

Submit a GET request to `http://<ip of docker server>:5000/asset/name/<name>` and you will receive that asset. e.g. `http://localhost:5000/asset/name/antarctica`

## Getting an asset by asset_id

Submit a GET request to `http://<ip of docker server>:5000/asset/<asset_id>` and you will receive that asset. e.g. `http://localhost:5000/asset/1`
