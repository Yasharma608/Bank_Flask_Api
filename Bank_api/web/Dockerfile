From python:3
/home/yasharma/Yash/2020/June/Udemy_flask/Bank_api/web
COPY requirment.txt ./
RUN pip insatll --no-cache-dir-r requirement.txt
COPY . .
RUN pip install ./en_core_web_sm-2.0.0.tar.gz
CMD["python","app.py"]

