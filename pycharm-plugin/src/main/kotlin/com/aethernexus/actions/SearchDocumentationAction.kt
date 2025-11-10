package com.aethernexus.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages
import com.aethernexus.api.AetherNexusApiClient

/**
 * Действие для поиска документации
 */
class SearchDocumentationAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.getData(CommonDataKeys.PROJECT) ?: return
        val file = e.getData(CommonDataKeys.PSI_FILE) ?: return
        
        // TODO: Открыть диалог поиска документации
        val apiClient = AetherNexusApiClient.getInstance(project)
        
        Messages.showInfoMessage(
            project,
            "Documentation search feature coming soon",
            "AetherNexus"
        )
    }
}

