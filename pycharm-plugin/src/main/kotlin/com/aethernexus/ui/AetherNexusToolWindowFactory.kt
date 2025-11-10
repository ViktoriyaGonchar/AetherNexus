package com.aethernexus.ui

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory

/**
 * Factory для создания Tool Window AetherNexus
 */
class AetherNexusToolWindowFactory : ToolWindowFactory {
    
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val panel = AetherNexusPanel(project)
        val content = ContentFactory.SERVICE.getInstance().createContent(panel, "", false)
        toolWindow.contentManager.addContent(content)
    }
}

