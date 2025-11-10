package com.aethernexus.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages
import com.aethernexus.api.AetherNexusApiClient

/**
 * Действие для объяснения выделенного кода
 */
class ExplainCodeAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val project = e.getData(CommonDataKeys.PROJECT) ?: return
        
        val selectionModel = editor.selectionModel
        val selectedText = selectionModel.selectedText
        
        if (selectedText.isNullOrBlank()) {
            Messages.showInfoMessage(
                project,
                "Please select code to explain",
                "AetherNexus"
            )
            return
        }
        
        // TODO: Вызвать API для объяснения кода
        val apiClient = AetherNexusApiClient.getInstance(project)
        apiClient.explainCode(selectedText) { explanation ->
            Messages.showInfoMessage(
                project,
                explanation ?: "Explanation not available",
                "Code Explanation"
            )
        }
    }
    
    override fun update(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR)
        e.presentation.isEnabled = editor != null && editor.selectionModel.hasSelection()
    }
}

