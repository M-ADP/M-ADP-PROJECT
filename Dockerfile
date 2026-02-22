FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY build.gradle .
COPY settings.gradle .

# Make gradlew executable
RUN chmod +x ./gradlew

# Resolve dependencies (layer caching)
RUN ./gradlew dependencies --no-daemon

# Copy source code
COPY src src

# Build jar
RUN ./gradlew bootJar --no-daemon

# Prepare minimal runtime image
FROM eclipse-temurin:21-jdk-alpine

WORKDIR /app

# Copy the built jar from builder
COPY --from=builder /app/build/libs/*.jar app.jar

ENV TZ=Asia/Seoul
ENV SPRING_PROFILES_ACTIVE=dev

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
