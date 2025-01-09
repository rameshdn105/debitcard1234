# Step 1: Use an official openjdk as the base image
FROM openjdk:17-jdk-slim

# Step 2: Install wget (optional if you want to download Tomcat dynamically)
RUN apt-get update && apt-get install -y wget

# Step 3: Set environment variables
ENV CATALINA_HOME /opt/tomcat

# Step 4: Download and install Apache Tomcat (if not pre-installed)
RUN wget -q https://downloads.apache.org/tomcat/tomcat-9/v9.0.56/bin/apache-tomcat-9.0.56.tar.gz && \
    tar -xzf apache-tomcat-9.0.56.tar.gz -C /opt && \
    mv /opt/apache-tomcat-9.0.56 /opt/tomcat && \
    rm apache-tomcat-9.0.56.tar.gz

# Step 5: Copy your .war file into the Tomcat webapps folder
COPY target/debitcardapp.war $CATALINA_HOME/webapps/

# Step 6: Expose the port Tomcat listens on
EXPOSE 8080

# Step 7: Start Tomcat server
CMD ["sh", "-c", "$CATALINA_HOME/bin/catalina.sh run"]
