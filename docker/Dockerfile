FROM ubuntu:16.04

RUN apt update && apt install -y python-dev python-pip mongodb wget nano git
RUN pip install pymongo
RUN git clone https://github.com/google/re2.git && cd re2 && make install && cd ../src/pyre2 && python setup.py build && python setup.py install
RUN git clone https://github.com/Sefaria/Sefaria-Project.git sefaria && cd sefaria/ && pip install -r requirements.txt . && python manage.py syncdb

RUN wget http://dev.sefaria.org/static/dump_small.tar.gz && mongorestore --drop
ADD database.py /sefaria/sefaria/system/



