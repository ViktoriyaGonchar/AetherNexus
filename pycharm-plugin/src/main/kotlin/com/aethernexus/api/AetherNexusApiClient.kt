package com.aethernexus.api

import com.intellij.openapi.project.Project
import com.google.gson.Gson
import com.google.gson.JsonObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.CompletableFuture

/**
 * API клиент для связи с AetherNexus бэкендом
 */
class AetherNexusApiClient private constructor(private val project: Project) {
    
    private val baseUrl: String
    private val gson = Gson()
    
    init {
        // TODO: Получить URL из настроек
        baseUrl = "http://localhost:8000/api/v1"
    }
    
    companion object {
        private val instances = mutableMapOf<Project, AetherNexusApiClient>()
        
        fun getInstance(project: Project): AetherNexusApiClient {
            return instances.getOrPut(project) {
                AetherNexusApiClient(project)
            }
        }
    }
    
    /**
     * Поиск по тексту
     */
    fun textSearch(query: String, callback: (List<SearchResult>) -> Unit) {
        CompletableFuture.supplyAsync {
            val request = JsonObject().apply {
                addProperty("query", query)
                addProperty("limit", 10)
            }
            
            val response = post("$baseUrl/search/text", request.toString())
            parseSearchResponse(response)
        }.thenAccept(callback)
    }
    
    /**
     * Семантический поиск
     */
    fun semanticSearch(query: String, callback: (List<SearchResult>) -> Unit) {
        CompletableFuture.supplyAsync {
            val request = JsonObject().apply {
                addProperty("query", query)
                addProperty("limit", 10)
            }
            
            val response = post("$baseUrl/search/semantic", request.toString())
            parseSearchResponse(response)
        }.thenAccept(callback)
    }
    
    /**
     * Объяснение кода
     */
    fun explainCode(code: String, callback: (String?) -> Unit) {
        CompletableFuture.supplyAsync {
            val request = JsonObject().apply {
                addProperty("code", code)
                addProperty("language", "python")
            }
            
            val response = post("$baseUrl/context/explain", request.toString())
            val json = gson.fromJson(response, JsonObject::class.java)
            json.get("explanation")?.asString
        }.thenAccept(callback)
    }
    
    /**
     * Поиск связанных сущностей
     */
    fun findRelated(entityId: String, callback: (List<RelatedEntity>) -> Unit) {
        CompletableFuture.supplyAsync {
            val response = get("$baseUrl/context/related/$entityId")
            val json = gson.fromJson(response, JsonObject::class.java)
            val relatedArray = json.getAsJsonArray("related")
            
            relatedArray.map { element ->
                val obj = element.asJsonObject
                RelatedEntity(
                    id = obj.get("id").asString,
                    type = obj.get("type").asString,
                    title = obj.get("title").asString,
                    relationType = obj.get("relation_type").asString,
                    score = obj.get("score").asDouble
                )
            }
        }.thenAccept(callback)
    }
    
    /**
     * Генерация документации
     */
    fun generateDocumentation(code: String, callback: (String?) -> Unit) {
        CompletableFuture.supplyAsync {
            val request = JsonObject().apply {
                addProperty("code", code)
                addProperty("language", "python")
                addProperty("style", "google")
            }
            
            val response = post("$baseUrl/context/generate-docs", request.toString())
            val json = gson.fromJson(response, JsonObject::class.java)
            json.get("docstring")?.asString
        }.thenAccept(callback)
    }
    
    private fun get(urlString: String): String {
        val url = URL(urlString)
        val connection = url.openConnection() as HttpURLConnection
        connection.requestMethod = "GET"
        connection.setRequestProperty("Content-Type", "application/json")
        
        return connection.inputStream.bufferedReader().use { it.readText() }
    }
    
    private fun post(urlString: String, body: String): String {
        val url = URL(urlString)
        val connection = url.openConnection() as HttpURLConnection
        connection.requestMethod = "POST"
        connection.setRequestProperty("Content-Type", "application/json")
        connection.doOutput = true
        
        connection.outputStream.use { output ->
            output.write(body.toByteArray())
        }
        
        return connection.inputStream.bufferedReader().use { it.readText() }
    }
    
    private fun parseSearchResponse(response: String): List<SearchResult> {
        val json = gson.fromJson(response, JsonObject::class.java)
        val resultsArray = json.getAsJsonArray("results")
        
        return resultsArray.map { element ->
            val obj = element.asJsonObject
            SearchResult(
                id = obj.get("id").asString,
                title = obj.get("title").asString,
                content = obj.get("content").asString,
                type = obj.get("type").asString,
                score = obj.get("score").asDouble.toFloat()
            )
        }
    }
}

/**
 * Модель результата поиска
 */
data class SearchResult(
    val id: String,
    val title: String,
    val content: String,
    val type: String,
    val score: Float
)

/**
 * Модель связанной сущности
 */
data class RelatedEntity(
    val id: String,
    val type: String,
    val title: String,
    val relationType: String,
    val score: Double
)

