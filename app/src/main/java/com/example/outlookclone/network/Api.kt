package com.example.outlookclone.network

import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import com.example.outlookclone.BuildConfig
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

object ApiClient {
    private val json = Json { ignoreUnknownKeys = true }

    private val logging = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
    }

    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(logging)
        .build()

    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .client(httpClient)
            .build()
    }

    val service: OutlookService by lazy { retrofit.create(OutlookService::class.java) }
}

interface OutlookService {
    @GET("/messages")
    suspend fun listMessages(): List<ServerMessage>

    @GET("/messages/{id}")
    suspend fun getMessage(@Path("id") id: String): ServerMessage

    @POST("/messages")
    suspend fun sendMessage(@Body req: SendMessageRequest): SendMessageResponse
}

@kotlinx.serialization.Serializable
data class ServerMessage(
    val id: String,
    val sender: String,
    val subject: String,
    val preview: String,
    val body: String,
    val timestampEpochMs: Long
)

@kotlinx.serialization.Serializable
data class SendMessageRequest(
    val to: String,
    val subject: String,
    val body: String
)

@kotlinx.serialization.Serializable
data class SendMessageResponse(val id: String)
