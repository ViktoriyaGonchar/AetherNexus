package com.aethernexus.settings

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.*

/**
 * Настройки плагина AetherNexus
 */
@State(
    name = "AetherNexusSettings",
    storages = [Storage("aethernexus.xml")]
)
@Service
class AetherNexusSettings : PersistentStateComponent<AetherNexusSettings.State> {
    
    data class State(
        var apiUrl: String = "http://localhost:8000/api/v1",
        var apiKey: String = "",
        var enableAutoIndexing: Boolean = true
    )
    
    private var state = State()
    
    override fun getState(): State = state
    
    override fun loadState(state: State) {
        this.state = state
    }
    
    var apiUrl: String
        get() = state.apiUrl
        set(value) {
            state.apiUrl = value
        }
    
    var apiKey: String
        get() = state.apiKey
        set(value) {
            state.apiKey = value
        }
    
    var enableAutoIndexing: Boolean
        get() = state.enableAutoIndexing
        set(value) {
            state.enableAutoIndexing = value
        }
    
    companion object {
        fun getInstance(): AetherNexusSettings {
            return ApplicationManager.getApplication().getService(AetherNexusSettings::class.java)
        }
    }
}

