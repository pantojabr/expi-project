# Stealth Dockerfile for API runtime with OpenTelemetry Java Agent
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app

COPY pom.xml .
COPY .mvn .mvn
COPY src src

RUN --mount=type=cache,target=/root/.m2 mvn clean install -DskipTests

FROM eclipse-temurin:21-jre-jammy
WORKDIR /app

ARG OTEL_JAVA_AGENT_VERSION=2.16.0
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /otel \
  && curl -fsSL -o /otel/opentelemetry-javaagent.jar \
      "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_JAVA_AGENT_VERSION}/opentelemetry-javaagent.jar"

COPY --from=build /app/target/despesa-api-mvp-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS:-} -javaagent:/otel/opentelemetry-javaagent.jar -jar /app/app.jar"]
