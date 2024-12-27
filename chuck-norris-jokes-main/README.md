# chuck-norris-jokes
Chuck Norris Jokes server

### Endpoints
**GET /joke**</br>
Get a Chuck Norris joke 

**Headers**
|          Name | Required |  Type   | Description                                                                                                                                                           |
| -------------:|:--------:|:-------:| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|     `Authorization` | required | string  | Your account authorization.                                                                     |
**Response**
```
{
    "id": "F6v0fEXeREek9FnF6_9k4A",
    "categories": ["some category"],
    "createdAt": "2020-01-05 13:42:25.352697",
    "joke": "Chuck Norris' first car was Optimus Prime."
}
```

In order to run a requst run one of the following servers(NodeJs\ Python) and you can use this request
```bash
curl --location --request GET 'http://localhost:8000/joke' \
--header 'Authorization: 1111-2222-3333'
```
*******
## JaveScript(NodeJs)
The project is under the `js` folder

#### Installation
`npm i`

#### Run tests
To run the service tests
`npm run test`

#### Run the server
To run the service you can use this command
`npm start`

********
## Python
The project is under the `python` folder.
First create virtualenv and activate it

#### Installation
`pip install -r /path/to/requirements.txt`

#### Run tests
`brew install python`
# Create virtual environment
`python3 -m venv venv`

# Activate it
`source venv/bin/activate`

Install the required packages:
`pip install -r requirements.txt`
`pip install pytest` # Make sure pytest is installed
`pip install fastapi pytest-asyncio httpx`

To run the service tests
`pytest`

#### Run the server
To run the service you can use this command
`uvicorn main:app`