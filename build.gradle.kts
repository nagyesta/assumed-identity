plugins {
    id("java")
    id("io.toolebox.git-versioner") version "1.6.7"
}

group = "com.github.nagyesta"

buildscript {
    fun optionalPropertyString(name: String): String {
        return if (project.hasProperty(name)) {
            project.property(name) as String
        } else {
            ""
        }
    }

    fun dockerAbortGroups(name: String): String {
        return if (project.hasProperty(name)) {
            "all"
        } else {
            ""
        }
    }

    // Define versions in a single place
    extra.apply {
        set("gitToken", optionalPropertyString("githubToken"))
        set("gitUser", optionalPropertyString("githubUser"))
        set("repoUrl", "https://github.com/nagyesta/assumed-identity")
        set("licenseName", "MIT License")
        set("licenseUrl", "https://raw.githubusercontent.com/nagyesta/assumed-identity/main/LICENSE")
        set("maintainerId", "nagyesta")
        set("maintainerName", "Istvan Zoltan Nagy")
        set("maintainerUrl", "https://github.com/nagyesta/")
    }
}

versioner {
    startFrom {
        major = 1
        minor = 0
        patch = 0
    }
    match {
        major = "{major}"
        minor = "{minor}"
        patch = "{patch}"
    }
    pattern {
        pattern = "%M.%m.%p"
    }
    git {
        authentication {
            https {
                token = project.extra.get("gitToken").toString()
            }
        }
    }
    tag {
        prefix = "v"
        useCommitMessage = true
    }
}

versioner.apply()

repositories {
    mavenCentral()
}

