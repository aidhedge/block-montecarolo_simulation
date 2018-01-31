# block-montecarlo_simulation
FROM python:3
EXPOSE 7002
ENV FLASK_DEBUG=1
ENV PORT=7002
RUN pip install flask
RUN pip install cerberus
RUN pip install numpy
RUN pip install python-dateutil
RUN pip install requests