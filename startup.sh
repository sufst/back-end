# Pulling Back-End Server. 

QUITE=$1

echo 'Updating Back-End Server...'

if [ $QUITE = '-q' ]
then
    git pull -q
else
   git pull 
fi

source backend-env/bin/activate

python server.py