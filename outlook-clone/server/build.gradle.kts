plugins {
    id("org.jetbrains.kotlin.jvm")
    application
    id("org.jetbrains.kotlin.plugin.serialization")
}

group = "com.example"
version = "1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation(project(":shared"))

    implementation("io.ktor:ktor-server-core-jvm:2.3.12")
    implementation("io.ktor:ktor-server-netty-jvm:2.3.12")
    implementation("io.ktor:ktor-server-content-negotiation:2.3.12")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.12")
    implementation("ch.qos.logback:logback-classic:1.5.12")
    testImplementation("io.ktor:ktor-server-tests-jvm:2.3.12")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit:1.9.24")
}

application {
    mainClass.set("com.example.server.ServerKt")
}

kotlin {
    jvmToolchain(17)
}
