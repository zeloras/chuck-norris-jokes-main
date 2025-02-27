# chuck-norris-jokes
Chuck Norris Jokes server
A service that provides Chuck Norris jokes with rate limiting based on subscription plans:

### Rate Limiting Plans
- **Free Plan**
  - 1 request per second
  - 50 requests per day limit
- **Pro Plan**
  - 10 requests per second
  - 12,000 requests per day limit
- **Enterprise Plan**
  - 100 requests per second
  - Unlimited daily requests

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

### Configuration
Create an `accounts.json` file in the root directory with your user tokens and plans:
```json
{
    "1111-2222-3333": {
        "plan": "PRO"
    }
}
```
Available plans: `FREE`, `PRO`, `ENTERPRISE`
In order to run a requst you can use this request
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

### Environment Variables
The following environment variables are used by the Python service:

| Variable | Description | Default |
|----------|-------------|---------|
| REDIS_HOST | Redis server hostname | redis |
| REDIS_PORT | Redis server port | 6379 |
| REDIS_DB | Redis database number | 0 |
| ACCOUNTS_FILE | Path to the accounts.json file | /accounts.json |

These environment variables can be configured in the docker-compose.yml file or set directly in your environment when running the service outside of Docker.

### Running with Docker
```bash
# Build and start the services
docker-compose up --build
```

### Running Tests
```bash
# Run all tests
docker-compose exec api pytest
```

### Project Structure
```
python/
├── rate_limit/           # Rate limiting implementation
│   ├── limits.py        # Rate limiter logic
│   └── plans.py         # Subscription plans definition
├── tests/               # Test files
├── auth.py             # Authentication middleware
├── joke.py             # Joke model
├── main.py             # FastAPI application
└── requirements.txt    # Project dependencies
```
