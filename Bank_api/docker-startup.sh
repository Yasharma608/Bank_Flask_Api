
#!/bin/bash
gunicorn -b 0.0.0.0:8003 server:application -w 4 -t 0 
#curl --location --request GET 'localhost:8000/apis/db_setup'
#curl --location --request POST 'localhost:8000/apis/update_tnc_keyword' --form 'file=@"/app/keyword"'
