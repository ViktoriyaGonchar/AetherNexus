plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.20"
    id("org.jetbrains.intellij") version "1.16.0"
}

group = "com.aethernexus"
version = "1.0.0-SNAPSHOT"

repositories {
    mavenCentral()
}

// Настройка IntelliJ Platform
intellij {
    version.set("2023.1")
    type.set("PC") // PyCharm Community
    plugins.set(listOf("python"))
    
    // Для PyCharm Professional используйте:
    // type.set("PY") // PyCharm Professional
}

dependencies {
    // Kotlin стандартная библиотека
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.9.20")
    
    // Kotlin Coroutines для асинхронных операций
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-swing:1.7.3")
    
    // HTTP клиент для API запросов
    implementation("org.apache.httpcomponents.client5:httpclient5:5.2.1")
    
    // JSON обработка
    implementation("com.google.code.gson:gson:2.10.1")
    // Или используйте kotlinx.serialization:
    // implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    
    // WebSocket клиент (опционально, для real-time уведомлений)
    implementation("org.java-websocket:Java-WebSocket:1.5.4")
    
    // Логирование
    implementation("org.slf4j:slf4j-api:2.0.9")
    implementation("ch.qos.logback:logback-classic:1.4.11")
    
    // Тестирование
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit:1.9.20")
    testImplementation("org.mockito:mockito-core:5.6.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
}

tasks {
    // Настройка компиляции Kotlin
    compileKotlin {
        kotlinOptions {
            jvmTarget = "17"
            apiVersion = "1.9"
            languageVersion = "1.9"
        }
    }
    
    compileTestKotlin {
        kotlinOptions {
            jvmTarget = "17"
        }
    }
    
    // Настройка Java компиляции
    compileJava {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }
    
    // Задача для запуска плагина в sandbox
    runIde {
        // JVM аргументы для отладки
        jvmArgs = listOf("-Xmx2048m", "-Xms512m")
    }
    
    // Задача для сборки плагина
    buildSearchableOptions {
        enabled = false
    }
    
    // Задача для публикации (настроить позже)
    publishPlugin {
        token.set(System.getenv("PUBLISH_TOKEN"))
        channels.set(listOf("alpha"))
    }
    
    // Задача для проверки совместимости
    patchPluginXml {
        version.set(project.version.toString())
        sinceBuild.set("231")
        untilBuild.set("241.*")
        
        pluginDescription.set("""
            AetherNexus — Интеллектуальная Ткань Знаний для PyCharm.
            Превращает IDE в центральный узел для доступа ко всей информации проекта.
            """.trimIndent())
        
        changeNotes.set("""
            <h3>1.0.0-SNAPSHOT</h3>
            <ul>
                <li>Начальная версия плагина</li>
                <li>Базовая интеграция с бэкендом</li>
                <li>Текстовый и семантический поиск</li>
            </ul>
            """.trimIndent())
    }
}

// Настройка для разных версий IDE (опционально)
tasks.register("runIde2023.1") {
    group = "intellij"
    doLast {
        intellij {
            version.set("2023.1")
        }
        tasks.runIde.get().exec()
    }
}

tasks.register("runIde2023.2") {
    group = "intellij"
    doLast {
        intellij {
            version.set("2023.2")
        }
        tasks.runIde.get().exec()
    }
}

tasks.register("runIde2023.3") {
    group = "intellij"
    doLast {
        intellij {
            version.set("2023.3")
        }
        tasks.runIde.get().exec()
    }
}

