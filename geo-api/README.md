### Install awscli
`apt install awscli`

### Configure aws credentials
`aws configure`

### Install serverlessframework
`npm install -g serverless`

### Install serverlessframwork plugins in package.json
`npm install`

### Install virtualenv for python
`pip install virtualenv`

### Create virtualenv
`virtualenv venv --python=python3`

### Install python requirements
`pip install -r requirements.txt`

### Run tests
`python -m pytest tests/`

### Set environment variables in .env file
This project uses a .env file to set needed environment variables for both development 
and deployment. There's a .env.example file in the root of this project (fpx-monorepo/geo-api/.env.example) that you can copy to fpx-monorepo/geo-api/.env and fill in the variables with
their intended value

### Run project in development (-o 0.0.0.0 makes it accessable from other hosts than localhost)
`serverless offline -o 0.0.0.0`

### Deploy
`serverless deploy`

### Invoke function
`serverless invoke -f numpy --log`
