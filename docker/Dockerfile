FROM ubuntu:16.04

RUN apt update && apt install -y python-dev python-pip mongodb wget nano git
RUN pip install pymongo
RUN git clone https://github.com/google/re2.git && cd re2 && make install 
RUN git clone https://github.com/axiak/pyre2.git && cd pyre2 && python setup.py build && python setup.py install
RUN git clone https://github.com/Sefaria/Sefaria-Project.git sefaria && cd sefaria/ && pip install -r requirements.txt 
RUN wget http://dev.sefaria.org/static/dump_small.tar.gz 
ADD database.py /sefaria/sefaria/system/
ADD local_settings.py /sefaria/sefaria/local_settings.py
ADD start.sh /
EXPOSE 8000 27017 22
CMD ["/bin/sh", "-c", "/start.sh"]




