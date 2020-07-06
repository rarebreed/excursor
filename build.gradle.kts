import org.jetbrains.kotlin.gradle.tasks.KotlinCompile
import io.quarkus.gradle.tasks.QuarkusDev

group = "app.khadga"
version = "0.1.0-SNAPSHOT"

val quarkusVersion = "1.5.2.FINAL"

plugins {
    java
    id("org.jetbrains.kotlin.jvm") version "1.3.72"
    id("org.jetbrains.kotlin.plugin.allopen") version "1.3.72"
    id("io.quarkus")
}

repositories {
     mavenLocal()
     mavenCentral()
}

dependencies {
    implementation(enforcedPlatform("io.quarkus:quarkus-bom:1.5.2.Final"))
    implementation("io.quarkus:quarkus-smallrye-graphql")
    implementation("io.quarkus:quarkus-logging-json")
    implementation("io.quarkus:quarkus-jackson")
    implementation("io.quarkus:quarkus-kotlin")
    implementation("io.quarkus:quarkus-config-yaml")
    implementation("io.quarkus:quarkus-vertx-web")
    implementation("io.quarkus:quarkus-vertx")
    implementation("io.quarkus:quarkus-mutiny")
    implementation("io.quarkus:quarkus-resteasy")
    implementation("io.smallrye.reactive:smallrye-mutiny-vertx-web-client")
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")

    testImplementation("io.quarkus:quarkus-junit5")
    testImplementation("io.rest-assured:kotlin-extensions")
}

quarkus {
    setOutputDirectory("$projectDir/build/classes/kotlin/main")
}

val quarkusDev: QuarkusDev by tasks
quarkusDev.setSourceDir("$projectDir/src/main/kotlin")

allOpen {
    annotation("javax.ws.rs.Path")
    annotation("javax.enterprise.context.ApplicationScoped")
    annotation("io.quarkus.test.junit.QuarkusTest")
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

val compileKotlin: KotlinCompile by tasks
compileKotlin.kotlinOptions {
    jvmTarget = "1.8"
}

val compileTestKotlin: KotlinCompile by tasks
compileTestKotlin.kotlinOptions {
    jvmTarget = "1.8"
}
