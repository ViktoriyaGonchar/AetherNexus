package com.aethernexus.actions

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.wm.ToolWindowManager

/**
 * Действие для показа Tool Window AetherNexus
 */
class ShowToolWindowAction : AnAction() {
    
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.getData(CommonDataKeys.PROJECT) ?: return
        val toolWindow = ToolWindowManager.getInstance(project)
            .getToolWindow("AetherNexus") ?: return
        
        toolWindow.show()
    }
}

