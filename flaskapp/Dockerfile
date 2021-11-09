FROM python:3.8
LABEL maintainer="unknown "

WORKDIR /flaskapp

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

# initiates the flaskapp
COPY main.py /flaskapp/
RUN chmod a+x main.py

# include the hotel api
COPY hotelapi.py /flaskapp/
RUN chmod a+x hotelapi.py

# Include NS_API.py:
COPY NS_API.py /flaskapp/
COPY afkortingennsstations.txt /flaskapp/
RUN chmod a+x NS_API.py

# Include skyscannerAPI.py
COPY skyscannerAPI.py /flaskapp/
RUN chmod a+x skyscannerAPI.py

# Include sqlconnection.py 
COPY sqlconnection.py /flaskapp/
RUN chmod a+x sqlconnection.py

# Inlcude json_to_html
COPY json_to_html.py /flaskapp/
RUN chmod a+x json_to_html.py 

CMD [ "python", "-u", "main.py" ]