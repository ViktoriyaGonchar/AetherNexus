package com.aethernexus.listeners

import com.intellij.openapi.project.Project
import com.intellij.openapi.project.ProjectManagerListener
import com.aethernexus.settings.AetherNexusSettings

/**
 * Слушатель открытия проекта
 */
class ProjectOpenListener : ProjectManagerListener {
    
    override fun projectOpened(project: Project) {
        val settings = AetherNexusSettings.getInstance()
        
        // TODO: Автоматическая индексация при открытии проекта
        if (settings.enableAutoIndexing) {
            // Запустить индексацию проекта
            println("AetherNexus: Project opened, starting indexing...")
        }
    }
    
    override fun projectClosed(project: Project) {
        // Очистка ресурсов при закрытии проекта
        println("AetherNexus: Project closed")
    }
}

