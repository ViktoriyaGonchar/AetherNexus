package com.aethernexus.ui

import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextField
import com.intellij.ui.table.JBTable
import com.intellij.util.ui.JBUI
import java.awt.BorderLayout
import java.awt.Dimension
import javax.swing.*
import javax.swing.table.DefaultTableModel

/**
 * Главная панель AetherNexus в Tool Window
 */
class AetherNexusPanel(project: Project) : JPanel(BorderLayout()) {
    
    private val searchField: JBTextField
    private val resultsTable: JBTable
    private val historyList: JList<String>
    
    init {
        border = JBUI.Borders.empty(10)
        preferredSize = Dimension(400, 600)
        
        // Поисковая панель
        val searchPanel = createSearchPanel()
        add(searchPanel, BorderLayout.NORTH)
        
        // Таблица результатов
        val resultsPanel = createResultsPanel()
        add(resultsPanel, BorderLayout.CENTER)
        
        // Панель истории
        val historyPanel = createHistoryPanel()
        add(historyPanel, BorderLayout.SOUTH)
    }
    
    private fun createSearchPanel(): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.emptyBottom(10)
        
        searchField = JBTextField()
        searchField.emptyText.setText("Search in project...")
        searchField.preferredSize = Dimension(Int.MAX_VALUE, 30)
        
        val searchButton = JButton("Search")
        searchButton.addActionListener {
            performSearch()
        }
        
        panel.add(searchField, BorderLayout.CENTER)
        panel.add(searchButton, BorderLayout.EAST)
        
        return panel
    }
    
    private fun createResultsPanel(): JPanel {
        val panel = JPanel(BorderLayout())
        
        val columnNames = arrayOf("Type", "Title", "Score")
        val data = arrayOf<Array<Any>>()
        val model = DefaultTableModel(data, columnNames)
        
        resultsTable = JBTable(model)
        resultsTable.setShowGrid(true)
        resultsTable.fillsViewportHeight = true
        
        val scrollPane = JBScrollPane(resultsTable)
        panel.add(scrollPane, BorderLayout.CENTER)
        
        return panel
    }
    
    private fun createHistoryPanel(): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.emptyTop(10)
        panel.preferredSize = Dimension(Int.MAX_VALUE, 100)
        
        val label = JLabel("Search History:")
        panel.add(label, BorderLayout.NORTH)
        
        historyList = JList(DefaultListModel<String>())
        val scrollPane = JBScrollPane(historyList)
        panel.add(scrollPane, BorderLayout.CENTER)
        
        return panel
    }
    
    private fun performSearch() {
        val query = searchField.text
        if (query.isBlank()) return
        
        // TODO: Вызвать API клиент для поиска
        println("Searching for: $query")
    }
}

