package com.aethernexus.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages
import com.aethernexus.api.AetherNexusApiClient

/**
 * Действие для поиска связанных тикетов, PR и документации
 */
class FindRelatedAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.getData(CommonDataKeys.PROJECT) ?: return
        val file = e.getData(CommonDataKeys.PSI_FILE) ?: return
        
        // TODO: Получить entity_id текущего файла/метода
        val entityId = file.virtualFile.path
        
        val apiClient = AetherNexusApiClient.getInstance(project)
        apiClient.findRelated(entityId) { related ->
            if (related.isEmpty()) {
                Messages.showInfoMessage(
                    project,
                    "No related entities found",
                    "AetherNexus"
                )
            } else {
                val message = related.joinToString("\n") { 
                    "${it.type}: ${it.title}"
                }
                Messages.showInfoMessage(
                    project,
                    "Related entities:\n$message",
                    "Related Entities"
                )
            }
        }
    }
}

