package com.aethernexus.settings

import com.intellij.openapi.options.Configurable
import com.intellij.openapi.options.ConfigurationException
import com.intellij.openapi.project.ProjectManager
import javax.swing.*

/**
 * Настройки плагина AetherNexus
 */
class AetherNexusConfigurable : Configurable {
    
    private var panel: AetherNexusSettingsPanel? = null
    
    override fun getDisplayName(): String = "AetherNexus"
    
    override fun createComponent(): JComponent? {
        panel = AetherNexusSettingsPanel()
        return panel
    }
    
    override fun isModified(): Boolean {
        val settings = AetherNexusSettings.getInstance()
        return panel?.let { p ->
            p.apiUrl != settings.apiUrl ||
            p.apiKey != settings.apiKey ||
            p.enableAutoIndexing != settings.enableAutoIndexing
        } ?: false
    }
    
    @Throws(ConfigurationException::class)
    override fun apply() {
        panel?.let { p ->
            val settings = AetherNexusSettings.getInstance()
            settings.apiUrl = p.apiUrl
            settings.apiKey = p.apiKey
            settings.enableAutoIndexing = p.enableAutoIndexing
        }
    }
    
    override fun reset() {
        val settings = AetherNexusSettings.getInstance()
        panel?.apiUrl = settings.apiUrl
        panel?.apiKey = settings.apiKey
        panel?.enableAutoIndexing = settings.enableAutoIndexing
    }
}

/**
 * Панель настроек
 */
class AetherNexusSettingsPanel : JPanel() {
    var apiUrl: String = "http://localhost:8000/api/v1"
    var apiKey: String = ""
    var enableAutoIndexing: Boolean = true
    
    init {
        layout = BoxLayout(this, BoxLayout.Y_AXIS)
        border = javax.swing.BorderFactory.createEmptyBorder(10, 10, 10, 10)
        
        // API URL
        val urlLabel = JLabel("Backend API URL:")
        val urlField = JTextField(apiUrl)
        urlField.text = apiUrl
        urlField.addActionListener { apiUrl = urlField.text }
        
        // API Key
        val keyLabel = JLabel("API Key (optional):")
        val keyField = JPasswordField()
        keyField.addActionListener { apiKey = String(keyField.password) }
        
        // Auto indexing
        val autoIndexCheckbox = JCheckBox("Enable auto-indexing", enableAutoIndexing)
        autoIndexCheckbox.addActionListener { enableAutoIndexing = autoIndexCheckbox.isSelected }
        
        add(urlLabel)
        add(urlField)
        add(Box.createVerticalStrut(10))
        add(keyLabel)
        add(keyField)
        add(Box.createVerticalStrut(10))
        add(autoIndexCheckbox)
    }
}

