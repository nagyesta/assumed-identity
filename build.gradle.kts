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

tasks.register<Exec>("buildDockerLocal") {
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
