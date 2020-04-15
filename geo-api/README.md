### Install awscli
apt install awscli

### Configure aws credentials
aws configure

### Install serverlessframework
npm install -g serverless

### Install serverlessframwork plugins in package.json
npm install

### Install virtualenv for python
pip install virtualenv

### Create virtualenv
virtualenv venv --python=python3

### Install python requirements
pip install -r requirements.txt

### Run tests
python -m pytest tests/

### Deploy
serverless deploy

### Invoke function
serverless invoke -f numpy --log
