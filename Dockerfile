FROM eclipse-temurin:21-jre

WORKDIR /opt/cbom-lab
COPY java-app/target/java-crypto-fixture-1.0.0.jar app.jar
COPY config/openssl.cnf /etc/ssl/cbom-lab-openssl.cnf
COPY certs/ /opt/cbom-lab/certs/

CMD ["java", "-cp", "app.jar", "lab.CryptoFixture"]
