mkdir -p /data/db 
mongod &

# rm -rf dump* &&  wget http://dev.sefaria.org/static/dump_small.tar.gz 

tar zxvf dump_small.tar.gz
mongorestore --drop
cd sefaria 
mkdir -p /sefaria/log 
python manage.py syncdb
python manage.py runserver 0.0.0.0:8000