dependencies {
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

var createVenv = tasks.register<Exec>("createVenv") {
    group = "python"
    outputs.dir("venv")
    description = "Create virtual environment."
    workingDir = file(".")
    commandLine = listOf("python", "-m", "venv", "./venv")
}

var upgradePip = tasks.register<Exec>("upgradePip") {
    group = "python"
    description = "Updates PIP for the build."
    workingDir = file("src/python")
    commandLine = listOf("../../venv/bin/python", "-m", "pip", "install", "--upgrade", "pip")
    dependsOn(createVenv)
}

var installPytest = tasks.register<Exec>("installPytest") {
    group = "python"
    description = "Install PyTest."
    workingDir = file("src/python")
    commandLine = listOf("../../venv/bin/python", "-m", "pip", "install", "pytest")
    dependsOn(upgradePip)
}

var installITRequirements = tasks.register<Exec>("installITRequirements") {
    group = "python"
    description = "Install Integration Test requirements."
    workingDir = file("src/python")
    commandLine = listOf("../../venv/bin/pip", "install", "-r", "integration-requirements.txt")
    dependsOn(installPytest)
}

var installRequirements = tasks.register<Exec>("installRequirements") {
    group = "python"
    description = "Install requirements."
    workingDir = file("src/python")
    commandLine = listOf("../../venv/bin/pip", "install", "-r", "requirements.txt")
    dependsOn(upgradePip)
}

var pytest = tasks.register<Exec>("pytest") {
    group = "python"
    description = "Run Python tests."
    workingDir = file("src/python")
    commandLine = listOf("../../venv/bin/python", "-m", "pytest", "test.py")
    dependsOn(installPytest)
    dependsOn(installRequirements)
}

var pytestIT = tasks.register<Exec>("pytestIT") {
    group = "python"
    description = "Run Python integration tests."
    workingDir = file("src/python")
    commandLine = listOf("../../venv/bin/python", "-m", "pytest", "integration.py")
    dependsOn(installPytest)
    dependsOn(installITRequirements)
    dependsOn(runDocker)
    finalizedBy(stopDocker)
    doFirst {
        Thread.sleep(1000)
    }
}

var copyDockerfile = tasks.register<Copy>("copyDockerfile") {
    group = "docker"
    description = "Copies the Dockerfile to the Docker build folder."
    inputs.file(file("src/docker/Dockerfile"))
    outputs.file(layout.buildDirectory.file("docker/Dockerfile").get().asFile)
    from(file("src/docker/Dockerfile"))
    into(layout.buildDirectory.dir("docker").get().asFile)
    dependsOn(pytest)
}

var prepareDockerApp = tasks.register<Copy>("prepareDockerApp") {
    group = "docker"
    description = "Copies the Application to the Docker build folder."
    inputs.file(file("src/python/app.py"))
    outputs.file(layout.buildDirectory.file("docker/app.py").get().asFile)
    from(file("src/python/app.py"))
    into(layout.buildDirectory.dir("docker").get().asFile)
    dependsOn(pytest)
}

var prepareDockerRequirements = tasks.register<Copy>("prepareDockerRequirements") {
    group = "docker"
    description = "Copies the requirements file to the Docker build folder."
    inputs.file(file("src/python/requirements.txt"))
    outputs.file(layout.buildDirectory.file("docker/requirements.txt").get().asFile)
    from(file("src/python/requirements.txt"))
    into(layout.buildDirectory.dir("docker").get().asFile)
    dependsOn(pytest)
}

var createDockerBuildx = tasks.register<Exec>("createDockerBuildx") {
    group = "docker"
    description = "Creates a Docker Buildx instance."
    workingDir = layout.buildDirectory.dir("docker").get().asFile
    commandLine = listOf(
        "docker", "buildx",
        "create",
        "--use"
    )
    dependsOn(copyDockerfile)
    dependsOn(prepareDockerApp)
    dependsOn(prepareDockerRequirements)
    dependsOn(pytestIT)
}

var buildDocker = tasks.register<Exec>("buildDocker") {
    group = "docker"
    description = "Builds the Docker image."
    inputs.dir(layout.buildDirectory.dir("docker").get().asFile)
    workingDir = layout.buildDirectory.dir("docker").get().asFile
    commandLine = listOf(
        "docker", "buildx",
        "build",
        "--platform", "linux/arm64,linux/amd64",
        "--pull",
        "-t", "nagyesta/assumed-identity:${project.version}",
        "."
    )
    dependsOn(createDockerBuildx)
}

tasks.register<Exec>("buildDockerPush") {
    group = "docker"
    description = "Builds and pushes the Docker image."
    inputs.dir(layout.buildDirectory.dir("docker").get().asFile)
    workingDir = layout.buildDirectory.dir("docker").get().asFile
    commandLine = listOf(
        "docker", "buildx",
        "build",
        "--platform", "linux/arm64,linux/amd64",
        "--push",
        "-t", "nagyesta/assumed-identity:${project.version}",
        "."
    )
    dependsOn(createDockerBuildx)
}

var buildDockerLocal = tasks.register<Exec>("buildDockerLocal") {
    group = "docker"
    description = "Builds the Docker image for local use."
    inputs.dir(layout.buildDirectory.dir("docker").get().asFile)
    workingDir = layout.buildDirectory.dir("docker").get().asFile
    commandLine = listOf(
        "docker",
        "build",
        "-t", "nagyesta/assumed-identity:${project.version}",
        "."
    )
    dependsOn(copyDockerfile)
    dependsOn(prepareDockerApp)
    dependsOn(prepareDockerRequirements)
}

var runDocker = tasks.register<Exec>("runDocker") {
    group = "Docker"
    description = "Starts a container from the Docker image."
    inputs.dir(layout.buildDirectory.dir("docker"))
    workingDir = layout.buildDirectory.dir("docker").get().asFile

    environment(
        mapOf(
            "ASSUMED_ID_PORT" to "8080",
            "ASSUMED_ID_HOST" to "0.0.0.0",
            "ASSUMED_ID_ISSUER" to "https://sts.windows.net/00000000-0000-0000-0000-000000000001/"
        )
    )
    commandLine = listOf(
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "--name", "assumed-identity",
        "-e", "ASSUMED_ID_PORT",
        "-e", "ASSUMED_ID_HOST",
        "-e", "ASSUMED_ID_ISSUER",
        "-d",
        "-p", "8080:8080",
        "nagyesta/assumed-identity:${rootProject.version}"
    )
    dependsOn(buildDockerLocal)
}

var stopDocker = tasks.register<Exec>("stopDocker") {
    group = "Docker"
    description = "Stops the Docker container."
    inputs.dir(layout.buildDirectory.dir("docker"))
    workingDir = layout.buildDirectory.dir("docker").get().asFile
    commandLine = listOf("docker", "stop", "assumed-identity")
    dependsOn(runDocker)
}
