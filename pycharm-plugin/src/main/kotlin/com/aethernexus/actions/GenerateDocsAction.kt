package com.aethernexus.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.Messages
import com.aethernexus.api.AetherNexusApiClient

/**
 * Действие для генерации документации
 */
class GenerateDocsAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val project = e.getData(CommonDataKeys.PROJECT) ?: return
        
        val selectionModel = editor.selectionModel
        val selectedText = selectionModel.selectedText
        
        if (selectedText.isNullOrBlank()) {
            Messages.showInfoMessage(
                project,
                "Please select code to generate documentation for",
                "AetherNexus"
            )
            return
        }
        
        val apiClient = AetherNexusApiClient.getInstance(project)
        apiClient.generateDocumentation(selectedText) { docstring ->
            if (docstring != null) {
                // TODO: Вставить docstring в код
                Messages.showInfoMessage(
                    project,
                    "Documentation generated:\n$docstring",
                    "Generated Documentation"
                )
            }
        }
    }
    
    override fun update(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR)
        e.presentation.isEnabled = editor != null && editor.selectionModel.hasSelection()
    }
}

